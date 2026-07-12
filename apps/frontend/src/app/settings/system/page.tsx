/**
 * 系统设置页面
 * @description 系统级配置，需要管理员权限
 */

"use client";

import { useState } from "react";
import {
  Settings,
  Users,
  Shield,
  Database,
  Bell,
  Palette,
  Globe,
  Save,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { usePermission } from "@/store/permission/PermissionContext";

export default function SystemSettingsPage() {
  const { hasPermission } = usePermission();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // 检查管理员权限
  const canManageSystem = hasPermission("system.config") || hasPermission("admin");

  if (!canManageSystem) {
    return (
      <div className="flex items-center justify-center py-12">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">权限不足</h3>
            <p className="text-sm text-muted-foreground">
              您需要管理员权限才能访问系统设置
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  /**
   * 保存设置
   */
  const handleSave = async () => {
    setSaving(true);
    try {
      // TODO: 调用保存设置API
      await new Promise((resolve) => setTimeout(resolve, 1000));
      toast.success("保存成功");
    } catch (error) {
      console.error("保存失败:", error);
      toast.error("保存失败");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">系统设置</h1>
        <p className="text-muted-foreground mt-1">
          配置系统参数和全局设置
        </p>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList>
          <TabsTrigger value="general">基本设置</TabsTrigger>
          <TabsTrigger value="security">安全设置</TabsTrigger>
          <TabsTrigger value="notification">通知设置</TabsTrigger>
          <TabsTrigger value="appearance">外观设置</TabsTrigger>
        </TabsList>

        {/* 基本设置 */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                系统信息
              </CardTitle>
              <CardDescription>
                配置系统的基本信息
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="system_name">系统名称</Label>
                <Input
                  id="system_name"
                  defaultValue="ERP管理系统"
                  placeholder="请输入系统名称"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="system_logo">系统Logo</Label>
                <Input
                  id="system_logo"
                  type="url"
                  placeholder="请输入Logo URL"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="system_description">系统描述</Label>
                <Textarea
                  id="system_description"
                  rows={3}
                  placeholder="请输入系统描述"
                  defaultValue="企业资源计划管理系统"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                区域设置
              </CardTitle>
              <CardDescription>
                配置系统的区域和语言相关设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="timezone">默认时区</Label>
                <select
                  id="timezone"
                  className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="Asia/Shanghai">UTC+8 北京/上海</option>
                  <option value="Asia/Tokyo">UTC+9 东京</option>
                  <option value="America/New_York">UTC-5 纽约</option>
                  <option value="America/Los_Angeles">UTC-8 洛杉矶</option>
                  <option value="Europe/London">UTC+0 伦敦</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="date_format">日期格式</Label>
                <select
                  id="date_format"
                  className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="YYYY-MM-DD">2024-01-01</option>
                  <option value="YYYY/MM/DD">2024/01/01</option>
                  <option value="DD/MM/YYYY">01/01/2024</option>
                  <option value="MM-DD-YYYY">01-01-2024</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="currency">默认货币</Label>
                <select
                  id="currency"
                  className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="CNY">人民币 (CNY ¥)</option>
                  <option value="USD">美元 (USD $)</option>
                  <option value="EUR">欧元 (EUR €)</option>
                  <option value="JPY">日元 (JPY ¥)</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 安全设置 */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                密码策略
              </CardTitle>
              <CardDescription>
                配置用户密码的安全要求
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="min_password_length">最小密码长度</Label>
                <Input
                  id="min_password_length"
                  type="number"
                  min={6}
                  max={32}
                  defaultValue={8}
                />
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium">要求大写字母</p>
                  <p className="text-sm text-muted-foreground">
                    密码必须包含至少一个大写字母
                  </p>
                </div>
                <Switch defaultChecked={false} />
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium">要求小写字母</p>
                  <p className="text-sm text-muted-foreground">
                    密码必须包含至少一个小写字母
                  </p>
                </div>
                <Switch defaultChecked={false} />
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium">要求数字</p>
                  <p className="text-sm text-muted-foreground">
                    密码必须包含至少一个数字
                  </p>
                </div>
                <Switch defaultChecked={false} />
              </div>

              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium">要求特殊字符</p>
                  <p className="text-sm text-muted-foreground">
                    密码必须包含至少一个特殊字符
                  </p>
                </div>
                <Switch defaultChecked={false} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>会话管理</CardTitle>
              <CardDescription>
                配置用户会话和登录相关设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="session_timeout">会话超时时间（分钟）</Label>
                <Input
                  id="session_timeout"
                  type="number"
                  min={5}
                  max={1440}
                  defaultValue={30}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_login_attempts">最大登录尝试次数</Label>
                <Input
                  id="max_login_attempts"
                  type="number"
                  min={3}
                  max={10}
                  defaultValue={5}
                />
              </div>

              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="font-medium">启用单点登录（SSO）</p>
                  <p className="text-sm text-muted-foreground">
                    允许用户通过第三方账号登录
                  </p>
                </div>
                <Switch defaultChecked={false} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 通知设置 */}
        <TabsContent value="notification" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                通知配置
              </CardTitle>
              <CardDescription>
                配置系统通知相关的设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium">启用邮件通知</p>
                  <p className="text-sm text-muted-foreground">
                    系统可以发送邮件通知
                  </p>
                </div>
                <Switch defaultChecked={true} />
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="font-medium">启用短信通知</p>
                  <p className="text-sm text-muted-foreground">
                    系统可以发送短信通知
                  </p>
                </div>
                <Switch defaultChecked={false} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email_from">发件人邮箱</Label>
                <Input
                  id="email_from"
                  type="email"
                  placeholder="noreply@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email_from_name">发件人名称</Label>
                <Input
                  id="email_from_name"
                  placeholder="ERP系统"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 外观设置 */}
        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                主题配置
              </CardTitle>
              <CardDescription>
                自定义系统的外观和主题
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>默认主题</Label>
                <div className="flex gap-3">
                  <button className="flex-1 p-4 border-2 rounded-lg hover:border-primary transition-colors">
                    <div className="w-full h-8 bg-white border rounded mb-2"></div>
                    <p className="text-sm font-medium">浅色</p>
                  </button>
                  <button className="flex-1 p-4 border-2 rounded-lg hover:border-primary transition-colors">
                    <div className="w-full h-8 bg-gray-900 rounded mb-2"></div>
                    <p className="text-sm font-medium">深色</p>
                  </button>
                  <button className="flex-1 p-4 border-2 rounded-lg hover:border-primary transition-colors">
                    <div className="w-full h-8 bg-gradient-to-r from-white to-gray-900 rounded mb-2"></div>
                    <p className="text-sm font-medium">跟随系统</p>
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="primary_color">主题色</Label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    id="primary_color"
                    className="w-12 h-10 rounded cursor-pointer"
                    defaultValue="#3b82f6"
                  />
                  <Input
                    type="text"
                    defaultValue="#3b82f6"
                    className="flex-1"
                    placeholder="#3b82f6"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* 保存按钮 */}
      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={saving}>
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              保存中...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              保存设置
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
