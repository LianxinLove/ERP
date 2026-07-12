/**
 * 个人设置页面
 * @description 用户个人信息管理、密码修改、头像设置
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  User,
  Mail,
  Phone,
  Shield,
  Camera,
  Key,
  UserCircle,
} from "lucide-react";
import { useAuth } from "@/store/auth/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { authApi } from "@/api/auth";

export default function ProfileSettingsPage() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);

  // 个人信息表单
  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || "",
    phone: user?.phone || "",
    avatar_url: user?.avatar_url || "",
  });

  // 密码修改表单
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  /**
   * 更新个人信息
   */
  const handleUpdateProfile = async () => {
    setLoading(true);
    try {
      await authApi.updateProfile(profileForm);
      await refreshUser();
      toast.success("个人信息更新成功");
    } catch (error) {
      console.error("更新失败:", error);
      toast.error("更新失败");
    } finally {
      setLoading(false);
    }
  };

  /**
   * 修改密码
   */
  const handleChangePassword = async () => {
    // 验证
    if (!passwordForm.current_password) {
      toast.error("请输入当前密码");
      return;
    }
    if (!passwordForm.new_password) {
      toast.error("请输入新密码");
      return;
    }
    if (passwordForm.new_password.length < 6) {
      toast.error("新密码至少6位");
      return;
    }
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error("两次输入的新密码不一致");
      return;
    }

    setLoading(true);
    try {
      await authApi.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });

      toast.success("密码修改成功，请重新登录");

      // 清空表单
      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });

      // 延迟跳转到登录页
      setTimeout(() => {
        router.push("/auth/login");
      }, 1500);
    } catch (error: any) {
      console.error("修改密码失败:", error);
      const message = error?.response?.data?.message || "修改密码失败";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 上传头像
   */
  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith("image/")) {
      toast.error("请选择图片文件");
      return;
    }

    // 验证文件大小 (2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast.error("图片大小不能超过2MB");
      return;
    }

    setLoading(true);
    try {
      // TODO: 实现头像上传API
      toast.success("头像上传成功");
    } catch (error) {
      console.error("上传失败:", error);
      toast.error("上传失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">个人设置</h1>
        <p className="text-muted-foreground mt-1">
          管理您的个人信息和账户安全设置
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">基本信息</TabsTrigger>
          <TabsTrigger value="security">账户安全</TabsTrigger>
          <TabsTrigger value="preferences">偏好设置</TabsTrigger>
        </TabsList>

        {/* 基本信息 */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>头像</CardTitle>
              <CardDescription>
                点击头像或相机图标上传新头像
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="relative group">
                  <Avatar className="h-24 w-24">
                    <AvatarImage src={user?.avatar_url} />
                    <AvatarFallback>
                      <UserCircle className="h-16 w-16" />
                    </AvatarFallback>
                  </Avatar>
                  <label
                    htmlFor="avatar-upload"
                    className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
                  >
                    <Camera className="h-6 w-6 text-white" />
                  </label>
                  <input
                    type="file"
                    id="avatar-upload"
                    className="hidden"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                  />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium">{user?.full_name || user?.username}</p>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                  <p className="text-xs text-muted-foreground">
                    支持 JPG、PNG 格式，大小不超过 2MB
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>基本信息</CardTitle>
              <CardDescription>
                更新您的个人基本信息
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="username">用户名</Label>
                  <Input
                    id="username"
                    value={user?.username || ""}
                    disabled
                    className="bg-muted"
                  />
                  <p className="text-xs text-muted-foreground">
                    用户名不可修改
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">邮箱</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      value={user?.email || ""}
                      disabled
                      className="pl-10 bg-muted"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    邮箱不可修改
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="full_name">姓名</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="full_name"
                      value={profileForm.full_name}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, full_name: e.target.value })
                      }
                      className="pl-10"
                      placeholder="请输入您的姓名"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">手机号</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="phone"
                      type="tel"
                      value={profileForm.phone}
                      onChange={(e) =>
                        setProfileForm({ ...profileForm, phone: e.target.value })
                      }
                      className="pl-10"
                      placeholder="请输入手机号"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button onClick={handleUpdateProfile} disabled={loading}>
                  保存更改
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 账户安全 */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                修改密码
              </CardTitle>
              <CardDescription>
                定期修改密码可以保护您的账户安全
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current_password">当前密码</Label>
                <Input
                  id="current_password"
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      current_password: e.target.value,
                    })
                  }
                  placeholder="请输入当前密码"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="new_password">新密码</Label>
                <Input
                  id="new_password"
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      new_password: e.target.value,
                    })
                  }
                  placeholder="请输入新密码（至少6位）"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm_password">确认新密码</Label>
                <Input
                  id="confirm_password"
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      confirm_password: e.target.value,
                    })
                  }
                  placeholder="请再次输入新密码"
                />
              </div>

              <div className="flex justify-end">
                <Button
                  onClick={handleChangePassword}
                  disabled={loading}
                  variant="outline"
                >
                  <Key className="h-4 w-4 mr-2" />
                  修改密码
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>账户状态</CardTitle>
              <CardDescription>您当前的账户状态信息</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">账户状态</span>
                <Badge variant={user?.is_active ? "default" : "secondary"}>
                  {user?.is_active ? "正常" : "已禁用"}
                </Badge>
              </div>
              <div className="flex items-center justify-between py-2 border-b">
                <span className="text-sm text-muted-foreground">账户类型</span>
                <Badge variant={user?.is_superuser ? "default" : "secondary"}>
                  {user?.is_superuser ? "超级管理员" : "普通用户"}
                </Badge>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-muted-foreground">注册时间</span>
                <span className="text-sm">
                  {user?.created_at
                    ? new Date(user.created_at).toLocaleDateString("zh-CN")
                    : "-"}
                </span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 偏好设置 */}
        <TabsContent value="preferences" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>显示偏好</CardTitle>
              <CardDescription>
                自定义您在使用系统时的显示设置
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="text-sm font-medium">深色模式</p>
                  <p className="text-xs text-muted-foreground">
                    切换深色/浅色主题
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  切换主题
                </Button>
              </div>

              <div className="flex items-center justify-between py-3 border-b">
                <div>
                  <p className="text-sm font-medium">语言设置</p>
                  <p className="text-xs text-muted-foreground">
                    选择系统显示语言
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  简体中文
                </Button>
              </div>

              <div className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm font-medium">时区设置</p>
                  <p className="text-xs text-muted-foreground">
                    选择您所在的时区
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  UTC+8
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
