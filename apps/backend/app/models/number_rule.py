"""
编码规则数据模型

@description 支持自动编号生成，支持前缀、日期、流水号等多种组合方式

@models
- NumberRule: 编码规则表
- NumberSequence: 编码流水号表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NumberRule(Base):
    """
    编码规则表

    @description 定义各类单据的编号生成规则

    @attributes
    - id: 规则ID
    - code: 规则编码
    - name: 规则名称
    - description: 描述
    - prefix: 前缀
    - date_format: 日期格式（如：YYYYMMDD）
    - sequence_length: 流水号长度
    - reset_type: 重置类型（daily/monthly/yearly/never）
    - current_value: 当前值
    - is_active: 是否启用
    - example: 示例
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "number_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="规则编码"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="规则名称"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(200), comment="描述"
    )

    # 编码规则配置
    prefix: Mapped[Optional[str]] = mapped_column(
        String(50), comment="前缀"
    )
    date_format: Mapped[Optional[str]] = mapped_column(
        String(20), comment="日期格式（如：YYYYMMDD）"
    )
    sequence_length: Mapped[int] = mapped_column(
        Integer, default=4, nullable=False, comment="流水号长度"
    )
    reset_type: Mapped[str] = mapped_column(
        String(20), default="never", nullable=False, comment="重置类型"
    )

    # 当前值
    current_value: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="当前值"
    )

    # 状态
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )

    # 示例（用于预览）
    example: Mapped[Optional[str]] = mapped_column(
        String(100), comment="示例"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )


class NumberSequence(Base):
    """
    编码流水号表

    @description 记录流水号的使用历史，支持按日期重置

    @attributes
    - id: 流水号ID
    - rule_id: 规则ID
    - date_key: 日期键（用于重置）
    - current_value: 当前值
    - created_at: 创建时间
    - updated_at: 更新时间
    """

    __tablename__ = "number_sequences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("number_rules.id"), nullable=False, comment="规则ID"
    )
    date_key: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, comment="日期键"
    )
    current_value: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, comment="当前值"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="更新时间"
    )

    # 关系
    rule = relationship("NumberRule")
