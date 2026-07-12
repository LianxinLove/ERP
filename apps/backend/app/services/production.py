"""
生产制造服务层

@description 生产制造模块的业务逻辑
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.production import (
    BOM,
    BOMItem,
    BOMStatus,
    BOMItemType,
    ProductionOrder,
    ProductionOrderItem,
    ProductionOrderStatus,
    ProductionProcess,
    Routing,
    WorkOrder,
    WorkOrderStatus,
    WorkCenter,
)


class BOMService:
    """BOM服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_bom(
        self,
        product_id: int,
        product_code: str,
        product_name: str,
        version: str = "1.0",
        base_quantity: Decimal = Decimal("1.00"),
        **kwargs
    ) -> BOM:
        """创建BOM"""
        bom = BOM(
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            version=version,
            base_quantity=base_quantity,
            **kwargs
        )
        self.db.add(bom)
        self.db.flush()
        return bom

    def add_bom_item(
        self,
        bom_id: int,
        line_no: int,
        component_code: str,
        component_name: str,
        quantity: Decimal,
        item_type: BOMItemType = BOMItemType.MATERIAL,
        **kwargs
    ) -> BOMItem:
        """添加BOM明细"""
        item = BOMItem(
            bom_id=bom_id,
            line_no=line_no,
            component_code=component_code,
            component_name=component_name,
            quantity=quantity,
            item_type=item_type,
            **kwargs
        )
        self.db.add(item)
        self.db.flush()
        return item

    def get_bom_by_product(self, product_id: int) -> Optional[BOM]:
        """根据产品ID获取生效的BOM"""
        return self.db.query(BOM).filter(
            and_(
                BOM.product_id == product_id,
                BOM.status == BOMStatus.ACTIVE
            )
        ).first()

    def calculate_bom_cost(self, bom_id: int) -> dict:
        """
        计算BOM成本

        Returns:
            dict: 包含材料成本、人工成本、制造费用和总成本
        """
        bom = self.db.query(BOM).get(bom_id)
        if not bom:
            return None

        material_cost = Decimal("0.00")
        for item in bom.items:
            # 这里应该从产品主数据获取成本价
            # 暂时返回0
            pass

        return {
            "material_cost": material_cost,
            "labor_cost": bom.cost_labor or Decimal("0.00"),
            "overhead_cost": bom.cost_overhead or Decimal("0.00"),
            "total_cost": material_cost + (bom.cost_labor or Decimal("0.00")) + (bom.cost_overhead or Decimal("0.00")),
        }

    def activate_bom(self, bom_id: int) -> BOM:
        """激活BOM"""
        bom = self.db.query(BOM).get(bom_id)
        if bom:
            bom.status = BOMStatus.ACTIVE
            bom.effective_date = datetime.now()
        return bom

    def expire_bom(self, bom_id: int) -> BOM:
        """失效BOM"""
        bom = self.db.query(BOM).get(bom_id)
        if bom:
            bom.status = BOMStatus.EXPIRED
            bom.expiry_date = datetime.now()
        return bom


class ProductionOrderService:
    """生产订单服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_production_order(
        self,
        order_no: str,
        product_id: int,
        product_code: str,
        product_name: str,
        quantity: Decimal,
        bom_id: Optional[int] = None,
        plan_start_date: Optional[datetime] = None,
        plan_end_date: Optional[datetime] = None,
        **kwargs
    ) -> ProductionOrder:
        """创建生产订单"""
        order = ProductionOrder(
            order_no=order_no,
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            quantity=quantity,
            bom_id=bom_id,
            plan_start_date=plan_start_date,
            plan_end_date=plan_end_date,
            **kwargs
        )
        self.db.add(order)
        self.db.flush()

        # 如果指定了BOM，自动生成子件需求
        if bom_id:
            self._generate_material_requirements(order)

        return order

    def _generate_material_requirements(self, order: ProductionOrder):
        """生成物料需求"""
        bom = self.db.query(BOM).get(order.bom_id)
        if not bom:
            return

        # 计算每单位产品的子件用量
        multiplier = order.quantity / bom.base_quantity if bom.base_quantity else Decimal("1.00")

        for item in bom.items:
            required_qty = item.quantity * multiplier
            # 考虑损耗率
            if item.scrap_rate:
                required_qty = required_qty * (1 + item.scrap_rate / 100)

            order_item = ProductionOrderItem(
                order_id=order.id,
                component_id=item.component_id,
                component_code=item.component_code,
                component_name=item.component_name,
                required_quantity=required_qty.round(2),
                unit=item.unit
            )
            self.db.add(order_item)

        self.db.flush()

    def release_order(self, order_id: int) -> ProductionOrder:
        """下达生产订单"""
        order = self.db.query(ProductionOrder).get(order_id)
        if order:
            order.status = ProductionOrderStatus.RELEASED
            order.actual_start_date = datetime.now()
        return order

    def complete_order(self, order_id: int, qualified_quantity: Decimal) -> ProductionOrder:
        """完成生产订单"""
        order = self.db.query(ProductionOrder).get(order_id)
        if order:
            order.qualified_quantity = qualified_quantity
            order.status = ProductionOrderStatus.COMPLETED
            order.actual_end_date = datetime.now()
        return order


class WorkOrderService:
    """派工单服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_work_order(
        self,
        work_no: str,
        production_order_id: int,
        process_id: int,
        quantity: Decimal,
        plan_start_time: Optional[datetime] = None,
        plan_end_time: Optional[datetime] = None,
        **kwargs
    ) -> WorkOrder:
        """创建派工单"""
        work_order = WorkOrder(
            work_no=work_no,
            production_order_id=production_order_id,
            process_id=process_id,
            quantity=quantity,
            plan_start_time=plan_start_time,
            plan_end_time=plan_end_time,
            **kwargs
        )
        self.db.add(work_order)
        self.db.flush()
        return work_order

    def start_work(self, work_order_id: int) -> WorkOrder:
        """开始加工"""
        work_order = self.db.query(WorkOrder).get(work_order_id)
        if work_order:
            work_order.status = WorkOrderStatus.IN_PROGRESS
            work_order.actual_start_time = datetime.now()
        return work_order

    def complete_work(
        self,
        work_order_id: int,
        qualified_quantity: Decimal,
        rejected_quantity: Decimal = Decimal("0.00")
    ) -> WorkOrder:
        """完成加工"""
        work_order = self.db.query(WorkOrder).get(work_order_id)
        if work_order:
            work_order.qualified_quantity = qualified_quantity
            work_order.rejected_quantity = rejected_quantity
            work_order.completed_quantity = qualified_quantity + rejected_quantity
            work_order.status = WorkOrderStatus.COMPLETED
            work_order.actual_end_time = datetime.now()
        return work_order


class WorkCenterService:
    """工作中心服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_work_center(
        self,
        code: str,
        name: str,
        capacity: Optional[Decimal] = None,
        efficiency: Decimal = Decimal("100.00"),
        **kwargs
    ) -> WorkCenter:
        """创建工作中心"""
        work_center = WorkCenter(
            code=code,
            name=name,
            capacity=capacity,
            efficiency=efficiency,
            **kwargs
        )
        self.db.add(work_center)
        self.db.flush()
        return work_center

    def get_work_center_load(self, work_center_id: int) -> dict:
        """获取工作中心负荷"""
        # 获取该工作中心所有进行中的派工单
        active_work_orders = self.db.query(WorkOrder).filter(
            and_(
                WorkOrder.work_center_id == work_center_id,
                WorkOrder.status == WorkOrderStatus.IN_PROGRESS
            )
        ).all()

        total_quantity = sum(wo.quantity for wo in active_work_orders)
        completed_quantity = sum(wo.completed_quantity for wo in active_work_orders)

        return {
            "total_quantity": total_quantity,
            "completed_quantity": completed_quantity,
            "remaining_quantity": total_quantity - completed_quantity,
            "active_orders": len(active_work_orders),
        }


class ProductionProcessService:
    """工序服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_process(
        self,
        code: str,
        name: str,
        work_center_id: Optional[int] = None,
        standard_hours: Optional[Decimal] = None,
        **kwargs
    ) -> ProductionProcess:
        """创建工序"""
        process = ProductionProcess(
            code=code,
            name=name,
            work_center_id=work_center_id,
            standard_hours=standard_hours,
            **kwargs
        )
        self.db.add(process)
        self.db.flush()
        return process

    def get_routing_by_product(self, product_id: int) -> Optional[Routing]:
        """获取产品的工艺路线"""
        return self.db.query(Routing).filter(
            and_(
                Routing.product_id == product_id,
                Routing.is_default == True
            )
        ).first()
