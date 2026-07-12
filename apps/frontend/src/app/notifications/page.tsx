/**
 * 通知页面
 * @description 显示用户的所有通知，支持筛选、标记已读、删除等操作
 */

"use client";

import { useState } from "react";
import { useNotifications } from "@/hooks/useNotifications";
import { NotificationItem } from "@/components/notification/NotificationItem";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCheck, Filter } from "lucide-react";
import { NotificationStatus } from "@/types/notification";

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState<"all" | "unread">("all");

  // 获取所有通知
  const {
    notifications: allNotifications,
    unreadCount,
    loading: allLoading,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refresh,
  } = useNotifications({
    autoFetchUnread: true,
    pollInterval: 30000,
  });

  // 获取未读通知
  const unreadNotifications = allNotifications.filter(
    (n) => n.status === NotificationStatus.SENT || n.status === NotificationStatus.PENDING
  );

  // 当前显示的通知列表
  const currentNotifications =
    activeTab === "unread" ? unreadNotifications : allNotifications;

  // 标记所有已读
  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
    refresh();
  };

  return (
    <div className="container max-w-4xl mx-auto py-8">
      {/* 页面头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">通知中心</h1>
          <p className="text-muted-foreground mt-1">
            查看和管理您的所有通知
          </p>
        </div>
        {unreadCount > 0 && (
          <Button variant="outline" onClick={handleMarkAllAsRead}>
            <CheckCheck className="h-4 w-4 mr-2" />
            全部已读
          </Button>
        )}
      </div>

      {/* 统计信息 */}
      <div className="flex items-center gap-4 mb-6">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">总通知数：</span>
          <Badge variant="secondary">{allNotifications.length}</Badge>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">未读消息：</span>
          <Badge variant="default">{unreadCount}</Badge>
        </div>
      </div>

      {/* 通知列表 */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "all" | "unread")}>
        <div className="flex items-center justify-between mb-4">
          <TabsList>
            <TabsTrigger value="all" className="relative">
              全部通知
              {allNotifications.length > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {allNotifications.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="unread" className="relative">
              未读消息
              {unreadCount > 0 && (
                <Badge variant="default" className="ml-2">
                  {unreadCount}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          <Button variant="outline" size="sm" onClick={refresh}>
            <Filter className="h-4 w-4 mr-2" />
            刷新
          </Button>
        </div>

        <TabsContent value="all" className="mt-0">
          <NotificationList
            notifications={currentNotifications}
            loading={allLoading}
            onMarkRead={markAsRead}
            onDelete={(id) => {
              deleteNotification(id);
              refresh();
            }}
          />
        </TabsContent>

        <TabsContent value="unread" className="mt-0">
          <NotificationList
            notifications={currentNotifications}
            loading={allLoading}
            onMarkRead={markAsRead}
            onDelete={(id) => {
              deleteNotification(id);
              refresh();
            }}
            emptyMessage="暂无未读消息"
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}

/**
 * 通知列表组件
 */
interface NotificationListProps {
  notifications: any[];
  loading: boolean;
  onMarkRead?: (id: number) => void;
  onDelete?: (id: number) => void;
  emptyMessage?: string;
}

function NotificationList({
  notifications,
  loading,
  onMarkRead,
  onDelete,
  emptyMessage = "暂无通知",
}: NotificationListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4">
          <svg
            className="w-8 h-8 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
        </div>
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onMarkRead={onMarkRead}
          onDelete={onDelete}
          showActions
        />
      ))}
    </div>
  );
}
