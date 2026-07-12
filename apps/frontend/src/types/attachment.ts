/**
 * 附件管理类型定义
 * @description 附件相关的数据结构，用于前后端数据交互
 */

/**
 * 附件存储类型枚举
 */
export enum AttachmentStorageType {
  LOCAL = "local",
  OSS = "oss",
  DATABASE = "database",
}

/**
 * 附件状态枚举
 */
export enum AttachmentStatus {
  UPLOADING = "uploading",
  ACTIVE = "active",
  ARCHIVED = "archived",
  DELETED = "deleted",
}

/**
 * 附件响应数据结构
 */
export interface Attachment {
  id: number;
  file_name: string;
  original_name: string;
  file_path: string;
  file_size: number;
  file_type?: string;
  file_extension?: string;
  file_md5?: string;
  storage_type: AttachmentStorageType;
  entity_type?: string;
  entity_id?: number;
  category_id?: number;
  uploaded_by?: number;
  description?: string;
  download_count: number;
  status: AttachmentStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 附件上传响应
 */
export interface AttachmentUploadResponse {
  attachment_id: number;
  file_name: string;
  file_size: number;
  file_type?: string;
  upload_url?: string;
  message: string;
}

/**
 * 附件上传请求
 */
export interface AttachmentUploadRequest {
  file: File;
  entity_type?: string;
  entity_id?: number;
  category_id?: number;
  description?: string;
}

/**
 * 附件查询参数
 */
export interface AttachmentQuery {
  entity_type?: string;
  entity_id?: number;
  category_id?: number;
  uploaded_by?: number;
  status?: AttachmentStatus;
  file_type?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
}

/**
 * 附件列表响应
 */
export interface AttachmentListResponse {
  items: Attachment[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * 附件分类
 */
export interface AttachmentCategory {
  id: number;
  name: string;
  code: string;
  description?: string;
  allowed_types?: string;
  max_size?: number;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

/**
 * 附件分类创建请求
 */
export interface AttachmentCategoryCreate {
  name: string;
  code: string;
  description?: string;
  allowed_types?: string;
  max_size?: number;
  sort_order?: number;
}

/**
 * 附件分类更新请求
 */
export interface AttachmentCategoryUpdate {
  name?: string;
  description?: string;
  allowed_types?: string;
  max_size?: number;
  is_active?: boolean;
  sort_order?: number;
}

/**
 * 上传进度回调
 */
export type UploadProgressCallback = (progress: number) => void;
