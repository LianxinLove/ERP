"""
组织架构服务

@description 部门、职位、员工档案的业务逻辑

@features
- 部门树形结构管理
- 职位管理
- 员工档案管理
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.organization import Department, Position, EmployeeProfile
from app.models.user import User
from app.schemas.organization import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    DepartmentTree,
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    EmployeeProfileResponse,
    EmployeeDetailResponse,
)


class DepartmentService:
    """
    部门服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_department(self, data: DepartmentCreate) -> DepartmentResponse:
        """
        创建部门

        Args:
            data: 部门创建数据

        Returns:
            DepartmentResponse: 创建的部门信息

        Raises:
            BadRequestError: 部门编码已存在
        """
        # 检查部门编码是否已存在
        result = await self.db.execute(
            select(Department).where(Department.code == data.code, Department.is_deleted == False)
        )
        if result.scalar_one_or_none():
            raise BadRequestError("部门编码已存在")

        # 计算层级
        level = 1
        if data.parent_id:
            parent_result = await self.db.execute(
                select(Department).where(
                    Department.id == data.parent_id, Department.is_deleted == False
                )
            )
            parent = parent_result.scalar_one_or_none()
            if parent:
                level = parent.level + 1

        department = Department(
            name=data.name,
            code=data.code,
            parent_id=data.parent_id,
            level=level,
            sort_order=data.sort_order,
            leader_id=data.leader_id,
            description=data.description,
        )

        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)

        return DepartmentResponse.model_validate(department)

    async def get_departments(self, as_tree: bool = False) -> List[DepartmentResponse]:
        """
        获取部门列表

        Args:
            as_tree: 是否返回树形结构

        Returns:
            List[DepartmentResponse]: 部门列表
        """
        result = await self.db.execute(
            select(Department)
            .where(Department.is_deleted == False)
            .order_by(Department.sort_order, Department.id)
        )
        departments = result.scalars().all()

        if as_tree:
            return self._build_tree(departments)

        return [DepartmentResponse.model_validate(d) for d in departments]

    async def get_department(self, department_id: int) -> DepartmentResponse:
        """
        获取部门详情

        Args:
            department_id: 部门ID

        Returns:
            DepartmentResponse: 部门详情

        Raises:
            NotFoundError: 部门不存在
        """
        result = await self.db.execute(
            select(Department).where(
                Department.id == department_id, Department.is_deleted == False
            )
        )
        department = result.scalar_one_or_none()

        if not department:
            raise NotFoundError("部门不存在")

        return DepartmentResponse.model_validate(department)

    async def update_department(
        self, department_id: int, data: DepartmentUpdate
    ) -> DepartmentResponse:
        """
        更新部门

        Args:
            department_id: 部门ID
            data: 更新数据

        Returns:
            DepartmentResponse: 更新后的部门信息

        Raises:
            NotFoundError: 部门不存在
            BadRequestError: 不能将部门设置为自己的子部门
        """
        result = await self.db.execute(
            select(Department).where(
                Department.id == department_id, Department.is_deleted == False
            )
        )
        department = result.scalar_one_or_none()

        if not department:
            raise NotFoundError("部门不存在")

        # 检查是否将部门设置为自己的子部门
        if data.parent_id and data.parent_id == department_id:
            raise BadRequestError("不能将部门设置为自己的子部门")

        # 检查是否形成循环引用
        if data.parent_id is not None and data.parent_id:
            if await self._would_create_circular_reference(department_id, data.parent_id):
                raise BadRequestError("不能将部门设置为自己的后代部门（会形成循环引用）")

        # 更新基本信息
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(department, field, value)

        # 重新计算层级
        if data.parent_id is not None:
            if data.parent_id:
                parent_result = await self.db.execute(
                    select(Department).where(
                        Department.id == data.parent_id, Department.is_deleted == False
                    )
                )
                parent = parent_result.scalar_one_or_none()
                if parent:
                    department.level = parent.level + 1
            else:
                department.level = 1

        await self.db.commit()
        await self.db.refresh(department)

        return DepartmentResponse.model_validate(department)

    async def delete_department(self, department_id: int) -> None:
        """
        删除部门（软删除）

        Args:
            department_id: 部门ID

        Raises:
            NotFoundError: 部门不存在
            BadRequestError: 部门下有子部门或员工
        """
        result = await self.db.execute(
            select(Department).where(
                Department.id == department_id, Department.is_deleted == False
            )
        )
        department = result.scalar_one_or_none()

        if not department:
            raise NotFoundError("部门不存在")

        # 检查是否有子部门
        children_result = await self.db.execute(
            select(Department).where(
                Department.parent_id == department_id, Department.is_deleted == False
            )
        )
        if children_result.scalar_one_or_none():
            raise BadRequestError("部门下有子部门，无法删除")

        # 检查是否有员工
        employee_result = await self.db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.department_id == department_id,
                EmployeeProfile.is_deleted == False,
                EmployeeProfile.status == "active",
            )
        )
        if employee_result.scalar_one_or_none():
            raise BadRequestError("部门下有在职员工，无法删除")

        department.is_deleted = True
        department.deleted_at = datetime.now(timezone.utc)

        await self.db.commit()

    def _build_tree(
        self, departments: List[Department], parent_id: Optional[int] = None
    ) -> List[DepartmentTree]:
        """
        构建部门树

        Args:
            departments: 部门列表
            parent_id: 父部门ID

        Returns:
            List[DepartmentTree]: 树形结构
        """
        tree = []
        for dept in departments:
            if dept.parent_id == parent_id:
                dept_dict = DepartmentTree.model_validate(dept)
                dept_dict.children = self._build_tree(departments, dept.id)
                tree.append(dept_dict)
        return tree

    async def _would_create_circular_reference(
        self, department_id: int, new_parent_id: int
    ) -> bool:
        """
        检查设置新的父部门是否会形成循环引用

        Args:
            department_id: 要更新的部门ID
            new_parent_id: 新的父部门ID

        Returns:
            bool: 是否会形成循环引用
        """
        # 从新父部门开始，向上遍历其所有父部门
        current_parent_id = new_parent_id
        visited = {department_id, new_parent_id}  # 记录已访问的部门，防止无限循环

        while current_parent_id:
            # 如果向上遍历遇到了自己，说明会形成循环
            if current_parent_id == department_id:
                return True

            # 查找当前父部门的父部门
            result = await self.db.execute(
                select(Department).where(
                    Department.id == current_parent_id,
                    Department.is_deleted == False
                )
            )
            current_dept = result.scalar_one_or_none()

            if not current_dept:
                break

            if current_dept.parent_id in visited:
                # 防止已存在的循环导致无限循环
                break

            visited.add(current_dept.parent_id)
            current_parent_id = current_dept.parent_id

        return False


class PositionService:
    """
    职位服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_position(self, data: PositionCreate) -> PositionResponse:
        """
        创建职位

        Args:
            data: 职位创建数据

        Returns:
            PositionResponse: 创建的职位信息

        Raises:
            BadRequestError: 职位编码已存在
        """
        # 检查职位编码是否已存在
        result = await self.db.execute(
            select(Position).where(Position.code == data.code, Position.is_deleted == False)
        )
        if result.scalar_one_or_none():
            raise BadRequestError("职位编码已存在")

        position = Position(**data.model_dump())

        self.db.add(position)
        await self.db.commit()
        await self.db.refresh(position)

        return PositionResponse.model_validate(position)

    async def get_positions(self) -> List[PositionResponse]:
        """
        获取职位列表

        Returns:
            List[PositionResponse]: 职位列表
        """
        result = await self.db.execute(
            select(Position)
            .where(Position.is_deleted == False)
            .order_by(Position.level, Position.id)
        )
        positions = result.scalars().all()

        return [PositionResponse.model_validate(p) for p in positions]

    async def get_position(self, position_id: int) -> PositionResponse:
        """
        获取职位详情

        Args:
            position_id: 职位ID

        Returns:
            PositionResponse: 职位详情

        Raises:
            NotFoundError: 职位不存在
        """
        result = await self.db.execute(
            select(Position).where(
                Position.id == position_id, Position.is_deleted == False
            )
        )
        position = result.scalar_one_or_none()

        if not position:
            raise NotFoundError("职位不存在")

        return PositionResponse.model_validate(position)

    async def update_position(
        self, position_id: int, data: PositionUpdate
    ) -> PositionResponse:
        """
        更新职位

        Args:
            position_id: 职位ID
            data: 更新数据

        Returns:
            PositionResponse: 更新后的职位信息

        Raises:
            NotFoundError: 职位不存在
        """
        result = await self.db.execute(
            select(Position).where(
                Position.id == position_id, Position.is_deleted == False
            )
        )
        position = result.scalar_one_or_none()

        if not position:
            raise NotFoundError("职位不存在")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(position, field, value)

        await self.db.commit()
        await self.db.refresh(position)

        return PositionResponse.model_validate(position)

    async def delete_position(self, position_id: int) -> None:
        """
        删除职位（软删除）

        Args:
            position_id: 职位ID

        Raises:
            NotFoundError: 职位不存在
            BadRequestError: 职位下有员工
        """
        result = await self.db.execute(
            select(Position).where(
                Position.id == position_id, Position.is_deleted == False
            )
        )
        position = result.scalar_one_or_none()

        if not position:
            raise NotFoundError("职位不存在")

        # 检查是否有员工使用该职位
        employee_result = await self.db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.position_id == position_id,
                EmployeeProfile.is_deleted == False,
                EmployeeProfile.status == "active",
            )
        )
        if employee_result.scalar_one_or_none():
            raise BadRequestError("该职位下有在职员工，无法删除")

        position.is_deleted = True
        position.deleted_at = datetime.now(timezone.utc)

        await self.db.commit()


class EmployeeService:
    """
    员工档案服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_employee_profile(
        self, data: EmployeeProfileCreate
    ) -> EmployeeDetailResponse:
        """
        创建员工档案

        Args:
            data: 员工档案创建数据

        Returns:
            EmployeeDetailResponse: 创建的员工档案信息

        Raises:
            BadRequestError: 员工编号已存在或用户已有档案
        """
        # 检查员工编号是否已存在
        result = await self.db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.employee_no == data.employee_no, EmployeeProfile.is_deleted == False
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("员工编号已存在")

        # 检查用户是否已有档案
        result = await self.db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.user_id == data.user_id, EmployeeProfile.is_deleted == False
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("该用户已有员工档案")

        # 检查用户是否存在
        user_result = await self.db.execute(select(User).where(User.id == data.user_id))
        if not user_result.scalar_one_or_none():
            raise BadRequestError("用户不存在")

        # 检查部门和职位是否存在
        if data.department_id:
            dept_result = await self.db.execute(
                select(Department).where(
                    Department.id == data.department_id, Department.is_deleted == False
                )
            )
            if not dept_result.scalar_one_or_none():
                raise BadRequestError("部门不存在")

        if data.position_id:
            pos_result = await self.db.execute(
                select(Position).where(
                    Position.id == data.position_id, Position.is_deleted == False
                )
            )
            if not pos_result.scalar_one_or_none():
                raise BadRequestError("职位不存在")

        employee = EmployeeProfile(**data.model_dump())

        self.db.add(employee)
        await self.db.commit()

        return await self.get_employee_profile(employee.id)

    async def get_employees(
        self,
        department_id: Optional[int] = None,
        position_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[EmployeeDetailResponse]:
        """
        获取员工列表

        Args:
            department_id: 部门ID（可选）
            position_id: 职位ID（可选）
            status: 状态（可选）

        Returns:
            List[EmployeeDetailResponse]: 员工列表
        """
        query = (
            select(EmployeeProfile)
            .join(User, EmployeeProfile.user_id == User.id)
            .outerjoin(Department, EmployeeProfile.department_id == Department.id)
            .outerjoin(Position, EmployeeProfile.position_id == Position.id)
            .where(EmployeeProfile.is_deleted == False)
        )

        if department_id:
            query = query.filter(EmployeeProfile.department_id == department_id)

        if position_id:
            query = query.filter(EmployeeProfile.position_id == position_id)

        if status:
            query = query.filter(EmployeeProfile.status == status)

        result = await self.db.execute(query)
        employees = result.scalars().all()

        return [
            EmployeeDetailResponse(
                id=e.id,
                user_id=e.user_id,
                employee_no=e.employee_no,
                department_id=e.department_id,
                position_id=e.position_id,
                entry_date=e.entry_date,
                status=e.status,
                created_at=e.created_at,
                updated_at=e.updated_at,
                username=e.user.username,
                email=e.user.email,
                full_name=e.user.full_name,
                phone=e.user.phone,
                department=DepartmentResponse.model_validate(e.department) if e.department else None,
                position=PositionResponse.model_validate(e.position) if e.position else None,
            )
            for e in employees
        ]

    async def get_employee_profile(self, employee_id: int) -> EmployeeDetailResponse:
        """
        获取员工档案详情

        Args:
            employee_id: 员工档案ID

        Returns:
            EmployeeDetailResponse: 员工档案详情

        Raises:
            NotFoundError: 员工档案不存在
        """
        result = await self.db.execute(
            select(EmployeeProfile)
            .join(User, EmployeeProfile.user_id == User.id)
            .outerjoin(Department, EmployeeProfile.department_id == Department.id)
            .outerjoin(Position, EmployeeProfile.position_id == Position.id)
            .where(EmployeeProfile.id == employee_id, EmployeeProfile.is_deleted == False)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise NotFoundError("员工档案不存在")

        return EmployeeDetailResponse(
            id=employee.id,
            user_id=employee.user_id,
            employee_no=employee.employee_no,
            department_id=employee.department_id,
            position_id=employee.position_id,
            entry_date=employee.entry_date,
            status=employee.status,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
            username=employee.user.username,
            email=employee.user.email,
            full_name=employee.user.full_name,
            phone=employee.user.phone,
            department=DepartmentResponse.model_validate(employee.department) if employee.department else None,
            position=PositionResponse.model_validate(employee.position) if employee.position else None,
        )

    async def update_employee_profile(
        self, employee_id: int, data: EmployeeProfileUpdate
    ) -> EmployeeDetailResponse:
        """
        更新员工档案

        Args:
            employee_id: 员工档案ID
            data: 更新数据

        Returns:
            EmployeeDetailResponse: 更新后的员工档案信息

        Raises:
            NotFoundError: 员工档案不存在
        """
        result = await self.db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.id == employee_id, EmployeeProfile.is_deleted == False
            )
        )
        employee = result.scalar_one_or_none()

        if not employee:
            raise NotFoundError("员工档案不存在")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(employee, field, value)

        await self.db.commit()

        return await self.get_employee_profile(employee_id)
