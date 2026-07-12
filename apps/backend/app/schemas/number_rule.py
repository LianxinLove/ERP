"""
编码规则Schema
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NumberRuleResponse(BaseModel):
    """编码规则响应"""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    prefix: Optional[str] = None
    date_format: Optional[str] = None
    sequence_length: int
    reset_type: str
    current_value: int
    is_active: bool
    example: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NumberRuleCreate(BaseModel):
    """创建编码规则"""
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    prefix: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)
    sequence_length: int = Field(default=4, ge=1, le=10)
    reset_type: str = Field(default="never", pattern="^(daily|monthly|yearly|never)$")


class NumberRuleUpdate(BaseModel):
    """更新编码规则"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    prefix: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)
    sequence_length: Optional[int] = Field(None, ge=1, le=10)
    reset_type: Optional[str] = Field(None, pattern="^(daily|monthly|yearly|never)$")
    is_active: Optional[bool] = None


class GenerateNumberRequest(BaseModel):
    """生成编号请求"""
    rule_code: str
    preview: bool = Field(default=False, description="是否只是预览，不实际占用编号")


class GenerateNumberResponse(BaseModel):
    """生成编号响应"""
    number: str
    rule_code: str
    is_preview: bool
