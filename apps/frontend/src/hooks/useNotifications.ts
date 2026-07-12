/**
 * 通知管理 Hook
 * @description 封装通知相关的状态管理和操作逻辑
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { notificationAPI } from "@/api/notification";
import {
  Notification,
  UnreadCount,
  NotificationListResponse,
  NotificationStatus,
} from "@/types/notification";
import { toast } from "sonner";

interface UseNotificationsOptions {
  /** 是否自动获取未读数 */
  autoFetchUnread?: boolean;
  /** 轮询间隔（毫秒），0表示不轮询 */
  pollInterval?: number;
}

/**
 * 通知管理 Hook
 *
 * @features
 * - 管理通知列表状态
 * - 自动轮询未读消息数
 * - 提供标记已读、删除等操作方法
 * - 支持刷新和加载更多
 *
 * @example
 * ```tsx
 * const {
 *   notifications,
 *   unreadCount,
 *   loading,
 *   markAsRead,
 *   markAllAsRead,
 *   deleteNotification,
 *   refresh,
 *   loadMore
 * } = useNotifications({ autoFetchUnread: true, pollInterval: 30000 });
 * ```
 */
export function useNotifications(options: UseNotificationsOptions = {}) {
  const {
    autoFetchUnread = true,
    pollInterval = 0,
  } = options;

  // 状态
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [page, setPage] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);

  // 获取未读消息数
  const fetchUnreadCount = useCallback(async () => {
    try {
      const count = await notificationAPI.getUnreadCount();
      setUnreadCount(count.total);
      return count;
    } catch (error) {
      console.error("获取未读消息数失败:", error);
      return { total: 0, by_type: {} };
    }
  }, []);

  // 获取通知列表
  const fetchNotifications = useCallback(async (pageNum = 1, append = false) => {
    setLoading(true);
    try {
      const response: NotificationListResponse = await notificationAPI.getMyNotifications({
        page: pageNum,
        page_size: 20,
      });

      const newNotifications = response.items;

      if (append) {
        setNotifications((prev) => [...prev, ...newNotifications]);
      } else {
        setNotifications(newNotifications);
      }

      setTotal(response.total);
      setHasMore(pageNum * response.page_size < response.total);
      setPage(pageNum);

      return response;
    } catch (error) {
      console.error("获取通知列表失败:", error);
      toast.error("获取通知列表失败");
      return { items: [], total: 0, page: 1, page_size: 20 };
    } finally {
      setLoading(false);
    }
  }, []);

  // 刷新列表
  const refresh = useCallback(async () => {
    setPage(1);
    await fetchNotifications(1, false);
    await fetchUnreadCount();
  }, [fetchNotifications, fetchUnreadCount]);

  // 加载更多
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    await fetchNotifications(page + 1, true);
  }, [loading, hasMore, page, fetchNotifications]);

  // 标记已读
  const markAsRead = useCallback(async (notificationId: number) => {
    try {
      await notificationAPI.markAsRead(notificationId);

      // 更新本地状态
      setNotifications((prev) =>
        prev.map((n) =>
          n.id === notificationId
            ? { ...n, status: NotificationStatus.READ, read_at: new Date().toISOString() }
            : n
        )
      );

      // 更新未读数
      setUnreadCount((prev) => Math.max(0, prev - 1));

      return true;
    } catch (error) {
      console.error("标记已读失败:", error);
      toast.error("操作失败");
      return false;
    }
  }, []);

  // 标记所有已读
  const markAllAsRead = useCallback(async () => {
    try {
      const result = await notificationAPI.markAllAsRead();

      // 更新本地状态
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, status: NotificationStatus.READ, read_at: new Date().toISOString() }))
      );
      setUnreadCount(0);

      toast.success(result.message);
      return result;
    } catch (error) {
      console.error("标记全部已读失败:", error);
      toast.error("操作失败");
      return null;
    }
  }, []);

  // 删除通知
  const deleteNotification = useCallback(async (notificationId: number) => {
    try {
      await notificationAPI.deleteNotification(notificationId);

      // 更新本地状态
      setNotifications((prev) => {
        const notification = prev.find((n) => n.id === notificationId);
        const newCount = notification && notification.status !== "read" ? -1 : 0;
        setUnreadCount((prev) => Math.max(0, prev + newCount));
        return prev.filter((n) => n.id !== notificationId);
      });

      setTotal((prev) => Math.max(0, prev - 1));
      toast.success("删除成功");
      return true;
    } catch (error) {
      console.error("删除失败:", error);
      toast.error("删除失败");
      return false;
    }
  }, []);

  // 初始化：获取未读数和通知列表
  useEffect(() => {
    if (autoFetchUnread) {
      fetchUnreadCount();
    }
    fetchNotifications(1, false);
  }, [autoFetchUnread]);

  // 轮询未读数
  useEffect(() => {
    if (pollInterval > 0) {
      const interval = setInterval(fetchUnreadCount, pollInterval);
      return () => clearInterval(interval);
    }
  }, [pollInterval, fetchUnreadCount]);

  return {
    // 状态
    notifications,
    unreadCount,
    loading,
    hasMore,
    total,
    page,

    // 方法
    fetchUnreadCount,
    fetchNotifications,
    refresh,
    loadMore,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  };
}
