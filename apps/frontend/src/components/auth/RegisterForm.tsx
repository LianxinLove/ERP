'use client';

/**
 * 注册表单组件
 *
 * @description 用户注册表单
 *
 * @features
 * - 表单验证
 * - 密码确认
 * - 错误提示
 * - 平滑的主题过渡
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { useAuth } from '@/store/auth/AuthContext';
import { Loader2 } from 'lucide-react';

/**
 * 注册表单验证Schema
 */
const registerSchema = z
  .object({
    username: z.string().min(3, '用户名至少3个字符').max(50, '用户名最多50个字符'),
    email: z.string().email('请输入有效的邮箱地址'),
    password: z.string().min(6, '密码至少6个字符').max(50, '密码最多50个字符'),
    confirmPassword: z.string(),
    full_name: z.string().optional(),
    phone: z.string().optional(),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: '两次输入的密码不一致',
    path: ['confirmPassword'],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

/**
 * 注册表单组件
 */
export function RegisterForm() {
  const router = useRouter();
  const { register: registerUser, isLoading, error } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      full_name: '',
      phone: '',
    },
  });

  /**
   * 处理注册提交
   */
  const onSubmit = async (data: RegisterFormValues) => {
    setIsSubmitting(true);
    try {
      const { confirmPassword: _confirmPassword, ...registerData } = data;
      await registerUser(registerData);
      router.push('/dashboard');
    } catch {
      // 错误已在AuthContext中处理
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="w-full glass-card-light transition-all duration-300">
      <CardContent className="p-8">
        {/* 标题 */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary text-primary-foreground font-bold text-xl shadow-lg">
              ERP
            </div>
          </div>
          <h2 className="text-2xl font-bold text-foreground">创建账户</h2>
          <p className="text-muted-foreground mt-2">填写以下信息以注册新账户</p>
        </div>

        {/* 全局错误提示 */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg transition-colors duration-200">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* 用户名 */}
          <div className="space-y-2">
            <Label htmlFor="username" className="text-sm font-medium">
              用户名 <span className="text-destructive">*</span>
            </Label>
            <Input
              id="username"
              type="text"
              placeholder="请输入用户名"
              disabled={isSubmitting || isLoading}
              className="h-11 transition-all duration-200 focus-visible:ring-2"
              {...register('username')}
            />
            {errors.username && (
              <p className="text-sm text-destructive mt-1 transition-colors duration-200">
                {errors.username.message}
              </p>
            )}
          </div>

          {/* 邮箱 */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">
              邮箱地址 <span className="text-destructive">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="请输入邮箱"
              disabled={isSubmitting || isLoading}
              className="h-11 transition-all duration-200 focus-visible:ring-2"
              {...register('email')}
            />
            {errors.email && (
              <p className="text-sm text-destructive mt-1 transition-colors duration-200">
                {errors.email.message}
              </p>
            )}
          </div>

          {/* 姓名 */}
          <div className="space-y-2">
            <Label htmlFor="full_name" className="text-sm font-medium">
              姓名
            </Label>
            <Input
              id="full_name"
              type="text"
              placeholder="请输入姓名（可选）"
              disabled={isSubmitting || isLoading}
              className="h-11 transition-all duration-200 focus-visible:ring-2"
              {...register('full_name')}
            />
            {errors.full_name && (
              <p className="text-sm text-destructive mt-1 transition-colors duration-200">
                {errors.full_name.message}
              </p>
            )}
          </div>

          {/* 手机号 */}
          <div className="space-y-2">
            <Label htmlFor="phone" className="text-sm font-medium">
              手机号
            </Label>
            <Input
              id="phone"
              type="tel"
              placeholder="请输入手机号（可选）"
              disabled={isSubmitting || isLoading}
              className="h-11 transition-all duration-200 focus-visible:ring-2"
              {...register('phone')}
            />
            {errors.phone && (
              <p className="text-sm text-destructive mt-1 transition-colors duration-200">
                {errors.phone.message}
              </p>
            )}
          </div>

          {/* 密码 */}
          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium">
              密码 <span className="text-destructive">*</span>
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="请输入密码（至少6个字符）"
              disabled={isSubmitting || isLoading}
              className="h-11 transition-all duration-200 focus-visible:ring-2"
              {...register('password')}
            />
            {errors.password && (
              <p className="text-sm text-destructive mt-1 transition-colors duration-200">
                {errors.password.message}
              </p>
            )}
          </div>

          {/* 确认密码 */}
          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-sm font-medium">
              确认密码 <span className="text-destructive">*</span>
            </Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              disabled={isSubmitting || isLoading}
              className="h-11 transition-all duration-200 focus-visible:ring-2"
              {...register('confirmPassword')}
            />
            {errors.confirmPassword && (
              <p className="text-sm text-destructive mt-1 transition-colors duration-200">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>

          {/* 注册按钮 */}
          <Button
            type="submit"
            className="w-full h-11 bg-gradient-primary hover:shadow-lg transition-all duration-200 active:scale-[0.98]"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                注册中...
              </>
            ) : (
              '注册'
            )}
          </Button>

          {/* 登录链接 */}
          <div className="text-center pt-2">
            <p className="text-sm text-muted-foreground">
              已有账号？
              <Link
                href="/auth/login"
                className="ml-1 text-primary hover:text-primary/80 hover:underline font-medium transition-colors duration-200 cursor-pointer"
              >
                立即登录
              </Link>
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
