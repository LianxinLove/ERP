"""
编码规则服务
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.number_rule import NumberRule, NumberSequence
from app.schemas.number_rule import NumberRuleCreate, NumberRuleUpdate, GenerateNumberRequest


class NumberRuleService:
    """编码规则服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_rule(self, data: NumberRuleCreate) -> NumberRule:
        """
        创建编码规则

        Args:
            data: 规则数据

        Returns:
            NumberRule: 创建的规则对象
        """
        # 生成示例
        example = self._generate_example(
            data.prefix,
            data.date_format,
            data.sequence_length,
        )

        rule = NumberRule(
            code=data.code,
            name=data.name,
            description=data.description,
            prefix=data.prefix,
            date_format=data.date_format,
            sequence_length=data.sequence_length,
            reset_type=data.reset_type,
            current_value=0,
            is_active=True,
            example=example,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.db.add(rule)
        self.db.flush()

        return rule

    def get_rule(self, code: str) -> Optional[NumberRule]:
        """
        获取编码规则

        Args:
            code: 规则编码

        Returns:
            Optional[NumberRule]: 规则对象
        """
        return (
            self.db.query(NumberRule)
            .filter(
                and_(
                    NumberRule.code == code,
                    NumberRule.is_active == True,
                )
            )
            .first()
        )

    def get_rules(
        self,
        is_active: Optional[bool] = None,
    ) -> list:
        """
        获取编码规则列表

        Args:
            is_active: 是否只返回启用的规则

        Returns:
            list: 规则列表
        """
        q = self.db.query(NumberRule)

        if is_active is not None:
            q = q.filter(NumberRule.is_active == is_active)

        return q.order_by(NumberRule.code).all()

    def update_rule(
        self,
        code: str,
        data: NumberRuleUpdate,
    ) -> Optional[NumberRule]:
        """
        更新编码规则

        Args:
            code: 规则编码
            data: 更新数据

        Returns:
            Optional[NumberRule]: 更新后的规则对象
        """
        rule = self.get_rule(code)
        if not rule:
            return None

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        # 重新生成示例
        if any(k in update_data for k in ["prefix", "date_format", "sequence_length"]):
            rule.example = self._generate_example(
                rule.prefix,
                rule.date_format,
                rule.sequence_length,
            )

        rule.updated_at = datetime.now()

        return rule

    def delete_rule(self, code: str) -> bool:
        """
        删除编码规则（软删除）

        Args:
            code: 规则编码

        Returns:
            bool: 是否成功
        """
        rule = self.get_rule(code)
        if not rule:
            return False

        rule.is_active = False
        rule.updated_at = datetime.now()

        return True

    def generate_number(
        self,
        rule_code: str,
        preview: bool = False,
    ) -> str:
        """
        生成编号

        Args:
            rule_code: 规则编码
            preview: 是否只是预览，不实际占用编号

        Returns:
            str: 生成的编号
        """
        rule = self.get_rule(rule_code)
        if not rule:
            raise ValueError(f"编码规则 {rule_code} 不存在或未启用")

        # 生成日期部分
        date_part = self._get_date_part(rule.date_format)

        # 获取或创建流水号记录
        sequence = self._get_or_create_sequence(rule, date_part)

        # 递增流水号
        if not preview:
            sequence.current_value += 1
            sequence.updated_at = datetime.now()

        # 格式化流水号
        sequence_value = sequence.current_value if not preview else sequence.current_value + 1
        sequence_part = str(sequence_value).zfill(rule.sequence_length)

        # 组装编号
        parts = []
        if rule.prefix:
            parts.append(rule.prefix)
        if date_part:
            parts.append(date_part)
        parts.append(sequence_part)

        return "".join(parts)

    def _get_date_part(self, date_format: Optional[str]) -> str:
        """
        获取日期部分

        Args:
            date_format: 日期格式

        Returns:
            str: 格式化的日期字符串
        """
        if not date_format:
            return ""

        now = datetime.now()

        # 支持的格式占位符
        format_map = {
            "YYYY": now.strftime("%Y"),
            "YY": now.strftime("%y"),
            "MM": now.strftime("%m"),
            "DD": now.strftime("%d"),
        }

        result = date_format
        for key, value in format_map.items():
            result = result.replace(key, value)

        return result

    def _get_or_create_sequence(
        self,
        rule: NumberRule,
        date_part: str,
    ) -> NumberSequence:
        """
        获取或创建流水号记录

        Args:
            rule: 编码规则
            date_part: 日期部分

        Returns:
            NumberSequence: 流水号记录
        """
        # 生成日期键
        date_key = self._get_date_key(rule.reset_type, date_part)

        # 查找现有记录
        sequence = (
            self.db.query(NumberSequence)
            .filter(
                and_(
                    NumberSequence.rule_id == rule.id,
                    NumberSequence.date_key == date_key,
                )
            )
            .first()
        )

        # 如果不存在则创建
        if not sequence:
            sequence = NumberSequence(
                rule_id=rule.id,
                date_key=date_key,
                current_value=0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self.db.add(sequence)
            self.db.flush()

        return sequence

    def _get_date_key(self, reset_type: str, date_part: str) -> str:
        """
        获取日期键

        Args:
            reset_type: 重置类型
            date_part: 日期部分

        Returns:
            str: 日期键
        """
        now = datetime.now()

        if reset_type == "daily":
            return now.strftime("%Y%m%d")
        elif reset_type == "monthly":
            return now.strftime("%Y%m")
        elif reset_type == "yearly":
            return now.strftime("%Y")
        else:  # never
            return "permanent"

    def _generate_example(
        self,
        prefix: Optional[str],
        date_format: Optional[str],
        sequence_length: int,
    ) -> str:
        """
        生成示例编号

        Args:
            prefix: 前缀
            date_format: 日期格式
            sequence_length: 流水号长度

        Returns:
            str: 示例编号
        """
        parts = []
        if prefix:
            parts.append(prefix)

        # 生成示例日期部分
        if date_format:
            date_part = self._get_date_part(date_format)
            if date_part:
                parts.append(date_part)

        # 生成示例流水号
        sequence_part = "1".zfill(sequence_length)
        parts.append(sequence_part)

        return "".join(parts)
