'use client';

/**
 * 登录表单组件
 *
 * @description 用户登录表单，支持用户名/邮箱登录
 *
 * @features
 * - 表单验证
 * - 记住我功能
 * - 错误提示
 * - 跳转注册
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
import { cn } from '@/lib/utils';

/**
 * 登录表单验证Schema
 */
const loginSchema = z.object({
  username: z.string().min(1, '请输入用户名或邮箱'),
  password: z.string().min(6, '密码至少6个字符'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

/**
 * 登录表单组件
 */
export function LoginForm() {
  const router = useRouter();
  const { login, isLoading, error } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  });

  /**
   * 处理登录提交
   */
  const onSubmit = async (data: LoginFormValues) => {
    setIsSubmitting(true);
    try {
      await login(data);
      // 只有登录成功后才跳转到dashboard
      router.push('/dashboard');
    } catch {
      // 登录失败，错误已在AuthContext中处理，不进行跳转
      return;
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
          <h2 className="text-2xl font-bold text-foreground">欢迎回来</h2>
          <p className="text-muted-foreground mt-2">登录您的账户以继续</p>
        </div>

        {/* 全局错误提示 */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg transition-colors duration-200">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* 用户名/邮箱 */}
          <div className="space-y-2">
            <Label htmlFor="username" className="text-sm font-medium">
              用户名或邮箱
            </Label>
            <Input
              id="username"
              type="text"
              placeholder="请输入用户名或邮箱"
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

          {/* 密码 */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password" className="text-sm font-medium">
                密码
              </Label>
              <Link
                href="/auth/forgot-password"
                className="text-sm text-primary hover:text-primary/80 hover:underline transition-colors duration-200 cursor-pointer"
              >
                忘记密码？
              </Link>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="请输入密码"
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

          {/* 记住我 */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="remember"
              className="w-4 h-4 rounded border-input text-primary focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 cursor-pointer transition-colors duration-200"
            />
            <Label htmlFor="remember" className="text-sm font-normal text-muted-foreground cursor-pointer select-none">
              记住我
            </Label>
          </div>

          {/* 登录按钮 */}
          <Button
            type="submit"
            className="w-full h-11 bg-gradient-primary hover:shadow-lg transition-all duration-200 active:scale-[0.98]"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                登录中...
              </>
            ) : (
              '登录'
            )}
          </Button>

          {/* 注册链接 */}
          <div className="text-center pt-2">
            <p className="text-sm text-muted-foreground">
              还没有账号？
              <Link
                href="/auth/register"
                className="ml-1 text-primary hover:text-primary/80 hover:underline font-medium transition-colors duration-200 cursor-pointer"
              >
                立即注册
              </Link>
            </p>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
