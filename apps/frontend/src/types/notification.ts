/**
 * 通知系统类型定义
 * @description 通知相关的数据结构，用于前后端数据交互
 */

/**
 * 通知类型枚举
 */
export enum NotificationType {
  SYSTEM = "system",           // 系统通知
  WORKFLOW = "workflow",       // 工作流通知
  REMINDER = "reminder",       // 提醒通知
  ANNOUNCEMENT = "announcement", // 公告通知
  MESSAGE = "message",         // 私信
}

/**
 * 通知优先级枚举
 */
export enum NotificationPriority {
  LOW = "low",       // 低
  NORMAL = "normal", // 普通
  HIGH = "high",     // 高
  URGENT = "urgent", // 紧急
}

/**
 * 通知状态枚举
 */
export enum NotificationStatus {
  PENDING = "pending", // 待发送
  SENT = "sent",       // 已发送
  READ = "read",       // 已读
  FAILED = "failed",   // 发送失败
  EXPIRED = "expired", // 已过期
}

/**
 * 通知响应数据结构
 */
export interface Notification {
  id: number;
  type: NotificationType;
  title: string;
  content?: string;
  link?: string;
  sender_id?: number;
  receiver_id: number;
  priority: NotificationPriority;
  status: NotificationStatus;
  read_at?: string;
  sent_at?: string;
  expire_at?: string;
  created_at: string;
}

/**
 * 创建通知请求
 */
export interface CreateNotification {
  receiver_id: number;
  type: NotificationType;
  title: string;
  content?: string;
  link?: string;
  priority?: NotificationPriority;
  expire_hours?: number;
}

/**
 * 未读消息数响应
 */
export interface UnreadCount {
  total: number;
  by_type: Record<string, number>;
}

/**
 * 通知列表响应
 */
export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * 通知偏好设置
 */
export interface NotificationPreference {
  id: number;
  user_id: number;
  notification_type?: string;
  inbox_enabled: boolean;
  email_enabled: boolean;
  sms_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  created_at: string;
  updated_at: string;
}

/**
 * 通知偏好设置更新请求
 */
export interface UpdateNotificationPreference {
  notification_type?: string;
  inbox_enabled?: boolean;
  email_enabled?: boolean;
  sms_enabled?: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
}
