"""
财务管理 Pydantic Schemas

@description 财务模块的数据验证和序列化模型

@schemas
- 科目相关
- 付款方式相关
- 应收账款相关
- 应付账款相关
- 收付款记录相关
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============ 科目相关 Schemas ============

AccountType = Literal["asset", "liability", "equity", "revenue", "expense"]


class AccountBase(BaseModel):
    """科目基础模型"""
    code: str = Field(..., max_length=50, description="科目编码")
    name: str = Field(..., max_length=200, description="科目名称")
    account_type: AccountType = Field(..., description="科目类型")
    parent_id: Optional[int] = Field(None, description="父科目ID")
    level: int = Field(1, description="级别")
    description: Optional[str] = Field(None, description="描述")


class AccountCreate(AccountBase):
    """创建科目"""
    is_active: bool = Field(True, description="是否启用")


class AccountUpdate(BaseModel):
    """更新科目"""
    name: Optional[str] = Field(None, max_length=200, description="科目名称")
    account_type: Optional[AccountType] = Field(None, description="科目类型")
    parent_id: Optional[int] = Field(None, description="父科目ID")
    description: Optional[str] = Field(None, description="描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class AccountResponse(AccountBase):
    """科目响应"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountTree(AccountResponse):
    """科目树形结构"""
    children: List['AccountTree'] = []

    model_config = ConfigDict(from_attributes=True)


# ============ 付款方式相关 Schemas ============

class PaymentMethodBase(BaseModel):
    """付款方式基础模型"""
    code: str = Field(..., max_length=50, description="编码")
    name: str = Field(..., max_length=100, description="名称")
    description: Optional[str] = Field(None, description="描述")


class PaymentMethodCreate(PaymentMethodBase):
    """创建付款方式"""
    is_active: bool = Field(True, description="是否启用")


class PaymentMethodUpdate(BaseModel):
    """更新付款方式"""
    name: Optional[str] = Field(None, max_length=100, description="名称")
    description: Optional[str] = Field(None, description="描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class PaymentMethodResponse(PaymentMethodBase):
    """付款方式响应"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ 应收账款相关 Schemas ============

ReceivableStatus = Literal["pending", "partial_paid", "paid", "overdue", "write_off"]


class ReceivableBase(BaseModel):
    """应收账款基础模型"""
    customer_id: int = Field(..., description="客户ID")
    sales_order_id: Optional[int] = Field(None, description="销售订单ID")
    amount: Decimal = Field(..., gt=0, description="金额")
    due_date: Optional[datetime] = Field(None, description="到期日期")
    notes: Optional[str] = Field(None, description="备注")


class ReceivableCreate(ReceivableBase):
    """创建应收账款"""
    pass


class ReceivableUpdate(BaseModel):
    """更新应收账款"""
    amount: Optional[Decimal] = Field(None, gt=0, description="金额")
    due_date: Optional[datetime] = Field(None, description="到期日期")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[ReceivableStatus] = Field(None, description="状态")


class ReceivableResponse(ReceivableBase):
    """应收账款响应"""
    id: int
    receivable_no: str
    paid_amount: Decimal
    remaining_amount: Decimal
    status: ReceivableStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReceivableDetail(ReceivableResponse):
    """应收账款详情"""
    customer_name: Optional[str] = None
    sales_order_no: Optional[str] = None
    payments: List['PaymentResponse'] = []

    model_config = ConfigDict(from_attributes=True)


# ============ 应付账款相关 Schemas ============

PayableStatus = Literal["pending", "partial_paid", "paid", "overdue"]


class PayableBase(BaseModel):
    """应付账款基础模型"""
    supplier_id: int = Field(..., description="供应商ID")
    purchase_order_id: Optional[int] = Field(None, description="采购订单ID")
    amount: Decimal = Field(..., gt=0, description="金额")
    due_date: Optional[datetime] = Field(None, description="到期日期")
    notes: Optional[str] = Field(None, description="备注")


class PayableCreate(PayableBase):
    """创建应付账款"""
    pass


class PayableUpdate(BaseModel):
    """更新应付账款"""
    amount: Optional[Decimal] = Field(None, gt=0, description="金额")
    due_date: Optional[datetime] = Field(None, description="到期日期")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[PayableStatus] = Field(None, description="状态")


class PayableResponse(PayableBase):
    """应付账款响应"""
    id: int
    payable_no: str
    paid_amount: Decimal
    remaining_amount: Decimal
    status: PayableStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PayableDetail(PayableResponse):
    """应付账款详情"""
    supplier_name: Optional[str] = None
    purchase_order_no: Optional[str] = None
    payments: List['PaymentResponse'] = []

    model_config = ConfigDict(from_attributes=True)


# ============ 收付款记录相关 Schemas ============

PaymentType = Literal["receipt", "payment"]
PaymentStatus = Literal["pending", "completed", "cancelled"]


class PaymentBase(BaseModel):
    """收付款记录基础模型"""
    payment_type: PaymentType = Field(..., description="类型")
    receivable_id: Optional[int] = Field(None, description="应收账款ID")
    payable_id: Optional[int] = Field(None, description="应付账款ID")
    amount: Decimal = Field(..., gt=0, description="金额")
    payment_method_id: Optional[int] = Field(None, description="付款方式ID")
    payment_date: datetime = Field(..., description="收付款日期")
    reference_no: Optional[str] = Field(None, max_length=100, description="参考号/支票号")
    notes: Optional[str] = Field(None, description="备注")

    @field_validator('payment_type')
    @classmethod
    def validate_payment_type(cls, v, info):
        """验证收付款类型与关联单据的一致性"""
        data = info.data if hasattr(info, 'data') else {}
        if v == "receipt" and data.get('payable_id'):
            raise ValueError("收款不能关联应付账款")
        if v == "payment" and data.get('receivable_id'):
            raise ValueError("付款不能关联应收账款")
        return v


class PaymentCreate(PaymentBase):
    """创建收付款记录"""
    status: PaymentStatus = Field("pending", description="状态")


class PaymentUpdate(BaseModel):
    """更新收付款记录"""
    amount: Optional[Decimal] = Field(None, gt=0, description="金额")
    payment_method_id: Optional[int] = Field(None, description="付款方式ID")
    payment_date: Optional[datetime] = Field(None, description="收付款日期")
    reference_no: Optional[str] = Field(None, max_length=100, description="参考号/支票号")
    notes: Optional[str] = Field(None, description="备注")
    status: Optional[PaymentStatus] = Field(None, description="状态")


class PaymentResponse(PaymentBase):
    """收付款记录响应"""
    id: int
    payment_no: str
    status: PaymentStatus
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentDetail(PaymentResponse):
    """收付款记录详情"""
    payment_method_name: Optional[str] = None
    customer_name: Optional[str] = None
    supplier_name: Optional[str] = None
    receivable_no: Optional[str] = None
    payable_no: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============ 统计相关 Schemas ============

class FinanceSummary(BaseModel):
    """财务汇总"""
    total_receivable: Decimal = Field(..., description="应收总额")
    total_paid_receivable: Decimal = Field(..., description="已收总额")
    total_remaining_receivable: Decimal = Field(..., description="剩余应收")
    overdue_receivable_count: int = Field(..., description="逾期应收笔数")
    total_payable: Decimal = Field(..., description="应付总额")
    total_paid_payable: Decimal = Field(..., description="已付总额")
    total_remaining_payable: Decimal = Field(..., description="剩余应付")
    overdue_payable_count: int = Field(..., description="逾期应付笔数")
    total_payment_in: Decimal = Field(..., description="收款总额")
    total_payment_out: Decimal = Field(..., description="付款总额")

    model_config = ConfigDict(from_attributes=True)


# 解决前向引用问题
AccountTree.model_rebuild()
ReceivableDetail.model_rebuild()
PayableDetail.model_rebuild()
