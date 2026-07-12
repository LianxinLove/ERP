/**
 * 通知中心组件
 * @description 显示用户的通知列表，支持标记已读、删除等操作
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Bell,
  Check,
  CheckCheck,
  Trash2,
  Loader2,
  AlertCircle,
} from "lucide-react";
import { notificationAPI } from "@/api/notification";
import { Notification, NotificationType, NotificationPriority, NotificationStatus } from "@/types/notification";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

interface NotificationCenterProps {
  /** 是否显示未读消息角标 */
  showUnreadBadge?: boolean;
  /** 轮询间隔（毫秒） */
  pollInterval?: number;
  /** 自定义图标类名 */
  className?: string;
}

/**
 * 通知中心组件
 *
 * @features
 * - 显示未读消息数角标
 * - 下拉显示通知列表
 * - 支持标记单条/全部已读
 * - 支持删除通知
 * - 自动轮询更新未读数
 * - 按优先级显示不同样式
 *
 * @example
 * ```tsx
 * <NotificationCenter showUnreadBadge pollInterval={30000} />
 * ```
 */
export function NotificationCenter({
  showUnreadBadge = true,
  pollInterval = 30000,
  className = "",
}: NotificationCenterProps) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [markingAll, setMarkingAll] = useState(false);

  // 获取未读消息数
  const fetchUnreadCount = async () => {
    try {
      const count = await notificationAPI.getUnreadCount();
      setUnreadCount(count.total);
    } catch (error) {
      console.error("获取未读消息数失败:", error);
    }
  };

  // 获取通知列表
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await notificationAPI.getMyNotifications({
        page: 1,
        page_size: 20,
      });
      setNotifications(response.items);
    } catch (error) {
      console.error("获取通知列表失败:", error);
      toast.error("获取通知列表失败");
    } finally {
      setLoading(false);
    }
  };

  // 标记单条为已读
  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationAPI.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, status: NotificationStatus.READ, read_at: new Date().toISOString() } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (error) {
      console.error("标记已读失败:", error);
      toast.error("操作失败");
    }
  };

  // 标记所有为已读
  const handleMarkAllAsRead = async () => {
    setMarkingAll(true);
    try {
      const result = await notificationAPI.markAllAsRead();
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, status: NotificationStatus.READ, read_at: new Date().toISOString() }))
      );
      setUnreadCount(0);
      toast.success(result.message);
    } catch (error) {
      console.error("标记全部已读失败:", error);
      toast.error("操作失败");
    } finally {
      setMarkingAll(false);
    }
  };

  // 删除通知
  const handleDelete = async (id: number) => {
    try {
      await notificationAPI.deleteNotification(id);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      toast.success("删除成功");
    } catch (error) {
      console.error("删除失败:", error);
      toast.error("删除失败");
    }
  };

  // 点击通知
  const handleNotificationClick = (notification: Notification) => {
    if (notification.status !== "read") {
      handleMarkAsRead(notification.id);
    }
    if (notification.link) {
      router.push(notification.link);
    }
    setIsOpen(false);
  };

  // 获取通知类型颜色
  const getNotificationTypeColor = (type: NotificationType) => {
    switch (type) {
      case NotificationType.WORKFLOW:
        return "bg-blue-500/10 text-blue-700 border-blue-200";
      case NotificationType.REMINDER:
        return "bg-amber-500/10 text-amber-700 border-amber-200";
      case NotificationType.ANNOUNCEMENT:
        return "bg-purple-500/10 text-purple-700 border-purple-200";
      case NotificationType.MESSAGE:
        return "bg-green-500/10 text-green-700 border-green-200";
      default:
        return "bg-gray-500/10 text-gray-700 border-gray-200";
    }
  };

  // 获取优先级图标
  const getPriorityIcon = (priority: NotificationPriority) => {
    switch (priority) {
      case NotificationPriority.URGENT:
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case NotificationPriority.HIGH:
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default:
        return null;
    }
  };

  // 定时轮询
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, pollInterval);
    return () => clearInterval(interval);
  }, [pollInterval]);

  // 打开下拉时获取通知列表
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  return (
    <div className={`relative ${className}`}>
      {/* 通知图标按钮 */}
      <Button
        variant="ghost"
        size="icon"
        className="relative"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Bell className="h-5 w-5" />
        {showUnreadBadge && unreadCount > 0 && (
          <Badge
            variant="destructive"
            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
          >
            {unreadCount > 99 ? "99+" : unreadCount}
          </Badge>
        )}
      </Button>

      {/* 下拉面板 */}
      {isOpen && (
        <>
          {/* 遮罩 */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* 通知面板 */}
          <div className="absolute right-0 top-full z-50 w-80 md:w-96 bg-white rounded-lg shadow-lg border">
            {/* 头部 */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold">通知中心</h3>
              <div className="flex items-center gap-2">
                {unreadCount > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleMarkAllAsRead}
                    disabled={markingAll}
                  >
                    {markingAll ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCheck className="h-4 w-4" />
                    )}
                    <span className="ml-1">全部已读</span>
                  </Button>
                )}
              </div>
            </div>

            {/* 通知列表 */}
            <ScrollArea className="h-[400px]">
              {loading ? (
                <div className="flex items-center justify-center h-32">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
                  <Bell className="h-12 w-12 mb-2 opacity-50" />
                  <p>暂无通知</p>
                </div>
              ) : (
                <div className="divide-y">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        notification.status !== "read" ? "bg-blue-50/50" : ""
                      }`}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <div className="flex items-start gap-3">
                        {/* 优先级图标 */}
                        <div className="mt-1">
                          {getPriorityIcon(notification.priority)}
                        </div>

                        {/* 内容 */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span
                              className={`text-xs px-2 py-0.5 rounded border ${getNotificationTypeColor(notification.type)}`}
                            >
                              {notification.type}
                            </span>
                            {notification.status !== "read" && (
                              <Badge variant="default" className="h-1.5 w-1.5 rounded-full p-0" />
                            )}
                          </div>
                          <h4 className="font-medium text-sm truncate">{notification.title}</h4>
                          {notification.content && (
                            <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                              {notification.content}
                            </p>
                          )}
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(notification.created_at).toLocaleString("zh-CN")}
                          </p>
                        </div>

                        {/* 操作按钮 */}
                        <div className="flex flex-col gap-1">
                          {notification.status !== "read" && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMarkAsRead(notification.id);
                              }}
                            >
                              <Check className="h-3 w-3" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(notification.id);
                            }}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>
        </>
      )}
    </div>
  );
}
