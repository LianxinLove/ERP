/**
 * Header 顶部栏组件
 * @description 包含搜索、通知、用户菜单、主题切换等
 */

"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useAuth } from '@/store/auth/AuthContext';
import { useTheme } from 'next-themes';
import { Menu, Search, Bell, Settings, LogOut, User, Home, ChevronRight, Sun, Moon, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface HeaderProps {
  onMenuClick?: () => void;
  className?: string;
}

export function Header({ onMenuClick, className }: HeaderProps) {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const pathname = usePathname();
  const [searchValue, setSearchValue] = useState('');

  // 面包屑导航
  const getBreadcrumbs = () => {
    const segments = pathname.split('/').filter(Boolean);
    if (segments.length === 0) return [{ title: '首页', href: '/dashboard' }];

    const breadcrumbs = [{ title: '首页', href: '/dashboard' }];
    let currentPath = '';

    const pathTitles: Record<string, string> = {
      dashboard: '仪表盘',
      finance: '财务管理',
      purchase: '采购管理',
      sales: '销售管理',
      inventory: '库存管理',
      workflow: '审批流程',
      customers: '客户管理',
      suppliers: '供应商管理',
      orders: '订单管理',
      requests: '采购申请',
      products: '产品管理',
      warehouses: '仓库管理',
      transactions: '库存流水',
      transfers: '库存调拨',
      pending: '待办任务',
      completed: '已办任务',
      accounts: '会计科目',
      receivables: '应收账款',
      payables: '应付账款',
      payments: '收付款记录',
    };

    for (const segment of segments) {
      currentPath += `/${segment}`;
      const title = pathTitles[segment] || segment;
      breadcrumbs.push({ title, href: currentPath });
    }

    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header
      className={cn(
        'sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background/80 backdrop-blur-md px-6 transition-colors duration-300',
        className
      )}
    >
      {/* 移动端菜单按钮和首页链接 */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          onClick={onMenuClick}
          aria-label="打开菜单"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <Link href="/dashboard">
          <Button variant="ghost" size="icon" className="hidden md:flex hover:bg-accent transition-colors">
            <Home className="h-5 w-5" />
          </Button>
        </Link>
      </div>

      {/* 搜索框 */}
      <div className="flex-1 max-w-md hidden sm:block">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <Input
            type="search"
            placeholder="搜索..."
            aria-label="搜索内容"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="pl-8 transition-colors duration-200"
          />
        </div>
      </div>

      {/* 面包屑导航 */}
      <nav className="hidden md:flex items-center gap-1 text-sm">
        {breadcrumbs.map((crumb, index) => (
          <React.Fragment key={crumb.href}>
            {index > 0 && (
              <ChevronRight className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            )}
            <Link
              href={crumb.href}
              className={cn(
                'hover:text-foreground transition-colors duration-200',
                index === breadcrumbs.length - 1
                  ? 'font-medium text-foreground cursor-default'
                  : 'text-muted-foreground cursor-pointer'
              )}
              aria-current={index === breadcrumbs.length - 1 ? 'page' : undefined}
            >
              {crumb.title}
            </Link>
          </React.Fragment>
        ))}
      </nav>

      {/* 右侧操作区 */}
      <div className="flex items-center gap-2 ml-auto">
        {/* 主题切换 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="hover:bg-accent transition-colors duration-200"
              aria-label="切换主题"
            >
              <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">切换主题</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setTheme('light')} className="cursor-pointer">
              <Sun className="mr-2 h-4 w-4" />
              <span>浅色</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme('dark')} className="cursor-pointer">
              <Moon className="mr-2 h-4 w-4" />
              <span>深色</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setTheme('system')} className="cursor-pointer">
              <Monitor className="mr-2 h-4 w-4" />
              <span>跟随系统</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* 通知 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative hover:bg-accent transition-colors duration-200"
              aria-label="通知"
            >
              <Bell className="h-5 w-5" />
              <Badge
                variant="destructive"
                className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
              >
                3
              </Badge>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>通知</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <div className="max-h-[300px] overflow-y-auto">
              <DropdownMenuItem asChild>
                <a href="/workflow/pending" className="cursor-pointer">
                  <div className="flex flex-col gap-1">
                    <span className="font-medium">新的待办任务</span>
                    <span className="text-sm text-muted-foreground">
                      您有 2 条待审批的采购申请
                    </span>
                  </div>
                </a>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <a href="/finance/overdue" className="cursor-pointer">
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-destructive">逾期预警</span>
                    <span className="text-sm text-muted-foreground">
                      有 3 笔应收账款已逾期
                    </span>
                  </div>
                </a>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <a href="/inventory?low_stock=true" className="cursor-pointer">
                  <div className="flex flex-col gap-1">
                    <span className="font-medium">库存预警</span>
                    <span className="text-sm text-muted-foreground">
                      5 个产品库存低于安全库存
                    </span>
                  </div>
                </a>
              </DropdownMenuItem>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <a href="/notifications" className="cursor-pointer justify-center">
                查看全部通知
              </a>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* 用户菜单 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="relative h-9 w-9 rounded-full hover:bg-accent transition-colors duration-200"
              aria-label="用户菜单"
            >
              <Avatar className="h-9 w-9">
                <AvatarImage src={user?.avatar_url} alt={user?.username} />
                <AvatarFallback>{user?.username?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>
              <div className="flex flex-col gap-1">
                <p className="font-medium">{user?.username}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <a href="/profile" className="cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                <span>个人资料</span>
              </a>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <a href="/settings" className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                <span>设置</span>
              </a>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
              <LogOut className="mr-2 h-4 w-4" />
              <span>退出登录</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
