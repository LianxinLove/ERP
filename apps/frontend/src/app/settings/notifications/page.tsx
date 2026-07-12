/**
 * 通知设置页面
 * @description 配置通知接收方式和偏好
 */

"use client";

import { useState, useEffect } from "react";
import {
  Bell,
  Mail,
  MessageSquare,
  Clock,
  Check,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { notificationAPI } from "@/api/notification";
import {
  NotificationPreference,
  NotificationType,
} from "@/types/notification";

export default function NotificationSettingsPage() {
  const [preference, setPreference] = useState<NotificationPreference | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // 获取通知偏好设置
  const fetchPreference = async () => {
    setLoading(true);
    try {
      const pref = await notificationAPI.getMyPreference();
      setPreference(pref);
    } catch (error) {
      console.error("获取通知设置失败:", error);
      toast.error("获取通知设置失败");
    } finally {
      setLoading(false);
    }
  };

  // 保存设置
  const handleSave = async () => {
    if (!preference) return;

    setSaving(true);
    try {
      await notificationAPI.updatePreference({
        inbox_enabled: preference.inbox_enabled,
        email_enabled: preference.email_enabled,
        sms_enabled: preference.sms_enabled,
        quiet_hours_start: preference.quiet_hours_start,
        quiet_hours_end: preference.quiet_hours_end,
      });
      toast.success("保存成功");
    } catch (error) {
      console.error("保存失败:", error);
      toast.error("保存失败");
    } finally {
      setSaving(false);
    }
  };

  // 初始化加载
  useEffect(() => {
    fetchPreference();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">通知设置</h1>
        <p className="text-muted-foreground mt-1">
          配置您接收通知的方式和时间
        </p>
      </div>

      {/* 通知渠道设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            通知渠道
          </CardTitle>
          <CardDescription>
            选择您希望接收通知的方式
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 站内消息 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <Bell className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">站内消息</p>
                <p className="text-sm text-muted-foreground">
                  在系统内显示通知消息
                </p>
              </div>
            </div>
            <Switch
              checked={preference?.inbox_enabled ?? false}
              onCheckedChange={(checked) =>
                setPreference((prev) => ({ ...prev!, inbox_enabled: checked }))
              }
            />
          </div>

          {/* 邮件通知 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
                <Mail className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <p className="font-medium">邮件通知</p>
                <p className="text-sm text-muted-foreground">
                  发送邮件到您的邮箱
                </p>
              </div>
            </div>
            <Switch
              checked={preference?.email_enabled ?? false}
              onCheckedChange={(checked) =>
                setPreference((prev) => ({ ...prev!, email_enabled: checked }))
              }
            />
          </div>

          {/* 短信通知 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
                <MessageSquare className="h-5 w-5 text-green-500" />
              </div>
              <div>
                <p className="font-medium">短信通知</p>
                <p className="text-sm text-muted-foreground">
                  发送短信到您的手机
                </p>
              </div>
            </div>
            <Switch
              checked={preference?.sms_enabled ?? false}
              onCheckedChange={(checked) =>
                setPreference((prev) => ({ ...prev!, sms_enabled: checked }))
              }
            />
          </div>
        </CardContent>
      </Card>

      {/* 免打扰设置 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            免打扰时间
          </CardTitle>
          <CardDescription>
            设置免打扰时段，在此期间不会收到通知
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>开始时间</Label>
              <input
                type="time"
                value={preference?.quiet_hours_start || ""}
                onChange={(e) =>
                  setPreference((prev) => ({
                    ...prev!,
                    quiet_hours_start: e.target.value,
                  }))
                }
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
            <div className="space-y-2">
              <Label>结束时间</Label>
              <input
                type="time"
                value={preference?.quiet_hours_end || ""}
                onChange={(e) =>
                  setPreference((prev) => ({
                    ...prev!,
                    quiet_hours_end: e.target.value,
                  }))
                }
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            设置后，在开始时间到结束时间之间将不会收到通知
          </p>
        </CardContent>
      </Card>

      {/* 通知类型说明 */}
      <Card>
        <CardHeader>
          <CardTitle>通知类型</CardTitle>
          <CardDescription>
            系统支持以下类型的通知
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <Badge variant="outline">系统</Badge>
              <div className="text-sm">
                <p className="font-medium">系统通知</p>
                <p className="text-muted-foreground">系统公告、维护通知等</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <Badge variant="outline">工作流</Badge>
              <div className="text-sm">
                <p className="font-medium">工作流通知</p>
                <p className="text-muted-foreground">审批、待办事项等</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <Badge variant="outline">提醒</Badge>
              <div className="text-sm">
                <p className="font-medium">提醒通知</p>
                <p className="text-muted-foreground">日程、任务提醒等</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 border rounded-lg">
              <Badge variant="outline">公告</Badge>
              <div className="text-sm">
                <p className="font-medium">公告通知</p>
                <p className="text-muted-foreground">公司公告、通知等</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 保存按钮 */}
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={fetchPreference}>
          重置
        </Button>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              保存中...
            </>
          ) : (
            <>
              <Check className="h-4 w-4 mr-2" />
              保存设置
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
