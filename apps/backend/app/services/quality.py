"""
质量管理服务层

@description 质量管理模块的业务逻辑
"""

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.quality import (
    InspectionScheme,
    InspectionItem,
    InspectionStandard,
    SamplingPlan,
    IncomingInspection,
    IncomingInspectionItem,
    ProcessInspection,
    ProcessInspectionItem,
    OutgoingInspection,
    OutgoingInspectionItem,
    QualityTrace,
    InspectionType,
    InspectionMethod,
    InspectionResult,
    InspectionStatus,
    DefectLevel,
)


class InspectionSchemeService:
    """质检方案服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_scheme(
        self,
        code: str,
        name: str,
        inspection_type: InspectionType,
        sampling_plan_id: Optional[int] = None,
        **kwargs
    ) -> InspectionScheme:
        """创建质检方案"""
        scheme = InspectionScheme(
            code=code,
            name=name,
            inspection_type=inspection_type,
            sampling_plan_id=sampling_plan_id,
            **kwargs
        )
        self.db.add(scheme)
        self.db.flush()
        return scheme

    def add_inspection_item(
        self,
        scheme_id: int,
        code: str,
        name: str,
        inspection_method: InspectionMethod = InspectionMethod.QUALITATIVE,
        defect_level: DefectLevel = DefectLevel.NORMAL,
        **kwargs
    ) -> InspectionItem:
        """添加检验项目"""
        item = InspectionItem(
            scheme_id=scheme_id,
            code=code,
            name=name,
            inspection_method=inspection_method,
            defect_level=defect_level,
            **kwargs
        )
        self.db.add(item)
        self.db.flush()
        return item

    def get_default_scheme(self, inspection_type: InspectionType) -> Optional[InspectionScheme]:
        """获取默认质检方案"""
        return self.db.query(InspectionScheme).filter(
            and_(
                InspectionScheme.inspection_type == inspection_type,
                InspectionScheme.is_default == True,
                InspectionScheme.is_active == True
            )
        ).first()

    def set_default_scheme(self, scheme_id: int) -> InspectionScheme:
        """设置默认方案"""
        # 先取消其他同类型的默认方案
        scheme = self.db.query(InspectionScheme).get(scheme_id)
        if scheme:
            self.db.query(InspectionScheme).filter(
                and_(
                    InspectionScheme.inspection_type == scheme.inspection_type,
                    InspectionScheme.id != scheme_id
                )
            ).update({"is_default": False})
            scheme.is_default = True
        return scheme


class IncomingInspectionService:
    """来料检验服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_inspection(
        self,
        inspection_no: str,
        supplier_id: int,
        product_id: int,
        quantity: Decimal,
        purchase_order_id: Optional[int] = None,
        receipt_id: Optional[int] = None,
        batch_no: Optional[str] = None,
        **kwargs
    ) -> IncomingInspection:
        """创建来料检验单"""
        inspection = IncomingInspection(
            inspection_no=inspection_no,
            supplier_id=supplier_id,
            product_id=product_id,
            quantity=quantity,
            purchase_order_id=purchase_order_id,
            receipt_id=receipt_id,
            batch_no=batch_no,
            **kwargs
        )
        self.db.add(inspection)
        self.db.flush()
        return inspection

    def start_inspection(self, inspection_id: int, inspector_id: int) -> IncomingInspection:
        """开始检验"""
        inspection = self.db.query(IncomingInspection).get(inspection_id)
        if inspection:
            inspection.status = InspectionStatus.INSPECTING
            inspection.inspector_id = inspector_id
            inspection.inspection_date = datetime.now()
        return inspection

    def add_inspection_result(
        self,
        inspection_id: int,
        item_id: int,
        item_name: str,
        measured_value: Optional[str] = None,
        is_qualified: bool = True,
        defect_level: Optional[DefectLevel] = None,
        **kwargs
    ) -> IncomingInspectionItem:
        """添加检验结果"""
        item = IncomingInspectionItem(
            inspection_id=inspection_id,
            item_id=item_id,
            item_name=item_name,
            measured_value=measured_value,
            is_qualified=is_qualified,
            defect_level=defect_level,
            **kwargs
        )
        self.db.add(item)
        self.db.flush()

        # 更新检验单的统计
        self._update_inspection_stats(inspection_id)

        return item

    def _update_inspection_stats(self, inspection_id: int):
        """更新检验统计数据"""
        inspection = self.db.query(IncomingInspection).get(inspection_id)
        if not inspection:
            return

        items = self.db.query(IncomingInspectionItem).filter(
            IncomingInspectionItem.inspection_id == inspection_id
        ).all()

        qualified_count = sum(1 for item in items if item.is_qualified)
        inspection.qualified_quantity = Decimal(str(qualified_count))
        inspection.rejected_quantity = Decimal(str(len(items) - qualified_count))

        # 判断检验结果
        if inspection.rejected_quantity > 0:
            inspection.inspection_result = InspectionResult.UNQUALIFIED
        else:
            inspection.inspection_result = InspectionResult.QUALIFIED

    def complete_inspection(self, inspection_id: int) -> IncomingInspection:
        """完成检验"""
        inspection = self.db.query(IncomingInspection).get(inspection_id)
        if inspection:
            inspection.status = InspectionStatus.COMPLETED
        return inspection


class ProcessInspectionService:
    """过程检验服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_inspection(
        self,
        inspection_no: str,
        product_id: int,
        quantity: Decimal,
        production_order_id: Optional[int] = None,
        work_order_id: Optional[int] = None,
        process_id: Optional[int] = None,
        batch_no: Optional[str] = None,
        **kwargs
    ) -> ProcessInspection:
        """创建过程检验单"""
        inspection = ProcessInspection(
            inspection_no=inspection_no,
            product_id=product_id,
            quantity=quantity,
            production_order_id=production_order_id,
            work_order_id=work_order_id,
            process_id=process_id,
            batch_no=batch_no,
            **kwargs
        )
        self.db.add(inspection)
        self.db.flush()
        return inspection

    def complete_inspection(self, inspection_id: int, inspector_id: int) -> ProcessInspection:
        """完成过程检验"""
        inspection = self.db.query(ProcessInspection).get(inspection_id)
        if inspection:
            inspection.status = InspectionStatus.COMPLETED
            inspection.inspector_id = inspector_id
            inspection.inspection_date = datetime.now()

            # 更新统计
            items = self.db.query(ProcessInspectionItem).filter(
                ProcessInspectionItem.inspection_id == inspection_id
            ).all()

            qualified_count = sum(1 for item in items if item.is_qualified)
            inspection.qualified_quantity = Decimal(str(qualified_count))
            inspection.rejected_quantity = Decimal(str(len(items) - qualified_count))

            if inspection.rejected_quantity > 0:
                inspection.inspection_result = InspectionResult.UNQUALIFIED
            else:
                inspection.inspection_result = InspectionResult.QUALIFIED

        return inspection


class OutgoingInspectionService:
    """出货检验服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_inspection(
        self,
        inspection_no: str,
        customer_id: int,
        product_id: int,
        quantity: Decimal,
        delivery_order_id: Optional[int] = None,
        sales_order_id: Optional[int] = None,
        batch_no: Optional[str] = None,
        **kwargs
    ) -> OutgoingInspection:
        """创建出货检验单"""
        inspection = OutgoingInspection(
            inspection_no=inspection_no,
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            delivery_order_id=delivery_order_id,
            sales_order_id=sales_order_id,
            batch_no=batch_no,
            **kwargs
        )
        self.db.add(inspection)
        self.db.flush()
        return inspection

    def complete_inspection(
        self,
        inspection_id: int,
        inspector_id: int,
        certificate_no: Optional[str] = None
    ) -> OutgoingInspection:
        """完成出货检验"""
        inspection = self.db.query(OutgoingInspection).get(inspection_id)
        if inspection:
            inspection.status = InspectionStatus.COMPLETED
            inspection.inspector_id = inspector_id
            inspection.inspection_date = datetime.now()
            inspection.certificate_no = certificate_no

            # 更新统计
            items = self.db.query(OutgoingInspectionItem).filter(
                OutgoingInspectionItem.inspection_id == inspection_id
            ).all()

            qualified_count = sum(1 for item in items if item.is_qualified)
            inspection.qualified_quantity = Decimal(str(qualified_count))
            inspection.rejected_quantity = Decimal(str(len(items) - qualified_count))

            if inspection.rejected_quantity > 0:
                inspection.inspection_result = InspectionResult.UNQUALIFIED
            else:
                inspection.inspection_result = InspectionResult.QUALIFIED

        return inspection


class QualityTraceService:
    """质量追溯服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_trace(
        self,
        product_id: int,
        batch_no: Optional[str] = None,
        serial_no: Optional[str] = None,
        **kwargs
    ) -> QualityTrace:
        """创建质量追溯记录"""
        trace = QualityTrace(
            product_id=product_id,
            batch_no=batch_no,
            serial_no=serial_no,
            **kwargs
        )
        self.db.add(trace)
        self.db.flush()
        return trace

    def link_incoming_inspection(self, trace_id: int, inspection_id: int) -> QualityTrace:
        """关联来料检验"""
        trace = self.db.query(QualityTrace).get(trace_id)
        if trace:
            trace.incoming_inspection_id = inspection_id
        return trace

    def link_process_inspection(self, trace_id: int, inspection_id: int) -> QualityTrace:
        """关联过程检验"""
        trace = self.db.query(QualityTrace).get(trace_id)
        if trace:
            trace.process_inspection_id = inspection_id
        return trace

    def link_outgoing_inspection(self, trace_id: int, inspection_id: int) -> QualityTrace:
        """关联出货检验"""
        trace = self.db.query(QualityTrace).get(trace_id)
        if trace:
            trace.outgoing_inspection_id = inspection_id
        return trace

    def get_trace_by_batch(self, batch_no: str) -> List[QualityTrace]:
        """根据批号查询追溯记录"""
        return self.db.query(QualityTrace).filter(
            QualityTrace.batch_no == batch_no
        ).all()

    def get_trace_by_serial(self, serial_no: str) -> Optional[QualityTrace]:
        """根据序列号查询追溯记录"""
        return self.db.query(QualityTrace).filter(
            QualityTrace.serial_no == serial_no
        ).first()

    def get_product_quality_history(
        self,
        product_id: int,
        limit: int = 50
    ) -> List[QualityTrace]:
        """获取产品质量历史"""
        return self.db.query(QualityTrace).filter(
            QualityTrace.product_id == product_id
        ).order_by(QualityTrace.created_at.desc()).limit(limit).all()
