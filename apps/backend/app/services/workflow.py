"""
审批流程引擎服务

@description 工作流引擎的核心业务逻辑

@features
- 流程启动和流转
- 节点类型处理
- 条件判断
- 并行处理
- 审批操作（通过、拒绝、退回、转办、加签）
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.workflow import (
    WorkflowDefinition,
    WorkflowNode,
    WorkflowEdge,
    WorkflowInstance,
    WorkflowTask,
    WorkflowApproval,
)
from app.models.user import User
from app.schemas.workflow import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionUpdate,
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
    WorkflowProgressResponse,
    WorkflowProgressNode,
)


class WorkflowEngineService:
    """
    工作流引擎服务类

    处理流程的启动、流转和审批操作
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_workflow(
        self, workflow_id: int, data: WorkflowInstanceCreate, initiator_id: int
    ) -> WorkflowInstanceResponse:
        """
        启动流程实例

        Args:
            workflow_id: 流程定义ID
            data: 流程实例数据
            initiator_id: 发起人ID

        Returns:
            WorkflowInstanceResponse: 创建的流程实例

        Raises:
            NotFoundError: 流程定义不存在或未启用
        """
        # 获取流程定义
        result = await self.db.execute(
            select(WorkflowDefinition)
            .where(
                WorkflowDefinition.id == workflow_id,
                WorkflowDefinition.is_active == True,
                WorkflowDefinition.is_deleted == False,
            )
            .options(selectinload(WorkflowDefinition.nodes))
        )
        definition = result.scalar_one_or_none()

        if not definition:
            raise NotFoundError("流程定义不存在或未启用")

        # 生成实例编号
        instance_no = f"WF-{datetime.now().strftime('%Y%m%d%H%M%S')}-{initiator_id}"

        # 创建流程实例
        instance = WorkflowInstance(
            workflow_id=workflow_id,
            instance_no=instance_no,
            title=data.title,
            business_key=data.business_key,
            form_data=data.form_data,
            initiator_id=initiator_id,
            status="running",
        )

        self.db.add(instance)
        await self.db.flush()

        # 查找开始节点
        start_node = next((n for n in definition.nodes if n.node_type == "start"), None)
        if not start_node:
            raise BadRequestError("流程定义缺少开始节点")

        # 流转到开始节点
        await self._flow_to_node(instance, start_node.node_key)

        await self.db.commit()
        await self.db.refresh(instance)

        return await self.get_instance(instance.id)

    async def approve_task(
        self, task_id: int, approver_id: int, comment: Optional[str] = None
    ) -> None:
        """
        审批通过

        Args:
            task_id: 任务ID
            approver_id: 审批人ID
            comment: 审批意见

        Raises:
            NotFoundError: 任务不存在
            BadRequestError: 任务状态不允许该操作
        """
        result = await self.db.execute(
            select(WorkflowTask)
            .where(WorkflowTask.id == task_id)
            .options(selectinload(WorkflowTask.instance))
        )
        task = result.scalar_one_or_none()

        if not task:
            raise NotFoundError("任务不存在")

        if task.status != "pending":
            raise BadRequestError(f"任务状态为{task.status}，无法审批")

        instance = task.instance

        # 记录审批
        approval = WorkflowApproval(
            task_id=task_id,
            instance_id=instance.id,
            approver_id=approver_id,
            action="approve",
            comment=comment,
        )
        self.db.add(approval)

        # 更新任务状态
        task.status = "approved"
        task.completed_at = datetime.now(timezone.utc)

        # 检查是否是并行任务
        if task.parallel_source_node:
            # 检查是否所有并行任务都已完成
            all_complete = await self._check_parallel_tasks_complete(instance, task.parallel_source_node)

            if all_complete:
                # 所有并行任务完成，清除并行状态并流转
                instance.parallel_node_key = None
                instance.parallel_targets = None
                # 流转到并行节点后的下一节点
                await self._proceed_after_parallel(instance, task.parallel_source_node)
        else:
            # 非并行任务，直接流转到下一节点
            await self._proceed_next_task(instance, task.node_key)

        await self.db.commit()

    async def _check_parallel_tasks_complete(self, instance: WorkflowInstance, parallel_source: str) -> bool:
        """
        检查并行任务是否全部完成

        Args:
            instance: 流程实例
            parallel_source: 并行源节点

        Returns:
            bool: 是否所有并行任务都完成
        """
        # 获取该并行组的所有待办任务
        result = await self.db.execute(
            select(WorkflowTask).where(
                WorkflowTask.instance_id == instance.id,
                WorkflowTask.parallel_source_node == parallel_source,
                WorkflowTask.status == "pending",
            )
        )
        pending_tasks = result.scalars().all()

        # 如果没有待办任务，说明所有并行任务都已完成
        return len(pending_tasks) == 0

    async def _proceed_after_parallel(self, instance: WorkflowInstance, parallel_source: str) -> None:
        """
        并行任务全部完成后的流转处理

        查找所有并行节点的后续边，找到汇聚点并流转。

        Args:
            instance: 流程实例
            parallel_source: 并行源节点
        """
        # 获取所有并行目标节点
        parallel_targets = instance.parallel_targets or []

        if not parallel_targets:
            # 没有并行目标记录，查找并行节点的输出边
            result = await self.db.execute(
                select(WorkflowEdge).where(
                    WorkflowEdge.workflow_id == instance.workflow_id,
                    WorkflowEdge.source_node == parallel_source,
                )
            )
            edges = result.scalars().all()
            parallel_targets = [e.target_node for e in edges]

        if not parallel_targets:
            # 没有并行目标，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)
            return

        # 查找所有并行目标节点的输出边
        all_next_nodes = set()
        for target_node_key in parallel_targets:
            result = await self.db.execute(
                select(WorkflowEdge).where(
                    WorkflowEdge.workflow_id == instance.workflow_id,
                    WorkflowEdge.source_node == target_node_key,
                )
            )
            edges = result.scalars().all()
            for edge in edges:
                all_next_nodes.add(edge.target_node)

        if not all_next_nodes:
            # 并行任务后没有后续节点，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)
            return

        # 如果所有并行任务都指向同一个节点，直接流转
        if len(all_next_nodes) == 1:
            next_node = list(all_next_nodes)[0]
            await self._flow_to_node(instance, next_node)
        else:
            # 多个不同的后续节点，取第一个（简化处理）
            # TODO: 实现更复杂的汇聚逻辑
            next_node = list(all_next_nodes)[0]
            await self._flow_to_node(instance, next_node)

    async def reject_task(
        self, task_id: int, approver_id: int, comment: str
    ) -> None:
        """
        审批拒绝

        Args:
            task_id: 任务ID
            approver_id: 审批人ID
            comment: 拒绝原因

        Raises:
            NotFoundError: 任务不存在
            BadRequestError: 任务状态不允许该操作
        """
        result = await self.db.execute(
            select(WorkflowTask)
            .where(WorkflowTask.id == task_id)
            .options(selectinload(WorkflowTask.instance))
        )
        task = result.scalar_one_or_none()

        if not task:
            raise NotFoundError("任务不存在")

        if task.status != "pending":
            raise BadRequestError(f"任务状态为{task.status}，无法审批")

        instance = task.instance

        # 记录审批
        approval = WorkflowApproval(
            task_id=task_id,
            instance_id=instance.id,
            approver_id=approver_id,
            action="reject",
            comment=comment,
        )
        self.db.add(approval)

        # 更新任务状态
        task.status = "rejected"
        task.completed_at = datetime.now(timezone.utc)

        # 拒绝后整个流程结束
        instance.status = "rejected"
        instance.completed_at = datetime.now(timezone.utc)

        await self.db.commit()

    async def return_task(
        self, task_id: int, approver_id: int, comment: str, return_to_node: Optional[str] = None
    ) -> None:
        """
        退回任务

        Args:
            task_id: 任务ID
            approver_id: 审批人ID
            comment: 退回原因
            return_to_node: 退回到指定节点（可选）

        Raises:
            NotFoundError: 任务不存在
            BadRequestError: 任务状态不允许该操作
        """
        # 获取任务和实例信息
        result = await self.db.execute(
            select(WorkflowTask)
            .options(selectinload(WorkflowTask.instance))
            .where(WorkflowTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise NotFoundError("任务不存在")

        if task.status != "pending":
            raise BadRequestError(f"任务状态为{task.status}，无法退回")

        instance = task.instance
        current_node_key = task.node_key

        # 更新原任务状态
        task.status = "returned"
        task.completed_at = datetime.now(timezone.utc)

        # 记录退回操作
        approval = WorkflowApproval(
            task_id=task_id,
            instance_id=instance.id,
            approver_id=approver_id,
            action="return",
            comment=comment,
        )
        self.db.add(approval)

        # 确定退回的目标节点
        target_node_key = return_to_node

        if not target_node_key:
            # 如果未指定，则查找上一节点（通过边反向查找）
            edges_result = await self.db.execute(
                select(WorkflowEdge).where(
                    WorkflowEdge.workflow_id == instance.workflow_id,
                    WorkflowEdge.target_node == current_node_key,
                )
            )
            incoming_edges = edges_result.scalars().all()

            if not incoming_edges:
                raise BadRequestError("当前节点没有前置节点，无法退回")

            # 取第一条进入边作为退回目标
            target_node_key = incoming_edges[0].source_node

        # 验证目标节点存在
        node_result = await self.db.execute(
            select(WorkflowNode).where(
                WorkflowNode.workflow_id == instance.workflow_id,
                WorkflowNode.node_key == target_node_key,
            )
        )
        target_node = node_result.scalar_one_or_none()

        if not target_node:
            raise BadRequestError(f"目标节点 {target_node_key} 不存在")

        # 如果目标节点是开始节点，不允许退回
        if target_node.node_type == "start":
            raise BadRequestError("不允许退回到开始节点")

        # 取消目标节点当前的所有待办任务
        cancel_result = await self.db.execute(
            select(WorkflowTask).where(
                WorkflowTask.instance_id == instance.id,
                WorkflowTask.node_key == target_node_key,
                WorkflowTask.status == "pending",
            )
        )
        tasks_to_cancel = cancel_result.scalars().all()
        for t in tasks_to_cancel:
            t.status = "cancelled"
            t.updated_at = datetime.now(timezone.utc)

        # 在目标节点创建新的待办任务
        await self._create_approval_task(instance, target_node)

        # 更新实例当前节点
        instance.current_node = target_node_key

        await self.db.commit()

    async def get_instance(self, instance_id: int) -> WorkflowInstanceResponse:
        """
        获取流程实例详情

        Args:
            instance_id: 实例ID

        Returns:
            WorkflowInstanceResponse: 流程实例详情

        Raises:
            NotFoundError: 流程实例不存在
        """
        result = await self.db.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()

        if not instance:
            raise NotFoundError("流程实例不存在")

        return WorkflowInstanceResponse.model_validate(instance)

    async def get_pending_tasks(self, user_id: int) -> List[Any]:
        """
        获取用户的待办任务

        Args:
            user_id: 用户ID

        Returns:
            List: 待办任务列表
        """
        result = await self.db.execute(
            select(WorkflowTask, WorkflowInstance)
            .join(WorkflowInstance, WorkflowTask.instance_id == WorkflowInstance.id)
            .where(
                WorkflowTask.assignee_id == user_id,
                WorkflowTask.status == "pending",
            )
            .order_by(WorkflowTask.created_at.desc())
        )

        tasks = []
        for task, instance in result.all():
            tasks.append({
                "id": task.id,
                "instance_id": instance.id,
                "instance_title": instance.title,
                "node_name": task.node_name,
                "status": task.status,
                "created_at": task.created_at,
                "due_date": task.due_date,
            })

        return tasks

    async def get_workflow_progress(self, instance_id: int) -> WorkflowProgressResponse:
        """
        获取流程进度

        Args:
            instance_id: 实例ID

        Returns:
            WorkflowProgressResponse: 流程进度信息

        Raises:
            NotFoundError: 流程实例不存在
        """
        # 获取流程实例
        instance_result = await self.db.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == instance_id)
        )
        instance = instance_result.scalar_one_or_none()

        if not instance:
            raise NotFoundError("流程实例不存在")

        # 获取所有任务
        tasks_result = await self.db.execute(
            select(WorkflowTask)
            .where(WorkflowTask.instance_id == instance_id)
            .order_by(WorkflowTask.created_at)
        )
        tasks = tasks_result.scalars().all()

        # 获取所有审批记录
        approvals_result = await self.db.execute(
            select(WorkflowApproval, User)
            .join(User, WorkflowApproval.approver_id == User.id)
            .where(WorkflowApproval.instance_id == instance_id)
            .order_by(WorkflowApproval.created_at)
        )

        approvals = []
        for approval, user in approvals_result.all():
            approvals.append(
                {
                    "id": approval.id,
                    "task_id": approval.task_id,
                    "instance_id": approval.instance_id,
                    "approver_id": approval.approver_id,
                    "approver_name": user.full_name or user.username,
                    "action": approval.action,
                    "comment": approval.comment,
                    "attachments": approval.attachments,
                    "created_at": approval.created_at,
                }
            )

        # 构建节点进度
        nodes = []
        for task in tasks:
            nodes.append(
                {
                    "node_key": task.node_key,
                    "node_name": task.node_name,
                    "node_type": "approval",
                    "status": task.status,
                    "assignee_id": task.assignee_id,
                    "created_at": task.created_at,
                    "completed_at": task.completed_at,
                }
            )

        return {
            "instance_id": instance.id,
            "instance_no": instance.instance_no,
            "title": instance.title,
            "status": instance.status,
            "current_node": instance.current_node,
            "nodes": nodes,
            "approvals": approvals,
        }

    async def _flow_to_node(self, instance: WorkflowInstance, node_key: str) -> None:
        """
        流转到指定节点

        Args:
            instance: 流程实例
            node_key: 目标节点标识
        """
        # 获取节点信息
        result = await self.db.execute(
            select(WorkflowNode).where(
                WorkflowNode.workflow_id == instance.workflow_id,
                WorkflowNode.node_key == node_key,
            )
        )
        node = result.scalar_one_or_none()

        if not node:
            raise BadRequestError(f"节点 {node_key} 不存在")

        # 更新当前节点
        instance.current_node = node_key

        # 根据节点类型处理
        if node.node_type == "start":
            # 开始节点，直接流转到下一节点
            await self._proceed_next_task(instance, node_key)
        elif node.node_type == "end":
            # 结束节点
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)
        elif node.node_type == "approval":
            # 审批节点，创建任务
            await self._create_approval_task(instance, node)
        elif node.node_type == "condition":
            # 条件节点，判断条件后流转
            await self._handle_condition_node(instance, node)
        elif node.node_type == "parallel":
            # 并行节点，创建多个任务
            await self._handle_parallel_node(instance, node)

    async def _proceed_next_task(self, instance: WorkflowInstance, current_node_key: str) -> None:
        """
        流转到下一个任务

        Args:
            instance: 流程实例
            current_node_key: 当前节点标识
        """
        # 获取从当前节点出发的所有连线
        result = await self.db.execute(
            select(WorkflowEdge).where(
                WorkflowEdge.workflow_id == instance.workflow_id,
                WorkflowEdge.source_node == current_node_key,
            )
        )
        edges = result.scalars().all()

        if not edges:
            # 没有后续连线，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)
            return

        # 评估每条连线的条件，找到第一个满足条件的
        selected_edge = None
        form_data = instance.form_data or {}

        for edge in edges:
            edge_condition = edge.condition

            # 如果没有条件或条件为空，这是默认路径
            if not edge_condition:
                selected_edge = edge
                break

            # 检查是否是默认路径（condition中有default=true）
            if isinstance(edge_condition, dict) and edge_condition.get("default") is True:
                # 记录默认边，但继续检查其他条件
                if selected_edge is None:
                    selected_edge = edge
                continue

            # 评估条件
            if await self._evaluate_condition(edge_condition, form_data):
                selected_edge = edge
                break

        # 如果找到满足条件的边，流转到目标节点
        if selected_edge:
            await self._flow_to_node(instance, selected_edge.target_node)
        else:
            # 没有条件满足，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)

    async def _evaluate_condition(self, condition: dict, form_data: dict) -> bool:
        """
        评估流转条件

        Args:
            condition: 条件配置
            form_data: 表单数据

        Returns:
            bool: 条件是否满足

        条件格式:
        {
            "field": "amount",      # 字段名
            "operator": ">",        # 运算符: >, >=, <, <=, ==, !=, in, not_in, contains, empty
            "value": 10000,         # 比较值
            "default": false        # 是否为默认路径
        }
        """
        if not condition:
            return True

        field = condition.get("field")
        operator = condition.get("operator", "==")
        expected_value = condition.get("value")

        # 获取字段值（支持嵌套路径，如 "user.department"）
        actual_value = form_data
        if field:
            for key in field.split("."):
                if isinstance(actual_value, dict):
                    actual_value = actual_value.get(key)
                else:
                    actual_value = None
                    break

        # 根据运算符比较
        try:
            if operator == "==":
                return actual_value == expected_value
            elif operator == "!=":
                return actual_value != expected_value
            elif operator == ">":
                return self._safe_compare(actual_value, expected_value, lambda a, b: a > b)
            elif operator == ">=":
                return self._safe_compare(actual_value, expected_value, lambda a, b: a >= b)
            elif operator == "<":
                return self._safe_compare(actual_value, expected_value, lambda a, b: a < b)
            elif operator == "<=":
                return self._safe_compare(actual_value, expected_value, lambda a, b: a <= b)
            elif operator == "in":
                return actual_value in expected_value if isinstance(expected_value, list) else False
            elif operator == "not_in":
                return actual_value not in expected_value if isinstance(expected_value, list) else False
            elif operator == "contains":
                return str(expected_value) in str(actual_value) if actual_value else False
            elif operator == "empty":
                return actual_value is None or actual_value == "" or actual_value == []
            else:
                # 未知运算符，默认不满足
                return False
        except (TypeError, ValueError):
            # 比较失败，返回 False
            return False

    def _safe_compare(self, actual, expected, compare_func) -> bool:
        """
        安全的比较函数

        Args:
            actual: 实际值
            expected: 期望值
            compare_func: 比较函数

        Returns:
            bool: 比较结果
        """
        try:
            # 尝试转换为数字进行比较
            if actual is None or expected is None:
                return False
            return compare_func(float(actual), float(expected))
        except (TypeError, ValueError):
            # 转换失败，尝试字符串比较
            try:
                return compare_func(str(actual), str(expected))
            except:
                return False

    async def _create_approval_task(
        self, instance: WorkflowInstance, node: WorkflowNode, parallel_source: Optional[str] = None
    ) -> None:
        """
        创建审批任务

        Args:
            instance: 流程实例
            node: 节点信息
            parallel_source: 并行源节点（可选）
        """
        # 从节点配置中获取审批人
        config = node.config or {}
        assignee_id = config.get("assignee_id")

        if not assignee_id:
            raise BadRequestError(f"节点 {node.node_key} 未配置审批人")

        # 验证审批人是否存在
        user_result = await self.db.execute(select(User).where(User.id == assignee_id))
        assignee = user_result.scalar_one_or_none()
        if not assignee:
            raise BadRequestError(f"节点 {node.node_key} 的审批人（ID: {assignee_id}）不存在")

        # 计算到期时间（默认3天）
        due_date = datetime.now(timezone.utc) + timedelta(days=config.get("due_days", 3))

        task = WorkflowTask(
            instance_id=instance.id,
            node_key=node.node_key,
            node_name=node.name,
            assignee_id=assignee_id,
            status="pending",
            due_date=due_date,
            parallel_source_node=parallel_source,
        )

        self.db.add(task)

    async def _handle_condition_node(self, instance: WorkflowInstance, node: WorkflowNode) -> None:
        """
        处理条件节点

        条件节点会根据配置的条件表达式，评估表单数据并选择合适的输出路径。

        Args:
            instance: 流程实例
            node: 条件节点
        """
        # 获取从条件节点出发的所有连线
        result = await self.db.execute(
            select(WorkflowEdge).where(
                WorkflowEdge.workflow_id == instance.workflow_id,
                WorkflowEdge.source_node == node.node_key,
            )
        )
        edges = result.scalars().all()

        if not edges:
            # 条件节点没有输出连线，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)
            return

        # 评估每条连线的条件，找到第一个满足条件的
        selected_edge = None
        form_data = instance.form_data or {}

        # 获取节点配置中可能有的条件表达式
        node_config = node.config or {}

        for edge in edges:
            edge_condition = edge.condition

            # 如果没有条件或条件为空，这是默认路径
            if not edge_condition:
                selected_edge = edge
                break

            # 检查是否是默认路径
            if isinstance(edge_condition, dict) and edge_condition.get("default") is True:
                if selected_edge is None:
                    selected_edge = edge
                continue

            # 评估条件
            if await self._evaluate_condition(edge_condition, form_data):
                selected_edge = edge
                break

        # 流转到选中的目标节点
        if selected_edge:
            await self._flow_to_node(instance, selected_edge.target_node)
        else:
            # 没有条件满足，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)

    async def _handle_parallel_node(self, instance: WorkflowInstance, node: WorkflowNode) -> None:
        """
        处理并行节点

        并行节点会同时创建多个任务，所有任务完成后才继续流转。

        Args:
            instance: 流程实例
            node: 并行节点
        """
        # 获取从并行节点出发的所有连线
        result = await self.db.execute(
            select(WorkflowEdge).where(
                WorkflowEdge.workflow_id == instance.workflow_id,
                WorkflowEdge.source_node == node.node_key,
            )
        )
        edges = result.scalars().all()

        if not edges:
            # 并行节点没有输出连线，流程结束
            instance.status = "completed"
            instance.completed_at = datetime.now(timezone.utc)
            return

        # 收集所有目标节点
        target_nodes = []
        non_approval_targets = []
        for edge in edges:
            # 获取目标节点信息
            node_result = await self.db.execute(
                select(WorkflowNode).where(
                    WorkflowNode.workflow_id == instance.workflow_id,
                    WorkflowNode.node_key == edge.target_node,
                )
            )
            target_node = node_result.scalar_one_or_none()
            if target_node:
                if target_node.node_type == "approval":
                    target_nodes.append(target_node)
                else:
                    # 记录非审批节点
                    non_approval_targets.append(target_node)

        if not target_nodes:
            # 没有审批节点
            if non_approval_targets:
                # 如果有非审批节点，直接流转到第一个目标节点
                await self._flow_to_node(instance, non_approval_targets[0].node_key)
            else:
                # 如果没有任何目标节点，流程结束
                instance.status = "completed"
                instance.completed_at = datetime.now(timezone.utc)
            return

        # 记录并行状态
        instance.parallel_node_key = node.node_key
        instance.parallel_targets = [n.node_key for n in target_nodes]

        # 为每个目标节点创建任务
        for target_node in target_nodes:
            await self._create_approval_task(instance, target_node, parallel_source=node.node_key)

        # 更新当前节点为并行节点
        instance.current_node = node.node_key


class WorkflowDefinitionService:
    """
    流程定义服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_definition(self, data: WorkflowDefinitionCreate) -> WorkflowDefinitionResponse:
        """创建流程定义"""
        # 检查编码是否已存在
        result = await self.db.execute(
            select(WorkflowDefinition).where(
                WorkflowDefinition.code == data.code,
                WorkflowDefinition.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("流程编码已存在")

        # 创建流程定义
        definition = WorkflowDefinition(
            name=data.name,
            code=data.code,
            category=data.category,
            description=data.description,
            form_config=data.form_config,
        )

        self.db.add(definition)
        await self.db.flush()

        # 创建节点
        for node_data in data.nodes:
            node = WorkflowNode(
                workflow_id=definition.id,
                **node_data
            )
            self.db.add(node)

        # 创建连线
        for edge_data in data.edges:
            edge = WorkflowEdge(
                workflow_id=definition.id,
                **edge_data
            )
            self.db.add(edge)

        await self.db.commit()
        await self.db.refresh(definition)

        return WorkflowDefinitionResponse.model_validate(definition)

    async def get_definitions(self, category: Optional[str] = None) -> List[WorkflowDefinitionResponse]:
        """获取流程定义列表"""
        query = select(WorkflowDefinition).where(
            WorkflowDefinition.is_deleted == False
        )

        if category:
            query = query.where(WorkflowDefinition.category == category)

        result = await self.db.execute(query.order_by(WorkflowDefinition.created_at.desc()))
        definitions = result.scalars().all()

        return [WorkflowDefinitionResponse.model_validate(d) for d in definitions]

    async def get_definition(self, definition_id: int) -> dict:
        """获取流程定义详情（包含节点和连线）"""
        result = await self.db.execute(
            select(WorkflowDefinition).where(
                WorkflowDefinition.id == definition_id,
                WorkflowDefinition.is_deleted == False,
            )
        )
        definition = result.scalar_one_or_none()

        if not definition:
            raise NotFoundError("流程定义不存在")

        # 获取节点
        nodes_result = await self.db.execute(
            select(WorkflowNode).where(
                WorkflowNode.workflow_id == definition_id
            ).order_by(WorkflowNode.sort_order)
        )
        nodes = nodes_result.scalars().all()

        # 获取连线
        edges_result = await self.db.execute(
            select(WorkflowEdge).where(
                WorkflowEdge.workflow_id == definition_id
            )
        )
        edges = edges_result.scalars().all()

        return {
            "id": definition.id,
            "name": definition.name,
            "code": definition.code,
            "category": definition.category,
            "description": definition.description,
            "form_config": definition.form_config,
            "is_active": definition.is_active,
            "created_at": definition.created_at,
            "updated_at": definition.updated_at,
            "nodes": [
                {
                    "id": n.id,
                    "node_key": n.node_key,
                    "node_type": n.node_type,
                    "name": n.name,
                    "config": n.config,
                    "sort_order": n.sort_order,
                }
                for n in nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source_node": e.source_node,
                    "target_node": e.target_node,
                    "condition": e.condition,
                }
                for e in edges
            ],
        }

    async def update_definition(self, definition_id: int, data: WorkflowDefinitionUpdate) -> WorkflowDefinitionResponse:
        """更新流程定义"""
        result = await self.db.execute(
            select(WorkflowDefinition).where(
                WorkflowDefinition.id == definition_id,
                WorkflowDefinition.is_deleted == False,
            )
        )
        definition = result.scalar_one_or_none()

        if not definition:
            raise NotFoundError("流程定义不存在")

        # 更新基本信息
        for field, value in data.model_dump(exclude_unset=True, exclude={"nodes", "edges"}).items():
            setattr(definition, field, value)

        # 更新节点和连线
        if data.nodes is not None or data.edges is not None:
            # 删除现有节点和连线
            await self.db.execute(
                select(WorkflowNode).where(WorkflowNode.workflow_id == definition_id)
            )
            await self.db.execute(
                select(WorkflowEdge).where(WorkflowEdge.workflow_id == definition_id)
            )

            # 重新创建
            if data.nodes:
                for node_data in data.nodes:
                    node = WorkflowNode(workflow_id=definition_id, **node_data)
                    self.db.add(node)

            if data.edges:
                for edge_data in data.edges:
                    edge = WorkflowEdge(workflow_id=definition_id, **edge_data)
                    self.db.add(edge)

        await self.db.commit()
        await self.db.refresh(definition)

        return WorkflowDefinitionResponse.model_validate(definition)

    async def delete_definition(self, definition_id: int) -> None:
        """删除流程定义（软删除）"""
        result = await self.db.execute(
            select(WorkflowDefinition).where(
                WorkflowDefinition.id == definition_id,
                WorkflowDefinition.is_deleted == False,
            )
        )
        definition = result.scalar_one_or_none()

        if not definition:
            raise NotFoundError("流程定义不存在")

        definition.is_deleted = True
        definition.deleted_at = datetime.now(timezone.utc)

        await self.db.commit()
