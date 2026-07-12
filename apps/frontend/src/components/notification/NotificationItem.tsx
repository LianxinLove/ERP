/**
 * 通知项组件
 * @description 用于在列表中展示单个通知，常用于通知详情页面
 */

"use client";

import { useRouter } from "next/navigation";
import { Bell, Clock, Check, AlertCircle, Link2 } from "lucide-react";
import { Notification, NotificationType, NotificationPriority } from "@/types/notification";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";

interface NotificationItemProps {
  /** 通知数据 */
  notification: Notification;
  /** 标记已读回调 */
  onMarkRead?: (id: number) => void;
  /** 删除回调 */
  onDelete?: (id: number) => void;
  /** 点击回调 */
  onClick?: (notification: Notification) => void;
  /** 是否显示操作按钮 */
  showActions?: boolean;
}

/**
 * 通知项组件
 *
 * @features
 * - 显示通知完整信息
 * - 按类型和优先级显示不同样式
 * - 支持点击跳转
 * - 支持标记已读和删除操作
 *
 * @example
 * ```tsx
 * <NotificationItem
 *   notification={notification}
 *   onMarkRead={handleMarkRead}
 *   onDelete={handleDelete}
 *   onClick={handleClick}
 * />
 * ```
 */
export function NotificationItem({
  notification,
  onMarkRead,
  onDelete,
  onClick,
  showActions = true,
}: NotificationItemProps) {
  const router = useRouter();

  // 获取通知类型样式
  const getNotificationTypeStyle = (type: NotificationType) => {
    switch (type) {
      case NotificationType.WORKFLOW:
        return {
          bgColor: "bg-blue-50 dark:bg-blue-950",
          borderColor: "border-blue-200 dark:border-blue-800",
          textColor: "text-blue-700 dark:text-blue-400",
          label: "工作流",
        };
      case NotificationType.REMINDER:
        return {
          bgColor: "bg-amber-50 dark:bg-amber-950",
          borderColor: "border-amber-200 dark:border-amber-800",
          textColor: "text-amber-700 dark:text-amber-400",
          label: "提醒",
        };
      case NotificationType.ANNOUNCEMENT:
        return {
          bgColor: "bg-purple-50 dark:bg-purple-950",
          borderColor: "border-purple-200 dark:border-purple-800",
          textColor: "text-purple-700 dark:text-purple-400",
          label: "公告",
        };
      case NotificationType.MESSAGE:
        return {
          bgColor: "bg-green-50 dark:bg-green-950",
          borderColor: "border-green-200 dark:border-green-800",
          textColor: "text-green-700 dark:text-green-400",
          label: "私信",
        };
      default:
        return {
          bgColor: "bg-gray-50 dark:bg-gray-950",
          borderColor: "border-gray-200 dark:border-gray-800",
          textColor: "text-gray-700 dark:text-gray-400",
          label: "系统",
        };
    }
  };

  // 获取优先级信息
  const getPriorityInfo = (priority: NotificationPriority) => {
    switch (priority) {
      case NotificationPriority.URGENT:
        return { label: "紧急", color: "text-red-600", bgColor: "bg-red-100" };
      case NotificationPriority.HIGH:
        return { label: "重要", color: "text-orange-600", bgColor: "bg-orange-100" };
      case NotificationPriority.LOW:
        return { label: "低", color: "text-gray-600", bgColor: "bg-gray-100" };
      default:
        return null;
    }
  };

  // 处理点击
  const handleClick = () => {
    if (onClick) {
      onClick(notification);
    } else if (notification.link) {
      router.push(notification.link);
    }
  };

  // 处理标记已读
  const handleMarkRead = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onMarkRead) {
      onMarkRead(notification.id);
    }
  };

  // 处理删除
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(notification.id);
    }
  };

  const typeStyle = getNotificationTypeStyle(notification.type);
  const priorityInfo = getPriorityInfo(notification.priority);
  const isRead = notification.status === "read";

  return (
    <Card
      className={`transition-all hover:shadow-md ${
        !isRead ? typeStyle.bgColor + " " + typeStyle.borderColor : ""
      }`}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          {/* 左侧图标 */}
          <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            isRead ? "bg-gray-100 dark:bg-gray-800" : typeStyle.bgColor
          }`}>
            <Bell className={`h-5 w-5 ${isRead ? "text-gray-400" : typeStyle.textColor}`} />
          </div>

          {/* 内容 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              {/* 类型标签 */}
              <Badge variant="outline" className={typeStyle.textColor + " " + typeStyle.borderColor}>
                {typeStyle.label}
              </Badge>

              {/* 优先级标签 */}
              {priorityInfo && (
                <Badge className={priorityInfo.color + " " + priorityInfo.bgColor}>
                  {priorityInfo.label}
                </Badge>
              )}

              {/* 未读标识 */}
              {!isRead && (
                <Badge variant="default" className="h-1.5 w-1.5 rounded-full p-0" />
              )}
            </div>

            {/* 标题 */}
            <h4 className="font-semibold text-base mb-1">{notification.title}</h4>

            {/* 内容 */}
            {notification.content && (
              <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                {notification.content}
              </p>
            )}

            {/* 底部信息 */}
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{new Date(notification.created_at).toLocaleString("zh-CN")}</span>
              </div>
              {notification.link && (
                <div className="flex items-center gap-1">
                  <Link2 className="h-3 w-3" />
                  <span>点击查看详情</span>
                </div>
              )}
              {isRead && notification.read_at && (
                <div className="flex items-center gap-1">
                  <Check className="h-3 w-3" />
                  <span>已读于 {new Date(notification.read_at).toLocaleString("zh-CN")}</span>
                </div>
              )}
            </div>
          </div>

          {/* 操作按钮 */}
          {showActions && (
            <div className="flex flex-col gap-2">
              {!isRead && onMarkRead && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleMarkRead}
                  className="whitespace-nowrap"
                >
                  <Check className="h-4 w-4 mr-1" />
                  标记已读
                </Button>
              )}
              {onDelete && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDelete}
                  className="whitespace-nowrap text-destructive hover:text-destructive"
                >
                  删除
                </Button>
              )}
            </div>
          )}
        </div>

        {/* 点击区域 */}
        {notification.link && (
          <div
            className="absolute inset-0 cursor-pointer"
            onClick={handleClick}
          />
        )}
      </CardContent>
    </Card>
  );
}
