"""
健康检查端点

@description 提供系统健康检查接口
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    健康检查接口

    Returns:
        dict: 系统状态信息
    """
    return {
        "status": "ok",
        "service": "erp-backend",
        "version": "1.0.0",
    }
