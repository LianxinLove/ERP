"""
审批流程数据模型

@description 工作流引擎的数据库模型

@features
- 可配置的审批流程
- 多种节点类型（开始、结束、审批、条件、并行）
- 流程实例和任务管理
- 审批记录追踪
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WorkflowDefinition(Base):
    """
    流程定义模型

    Attributes:
        id: 主键ID
        name: 流程名称
        code: 流程编码（唯一）
        category: 流程分类
        description: 流程描述
        form_config: 表单配置（JSON）
        is_active: 是否启用
        created_at: 创建时间
        updated_at: 更新时间
        created_by: 创建人ID
        updated_by: 更新人ID
        is_deleted: 是否删除
        deleted_at: 删除时间
    """

    __tablename__ = "workflow_definitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    form_config: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by: Mapped[Optional[int]] = mapped_column()
    updated_by: Mapped[Optional[int]] = mapped_column()
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    nodes: Mapped[list["WorkflowNode"]] = relationship(
        "WorkflowNode", back_populates="workflow", cascade="all, delete-orphan"
    )
    instances: Mapped[list["WorkflowInstance"]] = relationship(
        "WorkflowInstance", back_populates="definition"
    )

    def __repr__(self) -> str:
        return f"<WorkflowDefinition(id={self.id}, name='{self.name}', code='{self.code}')>"


class WorkflowNode(Base):
    """
    流程节点模型

    节点类型：
    - start: 开始节点
    - end: 结束节点
    - approval: 审批节点
    - condition: 条件节点
    - parallel: 并行节点

    Attributes:
        id: 主键ID
        workflow_id: 流程定义ID
        node_key: 节点标识（唯一）
        node_type: 节点类型
        name: 节点名称
        config: 节点配置（JSON）
        sort_order: 排序
        created_at: 创建时间
        updated_at: 更新时间
    """

    __tablename__ = "workflow_nodes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[Optional[dict]] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # 关系
    workflow: Mapped["WorkflowDefinition"] = relationship("WorkflowDefinition", back_populates="nodes")

    def __repr__(self) -> str:
        return f"<WorkflowNode(id={self.id}, key='{self.node_key}', type='{self.node_type}')>"


class WorkflowEdge(Base):
    """
    流程连线模型

    定义节点之间的流转关系

    Attributes:
        id: 主键ID
        workflow_id: 流程定义ID
        source_node: 源节点标识
        target_node: 目标节点标识
        condition: 流转条件（JSON）
        created_at: 创建时间
    """

    __tablename__ = "workflow_edges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_node: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_node: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condition: Mapped[Optional[dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<WorkflowEdge(id={self.id}, {self.source_node} -> {self.target_node})>"


class WorkflowInstance(Base):
    """
    流程实例模型

    流程定义的具体运行实例

    Attributes:
        id: 主键ID
        workflow_id: 流程定义ID
        instance_no: 实例编号（唯一）
        title: 实例标题
        status: 状态
        current_node: 当前节点
        business_key: 业务键
        form_data: 表单数据（JSON）
        initiator_id: 发起人ID
        parallel_node_key: 并行节点标识（用于并行任务追踪）
        parallel_targets: 并行目标节点列表（JSON）
        created_at: 创建时间
        updated_at: 更新时间
        completed_at: 完成时间
    """

    __tablename__ = "workflow_instances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_definitions.id"), nullable=False, index=True
    )
    instance_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # running, completed, rejected, cancelled
    current_node: Mapped[Optional[str]] = mapped_column(String(50))
    business_key: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    form_data: Mapped[Optional[dict]] = mapped_column(JSON)
    initiator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    parallel_node_key: Mapped[Optional[str]] = mapped_column(String(50))  # 当前并行处理的源节点
    parallel_targets: Mapped[Optional[list]] = mapped_column(JSON)  # 并行任务的目标节点列表

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    definition: Mapped["WorkflowDefinition"] = relationship("WorkflowDefinition", back_populates="instances")
    tasks: Mapped[list["WorkflowTask"]] = relationship(
        "WorkflowTask", back_populates="instance", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkflowInstance(id={self.id}, no='{self.instance_no}', status='{self.status}')>"


class WorkflowTask(Base):
    """
    审批任务模型

    流程实例中的单个审批任务

    Attributes:
        id: 主键ID
        instance_id: 流程实例ID
        node_key: 节点标识
        node_name: 节点名称
        assignee_id: 审批人ID
        status: 状态
        comment: 审批意见
        due_date: 到期时间
        parallel_source_node: 并行源节点（标识此任务属于哪个并行组）
        created_at: 创建时间
        updated_at: 更新时间
        completed_at: 完成时间
    """

    __tablename__ = "workflow_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instance_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_instances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # pending, approved, rejected, returned, cancelled
    comment: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    parallel_source_node: Mapped[Optional[str]] = mapped_column(String(50), index=True)  # 并行源节点

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # 关系
    instance: Mapped["WorkflowInstance"] = relationship("WorkflowInstance", back_populates="tasks")
    approvals: Mapped[list["WorkflowApproval"]] = relationship(
        "WorkflowApproval", back_populates="task", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkflowTask(id={self.id}, node='{self.node_key}', status='{self.status}')>"


class WorkflowApproval(Base):
    """
    审批记录模型

    记录每次审批操作的详细信息

    Attributes:
        id: 主键ID
        task_id: 任务ID
        instance_id: 流程实例ID
        approver_id: 审批人ID
        action: 操作类型
        comment: 审批意见
        attachments: 附件（JSON）
        created_at: 创建时间
    """

    __tablename__ = "workflow_approvals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    instance_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_instances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # approve, reject, return
    comment: Mapped[Optional[str]] = mapped_column(Text)
    attachments: Mapped[Optional[list]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 关系
    task: Mapped["WorkflowTask"] = relationship("WorkflowTask", back_populates="approvals")

    def __repr__(self) -> str:
        return f"<WorkflowApproval(id={self.id}, action='{self.action}')>"
