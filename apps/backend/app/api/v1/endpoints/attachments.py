"""
附件管理API端点
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.permissions import require_permission
from app.models.user import User
from app.schemas.attachment import (
    AttachmentResponse,
    AttachmentUploadResponse,
    AttachmentDownloadUrl,
    AttachmentQuery,
    AttachmentCategoryResponse,
    AttachmentCategoryCreate,
    AttachmentCategoryUpdate,
)
from app.services.attachment import AttachmentService, AttachmentCategoryService

router = APIRouter(prefix="/attachments", tags=["附件管理"])


@router.post("/upload", summary="上传附件")
@require_permission("attachment.upload")
async def upload_attachment(
    request,
    file: UploadFile = File(...),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    上传附件

    支持关联到业务实体（如销售订单、采购申请等）
    """
    # 读取文件内容
    file_content = await file.read()

    # 获取上传IP
    upload_ip = request.client.host if request.client else None

    # 创建附件
    service = AttachmentService(db)
    attachment = service.create_attachment(
        original_name=file.filename,
        file_content=file_content,
        file_type=file.content_type,
        entity_type=entity_type,
        entity_id=entity_id,
        category_id=category_id,
        uploaded_by=current_user.id,
        description=description,
        upload_ip=upload_ip,
    )

    return AttachmentUploadResponse(
        attachment_id=attachment.id,
        file_name=attachment.file_name,
        file_size=attachment.file_size,
        file_type=attachment.file_type,
        message="上传成功",
    )


@router.get("/{attachment_id}", summary="获取附件信息")
@require_permission("attachment.read")
async def get_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取附件信息"""
    service = AttachmentService(db)
    attachment = service.get_attachment(attachment_id)

    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")

    return AttachmentResponse.model_validate(attachment)


@router.get("/{attachment_id}/download", summary="下载附件")
@require_permission("attachment.download")
async def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    下载附件

    返回文件流
    """
    service = AttachmentService(db)
    result = service.get_attachment_file(attachment_id)

    if not result:
        raise HTTPException(status_code=404, detail="附件不存在或已被删除")

    file_path, file_name = result

    # 增加下载次数
    service.increment_download_count(attachment_id)

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream",
    )


@router.get("/", summary="获取附件列表")
@require_permission("attachment.read")
async def get_attachments(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    uploaded_by: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取附件列表

    支持多种筛选条件和分页
    """
    service = AttachmentService(db)

    query = AttachmentQuery(
        entity_type=entity_type,
        entity_id=entity_id,
        category_id=category_id,
        uploaded_by=uploaded_by,
        status=status,
        file_type=file_type,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )

    attachments, total = service.get_attachments(query)

    return {
        "items": [AttachmentResponse.model_validate(a) for a in attachments],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.delete("/{attachment_id}", summary="删除附件")
@require_permission("attachment.delete")
async def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除附件（软删除）

    文件会被标记为删除状态，不会立即物理删除
    """
    service = AttachmentService(db)
    success = service.delete_attachment(attachment_id, deleted_by=current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="附件不存在")

    return {"message": "删除成功"}


# ===== 附件分类 =====

@router.post("/categories", summary="创建附件分类")
@require_permission("attachment.category.create")
async def create_category(
    data: AttachmentCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建附件分类"""
    service = AttachmentCategoryService(db)
    category = service.create_category(data)

    return AttachmentCategoryResponse.model_validate(category)


@router.get("/categories", summary="获取附件分类列表")
async def get_categories(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """获取附件分类列表"""
    service = AttachmentCategoryService(db)
    categories = service.get_categories(is_active=is_active)

    return {
        "items": [AttachmentCategoryResponse.model_validate(c) for c in categories]
    }


@router.get("/categories/{category_id}", summary="获取附件分类详情")
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """获取附件分类详情"""
    service = AttachmentCategoryService(db)
    category = service.get_category(category_id)

    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    return AttachmentCategoryResponse.model_validate(category)


@router.put("/categories/{category_id}", summary="更新附件分类")
@require_permission("attachment.category.update")
async def update_category(
    category_id: int,
    data: AttachmentCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新附件分类"""
    service = AttachmentCategoryService(db)
    category = service.update_category(category_id, data)

    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    return AttachmentCategoryResponse.model_validate(category)


@router.delete("/categories/{category_id}", summary="删除附件分类")
@require_permission("attachment.category.delete")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除附件分类"""
    service = AttachmentCategoryService(db)

    try:
        success = service.delete_category(category_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")

    return {"message": "删除成功"}
