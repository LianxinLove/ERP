"""
编码规则API端点
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.number_rule import (
    NumberRuleResponse,
    NumberRuleCreate,
    NumberRuleUpdate,
    GenerateNumberRequest,
    GenerateNumberResponse,
)
from app.services.number_rule import NumberRuleService

router = APIRouter(prefix="/number-rules", tags=["编码规则"])


@router.post("/", summary="创建编码规则")
@require_permission("system.number_rule.create")
async def create_rule(
    data: NumberRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建编码规则"""
    service = NumberRuleService(db)

    # 检查编码是否已存在
    existing = service.get_rule(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="规则编码已存在")

    rule = service.create_rule(data)

    return NumberRuleResponse.model_validate(rule)


@router.get("/", summary="获取编码规则列表")
@require_permission("system.number_rule.read")
async def get_rules(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取编码规则列表"""
    service = NumberRuleService(db)
    rules = service.get_rules(is_active=is_active)

    return {
        "items": [NumberRuleResponse.model_validate(r) for r in rules]
    }


@router.get("/{code}", summary="获取编码规则详情")
@require_permission("system.number_rule.read")
async def get_rule(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取编码规则详情"""
    service = NumberRuleService(db)
    rule = service.get_rule(code)

    if not rule:
        raise HTTPException(status_code=404, detail="编码规则不存在")

    return NumberRuleResponse.model_validate(rule)


@router.put("/{code}", summary="更新编码规则")
@require_permission("system.number_rule.update")
async def update_rule(
    code: str,
    data: NumberRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新编码规则"""
    service = NumberRuleService(db)
    rule = service.update_rule(code, data)

    if not rule:
        raise HTTPException(status_code=404, detail="编码规则不存在")

    return NumberRuleResponse.model_validate(rule)


@router.delete("/{code}", summary="删除编码规则")
@require_permission("system.number_rule.delete")
async def delete_rule(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除编码规则（软删除）"""
    service = NumberRuleService(db)
    success = service.delete_rule(code)

    if not success:
        raise HTTPException(status_code=404, detail="编码规则不存在")

    return {"message": "删除成功"}


@router.post("/generate", summary="生成编号")
@require_permission("system.number_rule.generate")
async def generate_number(
    data: GenerateNumberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    生成编号

    支持预览模式，预览时不会实际占用编号
    """
    service = NumberRuleService(db)

    try:
        number = service.generate_number(
            rule_code=data.rule_code,
            preview=data.preview,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return GenerateNumberResponse(
        number=number,
        rule_code=data.rule_code,
        is_preview=data.preview,
    )
