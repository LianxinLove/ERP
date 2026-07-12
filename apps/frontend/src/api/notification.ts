/**
 * 通知系统API调用
 * @description 封装所有通知相关的API请求
 */

import { apiClient } from "@/lib/api/client";
import {
  Notification,
  CreateNotification,
  UnreadCount,
  NotificationListResponse,
  NotificationPreference,
  UpdateNotificationPreference,
} from "@/types/notification";

/**
 * 通知API类
 */
class NotificationAPI {
  /**
   * 获取我的通知列表
   * @param params 查询参数
   * @returns 通知列表
   */
  async getMyNotifications(params?: {
    unread_only?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<NotificationListResponse> {
    const response = await apiClient.get<{ items: Notification[]; total: number; page: number; page_size: number }>(
      "/notifications/my",
      { params }
    );
    return response.data;
  }

  /**
   * 获取未读消息数
   * @returns 未读消息数
   */
  async getUnreadCount(): Promise<UnreadCount> {
    const response = await apiClient.get<UnreadCount>("/notifications/my/unread-count");
    return response.data;
  }

  /**
   * 标记通知为已读
   * @param notificationId 通知ID
   */
  async markAsRead(notificationId: number): Promise<void> {
    await apiClient.put(`/notifications/my/${notificationId}/read`);
  }

  /**
   * 标记所有通知为已读
   */
  async markAllAsRead(): Promise<{ message: string; count: number }> {
    const response = await apiClient.put<{ message: string; count: number }>("/notifications/my/read-all");
    return response.data;
  }

  /**
   * 删除通知
   * @param notificationId 通知ID
   */
  async deleteNotification(notificationId: number): Promise<void> {
    await apiClient.delete(`/notifications/my/${notificationId}`);
  }

  /**
   * 创建通知（需要权限）
   * @param data 创建通知数据
   */
  async createNotification(data: CreateNotification): Promise<Notification> {
    const response = await apiClient.post<Notification>("/notifications", data);
    return response.data;
  }

  /**
   * 获取我的通知偏好设置
   * @returns 通知偏好设置
   */
  async getMyPreference(): Promise<NotificationPreference> {
    const response = await apiClient.get<NotificationPreference>("/notifications/my/preference");
    return response.data;
  }

  /**
   * 更新通知偏好设置
   * @param data 更新数据
   */
  async updatePreference(data: UpdateNotificationPreference): Promise<NotificationPreference> {
    const response = await apiClient.put<NotificationPreference>("/notifications/my/preference", data);
    return response.data;
  }
}

// 导出单例
export const notificationAPI = new NotificationAPI();
