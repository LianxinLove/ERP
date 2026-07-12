/**
 * 附件管理API调用
 * @description 封装所有附件相关的API请求
 */

import { apiClient } from "@/lib/api/client";
import {
  Attachment,
  AttachmentUploadResponse,
  AttachmentQuery,
  AttachmentListResponse,
  AttachmentCategory,
  AttachmentCategoryCreate,
  AttachmentCategoryUpdate,
  UploadProgressCallback,
} from "@/types/attachment";

/**
 * 附件API类
 */
class AttachmentAPI {
  /**
   * 上传附件
   * @param data 上传数据
   * @param onProgress 上传进度回调
   * @returns 上传结果
   */
  async uploadAttachment(
    data: {
      file: File;
      entity_type?: string;
      entity_id?: number;
      category_id?: number;
      description?: string;
    },
    onProgress?: UploadProgressCallback
  ): Promise<AttachmentUploadResponse> {
    const formData = new FormData();
    formData.append("file", data.file);
    if (data.entity_type) formData.append("entity_type", data.entity_type);
    if (data.entity_id) formData.append("entity_id", String(data.entity_id));
    if (data.category_id) formData.append("category_id", String(data.category_id));
    if (data.description) formData.append("description", data.description);

    const response = await apiClient.post<AttachmentUploadResponse>(
      "/attachments/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
      }
    );

    return response.data;
  }

  /**
   * 获取附件信息
   * @param attachmentId 附件ID
   * @returns 附件信息
   */
  async getAttachment(attachmentId: number): Promise<Attachment> {
    const response = await apiClient.get<Attachment>(`/attachments/${attachmentId}`);
    return response.data;
  }

  /**
   * 获取附件下载URL
   * @param attachmentId 附件ID
   * @returns 下载URL
   */
  getDownloadUrl(attachmentId: number): string {
    return `${apiClient.defaults.baseURL}/attachments/${attachmentId}/download`;
  }

  /**
   * 获取附件列表
   * @param query 查询参数
   * @returns 附件列表
   */
  async getAttachments(query?: AttachmentQuery): Promise<AttachmentListResponse> {
    const response = await apiClient.get<AttachmentListResponse>("/attachments", {
      params: query,
    });
    return response.data;
  }

  /**
   * 删除附件
   * @param attachmentId 附件ID
   */
  async deleteAttachment(attachmentId: number): Promise<void> {
    await apiClient.delete(`/attachments/${attachmentId}`);
  }

  /**
   * 获取附件分类列表
   * @param isActive 是否只返回启用的分类
   * @returns 分类列表
   */
  async getCategories(isActive?: boolean): Promise<AttachmentCategory[]> {
    const response = await apiClient.get<{ items: AttachmentCategory[] }>(
      "/attachments/categories",
      { params: { is_active: isActive } }
    );
    return response.data.items;
  }

  /**
   * 获取附件分类详情
   * @param categoryId 分类ID
   * @returns 分类详情
   */
  async getCategory(categoryId: number): Promise<AttachmentCategory> {
    const response = await apiClient.get<AttachmentCategory>(
      `/attachments/categories/${categoryId}`
    );
    return response.data;
  }

  /**
   * 创建附件分类
   * @param data 创建数据
   * @returns 创建的分类
   */
  async createCategory(data: AttachmentCategoryCreate): Promise<AttachmentCategory> {
    const response = await apiClient.post<AttachmentCategory>(
      "/attachments/categories",
      data
    );
    return response.data;
  }

  /**
   * 更新附件分类
   * @param categoryId 分类ID
   * @param data 更新数据
   * @returns 更新后的分类
   */
  async updateCategory(
    categoryId: number,
    data: AttachmentCategoryUpdate
  ): Promise<AttachmentCategory> {
    const response = await apiClient.put<AttachmentCategory>(
      `/attachments/categories/${categoryId}`,
      data
    );
    return response.data;
  }

  /**
   * 删除附件分类
   * @param categoryId 分类ID
   */
  async deleteCategory(categoryId: number): Promise<void> {
    await apiClient.delete(`/attachments/categories/${categoryId}`);
  }
}

// 导出单例
export const attachmentAPI = new AttachmentAPI();
