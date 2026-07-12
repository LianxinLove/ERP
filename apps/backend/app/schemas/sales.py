"""
销售管理 Pydantic Schemas

@description 销售模块的请求/响应模型
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 客户相关 ============

class CustomerBase(BaseModel):
    """客户基础模型"""
    code: str = Field(..., max_length=50, description="客户编码")
    name: str = Field(..., max_length=200, description="客户名称")
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


class CustomerCreate(CustomerBase):
    """创建客户"""
    status: Optional[str] = Field("active", description="状态")


class CustomerUpdate(BaseModel):
    """更新客户"""
    name: Optional[str] = Field(None, max_length=200, description="客户名称")
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


class CustomerResponse(CustomerBase):
    """客户响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime


# ============ 销售订单明细相关 ============

class SalesOrderItemBase(BaseModel):
    """销售订单明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    discount_rate: Optional[Decimal] = Field(None, description="折扣率(%)")
    amount: Optional[Decimal] = Field(None, description="金额")
    tax_rate: Optional[Decimal] = Field(None, description="税率")
    notes: Optional[str] = Field(None, description="备注")


class SalesOrderItemCreate(SalesOrderItemBase):
    """创建销售订单明细"""
    pass


class SalesOrderItemResponse(SalesOrderItemBase):
    """销售订单明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    shipped_quantity: Optional[Decimal] = None


# ============ 销售订单相关 ============

class SalesOrderBase(BaseModel):
    """销售订单基础模型"""
    customer_id: int = Field(..., description="客户ID")
    order_date: datetime = Field(..., description="订单日期")
    delivery_date: Optional[datetime] = Field(None, description="交货日期")
    tax_inclusive: Optional[bool] = Field(False, description="是否含税")
    discount_amount: Optional[Decimal] = Field(None, description="折扣金额")
    payment_terms: Optional[int] = Field(None, description="付款条件（天数）")
    delivery_address: Optional[str] = Field(None, description="送货地址")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    salesperson_id: Optional[int] = Field(None, description="销售员ID")
    notes: Optional[str] = Field(None, description="备注")


class SalesOrderCreate(SalesOrderBase):
    """创建销售订单"""
    items: List[SalesOrderItemCreate] = Field(..., description="明细列表")


class SalesOrderUpdate(BaseModel):
    """更新销售订单"""
    customer_id: Optional[int] = Field(None, description="客户ID")
    order_date: Optional[datetime] = Field(None, description="订单日期")
    delivery_date: Optional[datetime] = Field(None, description="交货日期")
    tax_inclusive: Optional[bool] = Field(None, description="是否含税")
    discount_amount: Optional[Decimal] = Field(None, description="折扣金额")
    payment_terms: Optional[int] = Field(None, description="付款条件（天数）")
    delivery_address: Optional[str] = Field(None, description="送货地址")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    salesperson_id: Optional[int] = Field(None, description="销售员ID")
    notes: Optional[str] = Field(None, description="备注")
    items: Optional[List[SalesOrderItemCreate]] = Field(None, description="明细列表")
    status: Optional[str] = Field(None, description="状态")


class SalesOrderResponse(SalesOrderBase):
    """销售订单响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_no: str
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    paid_amount: Optional[Decimal] = None
    status: str
    created_at: datetime
    updated_at: datetime


class SalesOrderDetail(SalesOrderResponse):
    """销售订单详情"""
    items: List[SalesOrderItemResponse] = []
    customer: Optional[CustomerResponse] = None


# ============ 销售退货明细相关 ============

class SalesReturnItemBase(BaseModel):
    """销售退货明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    amount: Optional[Decimal] = Field(None, description="金额")
    notes: Optional[str] = Field(None, description="备注")


class SalesReturnItemCreate(SalesReturnItemBase):
    """创建销售退货明细"""
    pass


class SalesReturnItemResponse(SalesReturnItemBase):
    """销售退货明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============ 销售退货相关 ============

class SalesReturnBase(BaseModel):
    """销售退货基础模型"""
    customer_id: int = Field(..., description="客户ID")
    return_date: datetime = Field(..., description="退货日期")
    order_id: Optional[int] = Field(None, description="原销售订单ID")
    reason: Optional[str] = Field(None, description="退货原因")
    notes: Optional[str] = Field(None, description="备注")


class SalesReturnCreate(SalesReturnBase):
    """创建销售退货"""
    items: List[SalesReturnItemCreate] = Field(..., description="明细列表")


class SalesReturnUpdate(BaseModel):
    """更新销售退货"""
    customer_id: Optional[int] = Field(None, description="客户ID")
    return_date: Optional[datetime] = Field(None, description="退货日期")
    order_id: Optional[int] = Field(None, description="原销售订单ID")
    reason: Optional[str] = Field(None, description="退货原因")
    notes: Optional[str] = Field(None, description="备注")
    items: Optional[List[SalesReturnItemCreate]] = Field(None, description="明细列表")
    status: Optional[str] = Field(None, description="状态")


class SalesReturnResponse(SalesReturnBase):
    """销售退货响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    return_no: str
    total_amount: Optional[Decimal] = None
    refund_amount: Optional[Decimal] = None
    status: str
    created_at: datetime
    updated_at: datetime


class SalesReturnDetail(SalesReturnResponse):
    """销售退货详情"""
    items: List[SalesReturnItemResponse] = []
    customer: Optional[CustomerResponse] = None


# ============ 发货单明细相关 ============

class DeliveryOrderItemBase(BaseModel):
    """发货单明细基础模型"""
    order_item_id: Optional[int] = Field(None, description="销售订单明细ID")
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    amount: Optional[Decimal] = Field(None, description="金额")
    batch_no: Optional[str] = Field(None, max_length=50, description="批号")
    notes: Optional[str] = Field(None, description="备注")


class DeliveryOrderItemCreate(DeliveryOrderItemBase):
    """创建发货单明细"""
    pass


class DeliveryOrderItemResponse(DeliveryOrderItemBase):
    """发货单明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============ 发货单相关 ============

class DeliveryOrderBase(BaseModel):
    """发货单基础模型"""
    order_id: Optional[int] = Field(None, description="销售订单ID")
    customer_id: int = Field(..., description="客户ID")
    delivery_date: datetime = Field(..., description="发货日期")
    warehouse_id: Optional[int] = Field(None, description="发货仓库ID")
    delivery_address: Optional[str] = Field(None, description="送货地址")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    logistics_company: Optional[str] = Field(None, max_length=100, description="物流公司")
    logistics_no: Optional[str] = Field(None, max_length=50, description="物流单号")
    logistics_fee: Optional[Decimal] = Field(None, description="物流费用")
    notes: Optional[str] = Field(None, description="备注")


class DeliveryOrderCreate(DeliveryOrderBase):
    """创建发货单"""
    items: List[DeliveryOrderItemCreate] = Field(..., description="明细列表")


class DeliveryOrderUpdate(BaseModel):
    """更新发货单"""
    delivery_address: Optional[str] = Field(None, description="送货地址")
    contact: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    logistics_company: Optional[str] = Field(None, max_length=100, description="物流公司")
    logistics_no: Optional[str] = Field(None, max_length=50, description="物流单号")
    logistics_fee: Optional[Decimal] = Field(None, description="物流费用")
    notes: Optional[str] = Field(None, description="备注")
    items: Optional[List[DeliveryOrderItemCreate]] = Field(None, description="明细列表")
    status: Optional[str] = Field(None, description="状态")


class DeliveryOrderResponse(DeliveryOrderBase):
    """发货单响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    delivery_no: str
    total_amount: Optional[Decimal] = None
    total_quantity: Optional[Decimal] = None
    status: str
    shipped_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    received_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DeliveryOrderDetail(DeliveryOrderResponse):
    """发货单详情"""
    items: List[DeliveryOrderItemResponse] = []
    customer: Optional[CustomerResponse] = None
    sales_order: Optional[SalesOrderResponse] = None


class DeliveryOrderShip(BaseModel):
    """发货确认"""
    logistics_company: Optional[str] = Field(None, max_length=100, description="物流公司")
    logistics_no: Optional[str] = Field(None, max_length=50, description="物流单号")
    notes: Optional[str] = Field(None, description="备注")


class DeliveryOrderReceive(BaseModel):
    """签收确认"""
    received_by: str = Field(..., max_length=100, description="签收人")
    notes: Optional[str] = Field(None, description="备注")
