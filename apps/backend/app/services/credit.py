"""
客户信用控制服务
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from app.models.sales import Customer
from app.models.finance import Receivable, ReceivableStatus


class CreditControlService:
    """客户信用控制服务"""

    def __init__(self, db: Session):
        self.db = db

    def check_credit_limit(
        self,
        customer_id: int,
        order_amount: Decimal,
        strict: bool = False,
    ) -> dict:
        """
        检查客户信用额度

        Args:
            customer_id: 客户ID
            order_amount: 订单金额
            strict: 是否严格模式（严格模式下超额将阻止订单）

        Returns:
            dict: {
                "allowed": bool,  # 是否允许
                "credit_limit": Decimal,  # 信用额度
                "credit_used": Decimal,  # 已用额度
                "credit_available": Decimal,  # 可用额度
                "order_amount": Decimal,  # 订单金额
                "over_amount": Decimal,  # 超出金额
                "message": str,
            }
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        # 获取信用额度
        credit_limit = customer.credit_limit or Decimal(0)

        # 计算已用信用额度（未结清的应收账款）
        credit_used = self._calculate_credit_used(customer_id)

        # 可用额度
        credit_available = credit_limit - credit_used

        # 计算是否超出
        over_amount = order_amount - credit_available
        allowed = over_amount <= 0

        if not allowed and strict:
            return {
                "allowed": False,
                "credit_limit": credit_limit,
                "credit_used": credit_used,
                "credit_available": credit_available,
                "order_amount": order_amount,
                "over_amount": over_amount,
                "message": f"订单金额超出可用信用额度 {over_amount:.2f}",
            }
        elif not allowed:
            return {
                "allowed": True,
                "credit_limit": credit_limit,
                "credit_used": credit_used,
                "credit_available": credit_available,
                "order_amount": order_amount,
                "over_amount": over_amount,
                "message": f"警告：订单金额超出可用信用额度 {over_amount:.2f}",
                "warning": True,
            }
        else:
            return {
                "allowed": True,
                "credit_limit": credit_limit,
                "credit_used": credit_used,
                "credit_available": credit_available,
                "order_amount": order_amount,
                "over_amount": Decimal(0),
                "message": "信用额度充足",
            }

    def _calculate_credit_used(self, customer_id: int) -> Decimal:
        """
        计算已用信用额度

        Args:
            customer_id: 客户ID

        Returns:
            Decimal: 已用额度
        """
        from sqlalchemy import sum as sql_sum

        # 计算未结清的应收账款
        result = self.db.query(
            sql_sum(Receivable.remaining_amount)
        ).filter(
            Receivable.customer_id == customer_id,
            Receivable.status.in_([
                ReceivableStatus.PENDING,
                ReceivableStatus.PARTIAL_PAID,
            ]),
        )

        credit_used = result.scalar() or Decimal(0)

        # 更新客户的已用额度
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.credit_used = credit_used

        return credit_used

    def update_customer_credit(self, customer_id: int) -> dict:
        """
        更新客户信用使用情况

        Args:
            customer_id: 客户ID

        Returns:
            dict: 更新后的信用情况
        """
        credit_used = self._calculate_credit_used(customer_id)
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()

        if not customer:
            raise ValueError(f"客户 {customer_id} 不存在")

        credit_available = (customer.credit_limit or Decimal(0)) - credit_used

        return {
            "customer_id": customer_id,
            "credit_limit": customer.credit_limit,
            "credit_used": credit_used,
            "credit_available": credit_available,
            "utilization_rate": (
                (credit_used / customer.credit_limit * 100)
                if customer.credit_limit and customer.credit_limit > 0
                else 0
            ),
        }

    def get_overdue_customers(
        self,
        days: int = 30,
    ) -> list:
        """
        获取逾期客户列表

        Args:
            days: 逾期天数

        Returns:
            list: 逾期客户列表
        """
        from datetime import timedelta

        due_date_limit = datetime.now() - timedelta(days=days)

        # 查询逾期应收账款
        overdue_receivables = (
            self.db.query(Receivable)
            .filter(
                Receivable.status.in_([
                    ReceivableStatus.PENDING,
                    ReceivableStatus.PARTIAL_PAID,
                    ReceivableStatus.OVERDUE,
                ]),
                Receivable.due_date < due_date_limit,
            )
            .all()
        )

        # 按客户分组
        customer_overdue = {}
        for receivable in overdue_receivables:
            customer_id = receivable.customer_id
            if customer_id not in customer_overdue:
                customer_overdue[customer_id] = {
                    "customer_id": customer_id,
                    "overdue_count": 0,
                    "overdue_amount": Decimal(0),
                }

            customer_overdue[customer_id]["overdue_count"] += 1
            customer_overdue[customer_id]["overdue_amount"] += (
                receivable.remaining_amount
            )

        # 获取客户信息
        result = []
        for customer_id, data in customer_overdue.items():
            customer = (
                self.db.query(Customer).filter(Customer.id == customer_id).first()
            )
            if customer:
                result.append(
                    {
                        "customer_id": customer_id,
                        "customer_name": customer.name,
                        "customer_code": customer.code,
                        "overdue_count": data["overdue_count"],
                        "overdue_amount": data["overdue_amount"],
                        "credit_limit": customer.credit_limit,
                        "credit_used": customer.credit_used,
                    }
                )

        return result
