"""
采购管理 Pydantic Schemas

@description 采购模块的请求/响应模型
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 供应商相关 ============

class SupplierBase(BaseModel):
    """供应商基础模型"""
    code: str = Field(..., max_length=50, description="供应商编码")
    name: str = Field(..., max_length=200, description="供应商名称")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    tax_number: Optional[str] = Field(None, max_length=50, description="税号")
    bank_name: Optional[str] = Field(None, max_length=100, description="开户银行")
    bank_account: Optional[str] = Field(None, max_length=50, description="银行账号")
    credit_limit: Optional[Decimal] = Field(None, description="信用额度")
    payment_terms: Optional[int] = Field(None, description="付款条件（天数）")
    notes: Optional[str] = Field(None, description="备注")


class SupplierCreate(SupplierBase):
    """创建供应商"""
    status: Optional[str] = Field("active", description="状态")


class SupplierUpdate(BaseModel):
    """更新供应商"""
    name: Optional[str] = Field(None, max_length=200, description="供应商名称")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    address: Optional[str] = Field(None, description="地址")
    tax_number: Optional[str] = Field(None, max_length=50, description="税号")
    bank_name: Optional[str] = Field(None, max_length=100, description="开户银行")
    bank_account: Optional[str] = Field(None, max_length=50, description="银行账号")
    credit_limit: Optional[Decimal] = Field(None, description="信用额度")
    payment_terms: Optional[int] = Field(None, description="付款条件（天数）")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class SupplierResponse(SupplierBase):
    """供应商响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime


# ============ 采购申请明细相关 ============

class PurchaseRequestItemBase(BaseModel):
    """采购申请明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    estimated_price: Optional[Decimal] = Field(None, description="预估单价")
    estimated_amount: Optional[Decimal] = Field(None, description="预估金额")
    notes: Optional[str] = Field(None, description="备注")


class PurchaseRequestItemCreate(PurchaseRequestItemBase):
    """创建采购申请明细"""
    pass


class PurchaseRequestItemResponse(PurchaseRequestItemBase):
    """采购申请明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============ 采购申请相关 ============

class PurchaseRequestBase(BaseModel):
    """采购申请基础模型"""
    title: str = Field(..., max_length=200, description="申请标题")
    request_date: datetime = Field(..., description="需求日期")
    department_id: Optional[int] = Field(None, description="申请部门ID")
    reason: Optional[str] = Field(None, description="申请原因")


class PurchaseRequestCreate(PurchaseRequestBase):
    """创建采购申请"""
    items: List[PurchaseRequestItemCreate] = Field(..., description="明细列表")


class PurchaseRequestUpdate(BaseModel):
    """更新采购申请"""
    title: Optional[str] = Field(None, max_length=200, description="申请标题")
    request_date: Optional[datetime] = Field(None, description="需求日期")
    department_id: Optional[int] = Field(None, description="申请部门ID")
    reason: Optional[str] = Field(None, description="申请原因")
    items: Optional[List[PurchaseRequestItemCreate]] = Field(None, description="明细列表")
    status: Optional[str] = Field(None, description="状态")


class PurchaseRequestResponse(PurchaseRequestBase):
    """采购申请响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    request_no: str
    applicant_id: int
    total_amount: Optional[Decimal] = None
    status: str
    workflow_instance_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class PurchaseRequestDetail(PurchaseRequestResponse):
    """采购申请详情"""
    items: List[PurchaseRequestItemResponse] = []


# ============ 采购订单明细相关 ============

class PurchaseOrderItemBase(BaseModel):
    """采购订单明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    amount: Optional[Decimal] = Field(None, description="金额")
    tax_rate: Optional[Decimal] = Field(None, description="税率")
    notes: Optional[str] = Field(None, description="备注")


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """创建采购订单明细"""
    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    """采购订单明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    received_quantity: Optional[Decimal] = None


# ============ 采购订单相关 ============

class PurchaseOrderBase(BaseModel):
    """采购订单基础模型"""
    supplier_id: int = Field(..., description="供应商ID")
    order_date: datetime = Field(..., description="订单日期")
    expected_date: Optional[datetime] = Field(None, description="预计到货日期")
    tax_inclusive: Optional[bool] = Field(False, description="是否含税")
    payment_terms: Optional[int] = Field(None, description="付款条件（天数）")
    delivery_address: Optional[str] = Field(None, description="送货地址")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    notes: Optional[str] = Field(None, description="备注")


class PurchaseOrderCreate(PurchaseOrderBase):
    """创建采购订单"""
    request_id: Optional[int] = Field(None, description="采购申请ID")
    items: List[PurchaseOrderItemCreate] = Field(..., description="明细列表")


class PurchaseOrderUpdate(BaseModel):
    """更新采购订单"""
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    order_date: Optional[datetime] = Field(None, description="订单日期")
    expected_date: Optional[datetime] = Field(None, description="预计到货日期")
    tax_inclusive: Optional[bool] = Field(None, description="是否含税")
    payment_terms: Optional[int] = Field(None, description="付款条件（天数）")
    delivery_address: Optional[str] = Field(None, description="送货地址")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    notes: Optional[str] = Field(None, description="备注")
    items: Optional[List[PurchaseOrderItemCreate]] = Field(None, description="明细列表")
    status: Optional[str] = Field(None, description="状态")


class PurchaseOrderResponse(PurchaseOrderBase):
    """采购订单响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    request_id: Optional[int] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    status: str
    created_at: datetime
    updated_at: datetime


class PurchaseOrderDetail(PurchaseOrderResponse):
    """采购订单详情"""
    items: List[PurchaseOrderItemResponse] = []
    supplier: Optional[SupplierResponse] = None


# ============ 收货单明细相关 ============

class ReceiptOrderItemBase(BaseModel):
    """收货单明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="收货数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    amount: Optional[Decimal] = Field(None, description="金额")
    qualified_quantity: Optional[Decimal] = Field(None, description="合格数量")
    rejected_quantity: Optional[Decimal] = Field(None, description="不合格数量")
    batch_no: Optional[str] = Field(None, max_length=50, description="批号")
    production_date: Optional[datetime] = Field(None, description="生产日期")
    expiry_date: Optional[datetime] = Field(None, description="有效期")
    notes: Optional[str] = Field(None, description="备注")


class ReceiptOrderItemCreate(ReceiptOrderItemBase):
    """创建收货单明细"""
    order_item_id: Optional[int] = Field(None, description="采购订单明细ID")


class ReceiptOrderItemResponse(ReceiptOrderItemBase):
    """收货单明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_item_id: Optional[int] = None
    product_id: Optional[int] = None


# ============ 收货单相关 ============

class ReceiptOrderBase(BaseModel):
    """收货单基础模型"""
    order_id: Optional[int] = Field(None, description="采购订单ID")
    supplier_id: int = Field(..., description="供应商ID")
    receipt_date: datetime = Field(..., description="收货日期")
    warehouse_id: Optional[int] = Field(None, description="入库仓库ID")
    notes: Optional[str] = Field(None, description="备注")


class ReceiptOrderCreate(ReceiptOrderBase):
    """创建收货单"""
    items: List[ReceiptOrderItemCreate] = Field(..., description="明细列表")


class ReceiptOrderUpdate(BaseModel):
    """更新收货单"""
    warehouse_id: Optional[int] = Field(None, description="入库仓库ID")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class ReceiptOrderReceive(BaseModel):
    """收货确认"""
    warehouse_id: int = Field(..., description="入库仓库ID")
    notes: Optional[str] = Field(None, description="备注")


class ReceiptOrderInspect(BaseModel):
    """质检处理"""
    inspection_result: str = Field(..., description="质检结果（qualified/conditional/rejected）")
    items: List[dict] = Field(..., description="质检明细 [{item_id, qualified_quantity, rejected_quantity, reason}]")


class ReceiptOrderStock(BaseModel):
    """入库确认"""
    notes: Optional[str] = Field(None, description="备注")


class ReceiptOrderResponse(ReceiptOrderBase):
    """收货单响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    receipt_no: str
    total_amount: Optional[Decimal] = None
    total_quantity: Optional[Decimal] = None
    inspection_status: Optional[str] = None
    inspection_result: Optional[str] = None
    qualified_quantity: Optional[Decimal] = None
    rejected_quantity: Optional[Decimal] = None
    status: str
    received_at: Optional[datetime] = None
    inspected_at: Optional[datetime] = None
    stocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ReceiptOrderDetail(ReceiptOrderResponse):
    """收货单详情"""
    items: List[ReceiptOrderItemResponse] = []
    supplier: Optional[SupplierResponse] = None
