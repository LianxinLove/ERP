"""
价格管理服务
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.price import (
    PriceList,
    PriceListLine,
    CustomerPrice,
    DiscountPolicy,
    PriceListStatus,
)
from app.schemas.price import GetProductPriceRequest, GetProductPriceResponse


class PriceService:
    """价格管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_product_price(
        self,
        product_id: int,
        customer_id: Optional[int] = None,
        quantity: Decimal = Decimal(1),
        currency: str = "CNY",
        date: Optional[datetime] = None,
    ) -> GetProductPriceResponse:
        """
        获取产品价格

        Args:
            product_id: 产品ID
            customer_id: 客户ID
            quantity: 数量
            currency: 币种
            date: 查询日期（默认当前日期）

        Returns:
            GetProductPriceResponse: 价格响应
        """
        if date is None:
            date = datetime.now()

        # 1. 查找客户专属价格（优先级最高）
        customer_price = self._get_customer_price(
            product_id, customer_id, quantity, date
        )

        if customer_price:
            unit_price = customer_price.unit_price
            price_source = "customer_price"
        else:
            # 2. 查找价格表价格
            price_line = self._get_price_list_price(
                product_id, customer_id, quantity, currency, date
            )

            if price_line:
                unit_price = price_line.unit_price
                price_source = f"price_list:{price_line.price_list.name}"
            else:
                # 3. 使用产品基础价格
                from app.models.inventory import Product

                product = (
                    self.db.query(Product)
                    .filter(Product.id == product_id)
                    .first()
                )

                if not product:
                    raise ValueError(f"产品 {product_id} 不存在")

                unit_price = product.selling_price or Decimal(0)
                price_source = "product_base_price"

        # 4. 计算折扣
        discounts = []
        discount_amount = Decimal(0)

        # 查找适用的折扣政策
        discount_policies = self._get_discount_policies(
            customer_id, quantity, unit_price * quantity, date
        )

        for policy in discount_policies:
            if policy.type == "percentage":
                policy_discount = unit_price * (policy.discount_value / 100)
                discount_amount += policy_discount
                discounts.append(f"{policy.name}: -{policy.discount_value}%")
            elif policy.type == "fixed":
                discount_amount += policy.discount_value
                discounts.append(f"{policy.name}: -{policy.discount_value}")

        # 计算最终价格
        final_price = unit_price - (discount_amount / quantity if quantity > 0 else Decimal(0))

        return GetProductPriceResponse(
            product_id=product_id,
            unit_price=unit_price,
            currency=currency,
            price_list=price_source,
            discount_policy=", ".join(discounts) if discounts else None,
            final_price=final_price,
            applicable_discounts=discounts,
        )

    def _get_customer_price(
        self, product_id: int, customer_id: Optional[int], quantity: Decimal, date: datetime
    ) -> Optional[CustomerPrice]:
        """获取客户专属价格"""
        if not customer_id:
            return None

        return (
            self.db.query(CustomerPrice)
            .filter(
                and_(
                    CustomerPrice.customer_id == customer_id,
                    CustomerPrice.product_id == product_id,
                ),
                or_(
                    CustomerPrice.valid_from == None,
                    CustomerPrice.valid_from <= date,
                ),
                or_(
                    CustomerPrice.valid_until == None,
                    CustomerPrice.valid_until >= date,
                ),
                or_(
                    CustomerPrice.min_quantity == None,
                    CustomerPrice.min_quantity <= quantity,
                ),
                or_(
                    CustomerPrice.max_quantity == None,
                    CustomerPrice.max_quantity >= quantity,
                ),
            )
            .order_by(CustomerPrice.priority.desc())
            .first()
        )

    def _get_price_list_price(
        self,
        product_id: int,
        customer_id: Optional[int],
        quantity: Decimal,
        currency: str,
        date: datetime,
    ) -> Optional[PriceListLine]:
        """从价格表获取价格"""
        # 查找适用价格表
        query = self.db.query(PriceList).filter(
            PriceList.currency == currency,
            PriceList.status == PriceListStatus.ACTIVE,
        )

        # 按优先级排序
        query = query.order_by(PriceList.priority.desc())

        price_lists = query.all()

        for price_list in price_lists:
            # 检查客户匹配
            if price_list.customer_id and price_list.customer_id != customer_id:
                continue

            if (
                price_list.customer_group
                and customer_id
                and not self._check_customer_in_group(customer_id, price_list.customer_group)
            ):
                continue

            # 检查日期
            if price_list.valid_from and price_list.valid_from > date:
                continue

            if price_list.valid_until and price_list.valid_until < date:
                continue

            # 查找产品明细
            line = (
                self.db.query(PriceListLine)
                .filter(
                    PriceListLine.price_list_id == price_list.id,
                    PriceListLine.product_id == product_id,
                )
                .first()
            )

            if line:
                # 检查数量范围
                if line.min_quantity and line.min_quantity > quantity:
                    continue

                if line.max_quantity and line.max_quantity < quantity:
                    continue

                return line

        return None

    def _check_customer_in_group(self, customer_id: int, group: str) -> bool:
        """检查客户是否在指定分组中"""
        # 这里可以根据实际的客户分组逻辑实现
        # 暂时返回True，表示通过
        return True

    def _get_discount_policies(
        self,
        customer_id: Optional[int],
        quantity: Decimal,
        amount: Decimal,
        date: datetime,
    ) -> List[DiscountPolicy]:
        """获取适用的折扣政策"""
        query = self.db.query(DiscountPolicy).filter(
            DiscountPolicy.is_active == True,
            or_(
                DiscountPolicy.valid_from == None,
                DiscountPolicy.valid_from <= date,
            ),
            or_(
                DiscountPolicy.valid_until == None,
                DiscountPolicy.valid_until >= date,
            ),
        )

        # 客户筛选
        if customer_id:
            query = query.filter(
                or_(
                    DiscountPolicy.customer_id == None,
                    DiscountPolicy.customer_id == customer_id,
                )
            )
        else:
            query = filter(DiscountPolicy.customer_id == None)

        # 金额筛选
        if amount:
            query = query.filter(
                or_(
                    DiscountPolicy.min_amount == None,
                    DiscountPolicy.min_amount <= amount,
                )
            )

        return query.all()
