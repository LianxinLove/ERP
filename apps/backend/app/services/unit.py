"""
多单位换算服务层

@description 产品多单位换算的业务逻辑

@services
- UnitService: 单位管理服务
- UnitConversionService: 单位换算服务
"""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.unit import (
    ProductUnit,
    UnitConversion,
    UnitType,
)
from app.models.inventory import Product
from app.schemas.unit import (
    ProductUnitCreate,
    ProductUnitUpdate,
    UnitConversionCreate,
    UnitConversionRequest,
)


class UnitService:
    """
    单位管理服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_unit(self, data: ProductUnitCreate) -> ProductUnit:
        """
        创建产品单位

        Args:
            data: 单位创建数据

        Returns:
            ProductUnit: 创建的单位

        Raises:
            BadRequestError: 单位编码已存在
            NotFoundError: 产品不存在
        """
        # 验证产品存在
        product_result = await self.db.execute(
            select(Product).where(Product.id == data.product_id)
        )
        if not product_result.scalar_one_or_none():
            raise NotFoundError("产品不存在")

        # 检查单位编码是否已存在
        result = await self.db.execute(
            select(ProductUnit).where(
                ProductUnit.product_id == data.product_id,
                ProductUnit.unit_code == data.unit_code,
                ProductUnit.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("该产品已存在相同编码的单位")

        # 如果是基本单位，检查该产品是否已有基本单位
        if data.is_base:
            existing_base_result = await self.db.execute(
                select(ProductUnit).where(
                    ProductUnit.product_id == data.product_id,
                    ProductUnit.is_base == True,
                    ProductUnit.is_deleted == False,
                )
            )
            if existing_base_result.scalar_one_or_none():
                raise BadRequestError("该产品已存在基本单位")

        # 创建单位
        now = datetime.now(timezone.utc)
        unit = ProductUnit(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        self.db.add(unit)

        # 如果不是基本单位且有换算率，创建换算关系
        if not data.is_base and data.conversion_rate:
            await self.db.flush()

            # 获取基本单位
            base_unit_result = await self.db.execute(
                select(ProductUnit).where(
                    ProductUnit.product_id == data.product_id,
                    ProductUnit.is_base == True,
                    ProductUnit.is_deleted == False,
                )
            )
            base_unit = base_unit_result.scalar_one_or_none()

            if base_unit:
                conversion = UnitConversion(
                    product_id=data.product_id,
                    from_unit_id=unit.id,
                    to_unit_id=base_unit.id,
                    conversion_rate=data.conversion_rate,
                    is_direct=True,
                    created_at=now,
                    updated_at=now,
                )
                self.db.add(conversion)

                # 反向换算
                reverse_conversion = UnitConversion(
                    product_id=data.product_id,
                    from_unit_id=base_unit.id,
                    to_unit_id=unit.id,
                    conversion_rate=Decimal(1) / data.conversion_rate,
                    is_direct=True,
                    created_at=now,
                    updated_at=now,
                )
                self.db.add(reverse_conversion)

        await self.db.commit()
        await self.db.refresh(unit)

        return unit

    async def get_units(
        self,
        product_id: Optional[int] = None,
        unit_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProductUnit]:
        """
        获取单位列表

        Args:
            product_id: 产品筛选
            unit_type: 单位类型筛选
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[ProductUnit]: 单位列表
        """
        query = select(ProductUnit).where(ProductUnit.is_deleted == False)

        if product_id:
            query = query.where(ProductUnit.product_id == product_id)

        if unit_type:
            query = query.where(ProductUnit.unit_type == unit_type)

        query = query.order_by(ProductUnit.is_base.desc(), ProductUnit.created_at.asc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_unit(self, unit_id: int) -> ProductUnit:
        """
        获取单位详情

        Args:
            unit_id: 单位ID

        Returns:
            ProductUnit: 单位详情

        Raises:
            NotFoundError: 单位不存在
        """
        result = await self.db.execute(
            select(ProductUnit).where(
                ProductUnit.id == unit_id,
                ProductUnit.is_deleted == False,
            )
        )
        unit = result.scalar_one_or_none()

        if not unit:
            raise NotFoundError("单位不存在")

        return unit

    async def update_unit(self, unit_id: int, data: ProductUnitUpdate) -> ProductUnit:
        """
        更新单位

        Args:
            unit_id: 单位ID
            data: 更新数据

        Returns:
            ProductUnit: 更新后的单位

        Raises:
            NotFoundError: 单位不存在
            BadRequestError: 更新数据不合法
        """
        unit = await self.get_unit(unit_id)

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(unit, field, value)

        unit.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(unit)

        return unit


class UnitConversionService:
    """
    单位换算服务类
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_conversion(self, data: UnitConversionCreate) -> UnitConversion:
        """
        创建单位换算关系

        Args:
            data: 换算关系创建数据

        Returns:
            UnitConversion: 创建的换算关系

        Raises:
            NotFoundError: 单位不存在
            BadRequestError: 换算关系已存在
        """
        # 验证单位存在
        unit_service = UnitService(self.db)
        from_unit = await unit_service.get_unit(data.from_unit_id)
        to_unit = await unit_service.get_unit(data.to_unit_id)

        if from_unit.product_id != data.product_id or to_unit.product_id != data.product_id:
            raise BadRequestError("单位和换算关系的产品ID不一致")

        # 检查换算关系是否已存在
        result = await self.db.execute(
            select(UnitConversion).where(
                UnitConversion.product_id == data.product_id,
                UnitConversion.from_unit_id == data.from_unit_id,
                UnitConversion.to_unit_id == data.to_unit_id,
                UnitConversion.is_deleted == False,
            )
        )
        if result.scalar_one_or_none():
            raise BadRequestError("换算关系已存在")

        # 创建换算关系
        now = datetime.now(timezone.utc)
        conversion = UnitConversion(
            **data.model_dump(),
            created_at=now,
            updated_at=now,
        )
        self.db.add(conversion)

        # 创建反向换算
        reverse_conversion = UnitConversion(
            product_id=data.product_id,
            from_unit_id=data.to_unit_id,
            to_unit_id=data.from_unit_id,
            conversion_rate=Decimal(1) / data.conversion_rate,
            is_direct=True,
            created_at=now,
            updated_at=now,
        )
        self.db.add(reverse_conversion)

        await self.db.commit()
        await self.db.refresh(conversion)

        return conversion

    async def get_conversions(
        self,
        product_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UnitConversion]:
        """
        获取换算关系列表

        Args:
            product_id: 产品筛选
            skip: 跳过条数
            limit: 限制条数

        Returns:
            List[UnitConversion]: 换算关系列表
        """
        query = select(UnitConversion).where(UnitConversion.is_deleted == False)

        if product_id:
            query = query.where(UnitConversion.product_id == product_id)

        query = query.order_by(UnitConversion.created_at.asc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def convert_quantity(self, data: UnitConversionRequest) -> dict:
        """
        单位数量换算

        Args:
            data: 换算请求数据

        Returns:
            dict: 换算结果

        Raises:
            NotFoundError: 单位不存在
            BadRequestError: 无法进行换算
        """
        # 获取单位信息
        unit_service = UnitService(self.db)
        from_unit = await unit_service.get_unit(data.from_unit_id)
        to_unit = await unit_service.get_unit(data.to_unit_id)

        if from_unit.product_id != data.product_id or to_unit.product_id != data.product_id:
            raise BadRequestError("单位和换算请求的产品ID不一致")

        # 如果是同一单位
        if from_unit.id == to_unit.id:
            return {
                "product_id": data.product_id,
                "from_unit_id": data.from_unit_id,
                "from_unit_code": from_unit.unit_code,
                "from_unit_name": from_unit.unit_name,
                "to_unit_id": data.to_unit_id,
                "to_unit_code": to_unit.unit_code,
                "to_unit_name": to_unit.unit_name,
                "original_quantity": data.quantity,
                "converted_quantity": data.quantity,
                "conversion_rate": Decimal(1),
            }

        # 查找换算关系
        result = await self.db.execute(
            select(UnitConversion).where(
                UnitConversion.product_id == data.product_id,
                UnitConversion.from_unit_id == data.from_unit_id,
                UnitConversion.to_unit_id == data.to_unit_id,
                UnitConversion.is_deleted == False,
            )
        )
        conversion = result.scalar_one_or_none()

        if not conversion:
            # 尝试通过基本单位间接换算
            converted_quantity = await self._convert_via_base_unit(
                data.product_id,
                data.from_unit_id,
                data.to_unit_id,
                data.quantity,
            )
            conversion_rate = converted_quantity / data.quantity if data.quantity != 0 else Decimal(0)
        else:
            converted_quantity = data.quantity * conversion.conversion_rate
            conversion_rate = conversion.conversion_rate

        # 应用精度
        precision = to_unit.precision or 2
        quantized = converted_quantity.quantize(Decimal(f"1e-{precision}"), rounding=ROUND_HALF_UP)

        return {
            "product_id": data.product_id,
            "from_unit_id": data.from_unit_id,
            "from_unit_code": from_unit.unit_code,
            "from_unit_name": from_unit.unit_name,
            "to_unit_id": data.to_unit_id,
            "to_unit_code": to_unit.unit_code,
            "to_unit_name": to_unit.unit_name,
            "original_quantity": data.quantity,
            "converted_quantity": quantized,
            "conversion_rate": conversion_rate,
        }

    async def _convert_via_base_unit(
        self, product_id: int, from_unit_id: int, to_unit_id: int, quantity: Decimal
    ) -> Decimal:
        """
        通过基本单位进行间接换算

        Args:
            product_id: 产品ID
            from_unit_id: 源单位ID
            to_unit_id: 目标单位ID
            quantity: 数量

        Returns:
            Decimal: 换算后的数量

        Raises:
            BadRequestError: 无法进行换算
        """
        # 获取基本单位
        result = await self.db.execute(
            select(ProductUnit).where(
                ProductUnit.product_id == product_id,
                ProductUnit.is_base == True,
                ProductUnit.is_deleted == False,
            )
        )
        base_unit = result.scalar_one_or_none()

        if not base_unit:
            raise BadRequestError("产品没有基本单位，无法进行换算")

        # 转换到基本单位
        if from_unit_id == base_unit.id:
            base_quantity = quantity
        else:
            # 查找从源单位到基本单位的换算
            from_result = await self.db.execute(
                select(UnitConversion).where(
                    UnitConversion.product_id == product_id,
                    UnitConversion.from_unit_id == from_unit_id,
                    UnitConversion.to_unit_id == base_unit.id,
                    UnitConversion.is_deleted == False,
                )
            )
            from_conversion = from_result.scalar_one_or_none()

            if not from_conversion:
                raise BadRequestError(f"无法找到从单位 {from_unit_id} 到基本单位的换算关系")

            base_quantity = quantity * from_conversion.conversion_rate

        # 从基本单位转换到目标单位
        if to_unit_id == base_unit.id:
            return base_quantity

        # 查找从基本单位到目标单位的换算
        to_result = await self.db.execute(
            select(UnitConversion).where(
                UnitConversion.product_id == product_id,
                UnitConversion.from_unit_id == base_unit.id,
                UnitConversion.to_unit_id == to_unit_id,
                UnitConversion.is_deleted == False,
            )
        )
        to_conversion = to_result.scalar_one_or_none()

        if not to_conversion:
            raise BadRequestError(f"无法找到从基本单位到单位 {to_unit_id} 的换算关系")

        return base_quantity * to_conversion.conversion_rate

    async def get_product_units_info(self, product_id: int) -> dict:
        """
        获取产品的完整单位信息

        Args:
            product_id: 产品ID

        Returns:
            dict: 产品单位信息
        """
        # 获取所有单位
        units_result = await self.db.execute(
            select(ProductUnit).where(
                ProductUnit.product_id == product_id,
                ProductUnit.is_deleted == False,
            ).order_by(ProductUnit.is_base.desc(), ProductUnit.created_at.asc())
        )
        units = units_result.scalars().all()

        # 获取所有换算关系
        conversions_result = await self.db.execute(
            select(UnitConversion).where(
                UnitConversion.product_id == product_id,
                UnitConversion.is_deleted == False,
            )
        )
        conversions = conversions_result.scalars().all()

        # 构建换算关系字典
        conversion_map = {}
        for conv in conversions:
            key = f"{conv.from_unit_id}_to_{conv.to_unit_id}"
            conversion_map[key] = {
                "rate": conv.conversion_rate,
                "is_direct": conv.is_direct,
            }

        return {
            "product_id": product_id,
            "units": [
                {
                    "id": u.id,
                    "unit_code": u.unit_code,
                    "unit_name": u.unit_name,
                    "unit_type": u.unit_type,
                    "is_base": u.is_base,
                    "conversion_rate": u.conversion_rate,
                    "precision": u.precision,
                }
                for u in units
            ],
            "conversions": conversion_map,
        }
