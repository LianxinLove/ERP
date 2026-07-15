/**
 * Sidebar 侧边栏导航组件
 * @description 主导航侧边栏，支持展开/折叠，带有平滑过渡和交互反馈
 */

"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  Users,
  Settings,
  Building2,
  Workflow,
  ShoppingCart,
  Package,
  DollarSign,
  FileText,
  Wrench,
} from 'lucide-react';

interface NavItem {
  title: string;
  href: string;
  icon: React.ReactNode;
  badge?: string | number;
  items?: NavItem[];
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    title: '主要功能',
    items: [
      { title: '仪表盘', href: '/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
      { title: '工作流', href: '/workflow', icon: <Workflow className="h-4 w-4" /> },
    ],
  },
  {
    title: '业务管理',
    items: [
      { title: '采购管理', href: '/purchase', icon: <ShoppingCart className="h-4 w-4" /> },
      { title: '销售管理', href: '/sales', icon: <FileText className="h-4 w-4" /> },
      { title: '库存管理', href: '/inventory', icon: <Package className="h-4 w-4" /> },
      { title: '财务管理', href: '/finance', icon: <DollarSign className="h-4 w-4" /> },
    ],
  },
  {
    title: '系统管理',
    items: [
      { title: '组织架构', href: '/organization', icon: <Building2 className="h-4 w-4" /> },
      { title: '用户权限', href: '/rbac', icon: <Users className="h-4 w-4" /> },
      { title: '系统设置', href: '/settings', icon: <Settings className="h-4 w-4" /> },
    ],
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div
      className={cn(
        'relative flex flex-col h-full border-r bg-card/80 backdrop-blur-md transition-all duration-300 ease-out',
        isCollapsed ? 'w-16' : 'w-64',
        className
      )}
    >
      {/* Logo / 标题区域 */}
      <div className="flex h-16 items-center justify-between border-b px-4 transition-colors duration-300">
        {!isCollapsed && (
          <Link
            href="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary text-primary-foreground font-bold shadow-md">
              ERP
            </div>
            <span className="font-semibold text-foreground">管理系统</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="h-8 w-8 hover:bg-accent transition-colors duration-200"
          aria-label={isCollapsed ? '展开侧边栏' : '折叠侧边栏'}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* 导航菜单 */}
      <ScrollArea className="flex-1 px-2 py-4 scrollbar-thin">
        {navSections.map((section) => (
          <div key={section.title} className="mb-6">
            {!isCollapsed && (
              <div className="mb-2 px-2 text-xs font-semibold text-muted-foreground transition-colors duration-200">
                {section.title}
              </div>
            )}
            <nav className="space-y-1">
              {section.items.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                return (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={isActive ? 'secondary' : 'ghost'}
                      className={cn(
                        'w-full justify-start gap-3 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]',
                        isCollapsed && 'justify-center px-2',
                        isActive && 'bg-secondary font-medium shadow-sm'
                      )}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      <span className={cn(
                        'transition-colors duration-200',
                        isActive ? 'text-primary' : 'text-muted-foreground'
                      )}>
                        {item.icon}
                      </span>
                      {!isCollapsed && (
                        <span className="transition-colors duration-200">{item.title}</span>
                      )}
                      {!isCollapsed && item.badge && (
                        <Badge variant="secondary" className="ml-auto transition-colors duration-200">
                          {item.badge}
                        </Badge>
                      )}
                    </Button>
                  </Link>
                );
              })}
            </nav>
          </div>
        ))}
      </ScrollArea>

      {/* 底部用户信息 */}
      <div className="border-t p-4 transition-colors duration-300">
        <Button
          variant="ghost"
          className={cn(
            'w-full justify-start gap-3 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]',
            isCollapsed && 'justify-center px-2'
          )}
          asChild
        >
          <Link href="/settings">
            <Wrench className="h-4 w-4 text-muted-foreground transition-colors duration-200" />
            {!isCollapsed && <span className="transition-colors duration-200">偏好设置</span>}
          </Link>
        </Button>
      </div>
    </div>
  );
}

// 移动端侧边栏（抽屉式）
interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileSidebar({ isOpen, onClose }: MobileSidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* 遮罩层 */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm transition-opacity duration-300"
          onClick={onClose}
        />
      )}

      {/* 侧边栏 */}
      <div
        className={cn(
          'fixed top-0 bottom-0 left-0 z-50 h-full w-64 transform transition-transform duration-300 ease-out',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col border-r bg-card/95 backdrop-blur-md shadow-lg">
          {/* Logo / 标题区域 */}
          <div className="flex h-16 items-center justify-between border-b px-4 transition-colors duration-300">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer"
              onClick={onClose}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary text-primary-foreground font-bold shadow-md">
                ERP
              </div>
              <span className="font-semibold text-foreground">管理系统</span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="hover:bg-accent transition-colors duration-200"
              aria-label="关闭侧边栏"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </div>

          {/* 导航菜单 */}
          <ScrollArea className="flex-1 px-2 py-4 scrollbar-thin">
            {navSections.map((section) => (
              <div key={section.title} className="mb-6">
                <div className="mb-2 px-2 text-xs font-semibold text-muted-foreground transition-colors duration-200">
                  {section.title}
                </div>
                <nav className="space-y-1">
                  {section.items.map((item) => {
                    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                    return (
                      <Link key={item.href} href={item.href} onClick={onClose}>
                        <Button
                          variant={isActive ? 'secondary' : 'ghost'}
                          className={cn(
                            'w-full justify-start gap-3 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] cursor-pointer',
                            isActive && 'bg-secondary font-medium shadow-sm'
                          )}
                        >
                          <span className={cn(
                            'transition-colors duration-200',
                            isActive ? 'text-primary' : 'text-muted-foreground'
                          )}>
                            {item.icon}
                          </span>
                          <span className="transition-colors duration-200">{item.title}</span>
                          {item.badge && (
                            <Badge variant="secondary" className="ml-auto transition-colors duration-200">
                              {item.badge}
                            </Badge>
                          )}
                        </Button>
                      </Link>
                    );
                  })}
                </nav>
              </div>
            ))}
          </ScrollArea>
        </div>
      </div>
    </>
  );
}
