"""
发票管理 Pydantic Schemas

@description 发票模块的请求/响应模型
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============ 销售发票明细相关 ============

class SalesInvoiceItemBase(BaseModel):
    """销售发票明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    amount: Optional[Decimal] = Field(None, description="金额")
    tax_rate: Optional[Decimal] = Field(None, description="税率")
    tax_amount: Optional[Decimal] = Field(None, description="税额")


class SalesInvoiceItemCreate(SalesInvoiceItemBase):
    """创建销售发票明细"""
    pass


class SalesInvoiceItemResponse(SalesInvoiceItemBase):
    """销售发票明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============ 销售发票相关 ============

class SalesInvoiceBase(BaseModel):
    """销售发票基础模型"""
    order_id: Optional[int] = Field(None, description="关联订单ID")
    customer_id: int = Field(..., description="客户ID")
    invoice_date: datetime = Field(..., description="开票日期")
    invoice_type: Optional[str] = Field("vat_electronic", description="发票类型")
    total_amount: Optional[Decimal] = Field(None, description="总金额（不含税）")
    tax_amount: Optional[Decimal] = Field(None, description="税额")
    total_amount_with_tax: Optional[Decimal] = Field(None, description="价税合计")
    buyer_name: Optional[str] = Field(None, max_length=200, description="购方名称")
    buyer_tax_no: Optional[str] = Field(None, max_length=50, description="购方税号")
    buyer_address_phone: Optional[str] = Field(None, max_length=200, description="购方地址电话")
    buyer_bank_account: Optional[str] = Field(None, max_length=200, description="购方开户行及账号")
    seller_name: Optional[str] = Field(None, max_length=200, description="销方名称")
    seller_tax_no: Optional[str] = Field(None, max_length=50, description="销方税号")
    seller_address_phone: Optional[str] = Field(None, max_length=200, description="销方地址电话")
    seller_bank_account: Optional[str] = Field(None, max_length=200, description="销方开户行及账号")
    remarks: Optional[str] = Field(None, description="备注")


class SalesInvoiceCreate(SalesInvoiceBase):
    """创建销售发票"""
    invoice_code: Optional[str] = Field(None, max_length=50, description="发票代码")
    items: List[SalesInvoiceItemCreate] = Field(..., description="明细列表")


class SalesInvoiceUpdate(BaseModel):
    """更新销售发票"""
    invoice_date: Optional[datetime] = Field(None, description="开票日期")
    total_amount: Optional[Decimal] = Field(None, description="总金额（不含税）")
    tax_amount: Optional[Decimal] = Field(None, description="税额")
    total_amount_with_tax: Optional[Decimal] = Field(None, description="价税合计")
    buyer_name: Optional[str] = Field(None, max_length=200, description="购方名称")
    buyer_tax_no: Optional[str] = Field(None, max_length=50, description="购方税号")
    buyer_address_phone: Optional[str] = Field(None, max_length=200, description="购方地址电话")
    buyer_bank_account: Optional[str] = Field(None, max_length=200, description="购方开户行及账号")
    seller_name: Optional[str] = Field(None, max_length=200, description="销方名称")
    seller_tax_no: Optional[str] = Field(None, max_length=50, description="销方税号")
    seller_address_phone: Optional[str] = Field(None, max_length=200, description="销方地址电话")
    seller_bank_account: Optional[str] = Field(None, max_length=200, description="销方开户行及账号")
    remarks: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class SalesInvoiceIssue(BaseModel):
    """发票开具"""
    invoice_no: str = Field(..., max_length=50, description="发票号码")
    invoice_code: Optional[str] = Field(None, max_length=50, description="发票代码")
    pdf_url: Optional[str] = Field(None, max_length=500, description="发票PDF地址")


class SalesInvoiceSend(BaseModel):
    """发票发送"""
    send_method: str = Field(..., description="发送方式（email/paper）")
    send_to: Optional[str] = Field(None, description="接收人")
    notes: Optional[str] = Field(None, description="备注")


class SalesInvoiceVerify(BaseModel):
    """发票认证"""
    verification_result: str = Field(..., description="认证结果")
    notes: Optional[str] = Field(None, description="备注")


class SalesInvoiceResponse(SalesInvoiceBase):
    """销售发票响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_no: str
    invoice_code: Optional[str] = None
    status: str
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SalesInvoiceDetail(SalesInvoiceResponse):
    """销售发票详情"""
    items: List[SalesInvoiceItemResponse] = []


# ============ 采购发票明细相关 ============

class PurchaseInvoiceItemBase(BaseModel):
    """采购发票明细基础模型"""
    product_code: Optional[str] = Field(None, max_length=50, description="产品编码")
    product_name: str = Field(..., max_length=200, description="产品名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    quantity: Decimal = Field(..., description="数量")
    unit_price: Optional[Decimal] = Field(None, description="单价")
    amount: Optional[Decimal] = Field(None, description="金额")
    tax_rate: Optional[Decimal] = Field(None, description="税率")
    tax_amount: Optional[Decimal] = Field(None, description="税额")


class PurchaseInvoiceItemCreate(PurchaseInvoiceItemBase):
    """创建采购发票明细"""
    pass


class PurchaseInvoiceItemResponse(PurchaseInvoiceItemBase):
    """采购发票明细响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int


# ============ 采购发票相关 ============

class PurchaseInvoiceBase(BaseModel):
    """采购发票基础模型"""
    order_id: Optional[int] = Field(None, description="关联订单ID")
    supplier_id: int = Field(..., description="供应商ID")
    invoice_date: datetime = Field(..., description="开票日期")
    invoice_type: Optional[str] = Field("vat_electronic", description="发票类型")
    total_amount: Optional[Decimal] = Field(None, description="总金额（不含税）")
    tax_amount: Optional[Decimal] = Field(None, description="税额")
    total_amount_with_tax: Optional[Decimal] = Field(None, description="价税合计")
    buyer_name: Optional[str] = Field(None, max_length=200, description="购方名称")
    buyer_tax_no: Optional[str] = Field(None, max_length=50, description="购方税号")
    seller_name: Optional[str] = Field(None, max_length=200, description="销方名称")
    seller_tax_no: Optional[str] = Field(None, max_length=50, description="销方税号")
    remarks: Optional[str] = Field(None, description="备注")


class PurchaseInvoiceCreate(PurchaseInvoiceBase):
    """创建采购发票"""
    invoice_code: Optional[str] = Field(None, max_length=50, description="发票代码")
    items: List[PurchaseInvoiceItemCreate] = Field(..., description="明细列表")


class PurchaseInvoiceUpdate(BaseModel):
    """更新采购发票"""
    invoice_date: Optional[datetime] = Field(None, description="开票日期")
    total_amount: Optional[Decimal] = Field(None, description="总金额（不含税）")
    tax_amount: Optional[Decimal] = Field(None, description="税额")
    total_amount_with_tax: Optional[Decimal] = Field(None, description="价税合计")
    buyer_name: Optional[str] = Field(None, max_length=200, description="购方名称")
    buyer_tax_no: Optional[str] = Field(None, max_length=50, description="购方税号")
    seller_name: Optional[str] = Field(None, max_length=200, description="销方名称")
    seller_tax_no: Optional[str] = Field(None, max_length=50, description="销方税号")
    remarks: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, description="状态")


class PurchaseInvoiceReceive(BaseModel):
    """发票接收"""
    invoice_no: str = Field(..., max_length=50, description="发票号码")
    invoice_code: Optional[str] = Field(None, max_length=50, description="发票代码")
    pdf_url: Optional[str] = Field(None, max_length=500, description="发票PDF地址")


class PurchaseInvoiceVerify(BaseModel):
    """发票认证"""
    verification_status: str = Field(..., description="认证状态")
    verification_result: Optional[str] = Field(None, description="认证结果")
    notes: Optional[str] = Field(None, description="备注")


class PurchaseInvoiceResponse(PurchaseInvoiceBase):
    """采购发票响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_no: str
    invoice_code: Optional[str] = None
    verification_status: Optional[str] = None
    verification_date: Optional[datetime] = None
    status: str
    pdf_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PurchaseInvoiceDetail(PurchaseInvoiceResponse):
    """采购发票详情"""
    items: List[PurchaseInvoiceItemResponse] = []


# ============ 发票勾稽相关 ============

class InvoiceMatchRequest(BaseModel):
    """发票勾稽请求"""
    invoice_id: int = Field(..., description="发票ID")
    order_id: Optional[int] = Field(None, description="订单ID")
    delivery_id: Optional[int] = Field(None, description="发货单ID（销售发票）")
    receipt_id: Optional[int] = Field(None, description="收货单ID（采购发票）")


class InvoiceMatchResponse(BaseModel):
    """发票勾稽响应"""
    matched: bool = Field(..., description="是否匹配")
    differences: List[dict] = Field(default_factory=list, description="差异列表")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
