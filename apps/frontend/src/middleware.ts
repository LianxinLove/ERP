/**
 * Next.js Middleware
 *
 * @description 服务端路由保护，防止未授权用户访问受保护页面
 *
 * @features
 * - 检查 access_token cookie 是否存在
 * - 重定向未认证用户到登录页
 * - 重定向已认证用户离开认证页
 * - 保护所有业务模块路由
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * 需要认证的路径前缀
 */
const PROTECTED_PATHS = [
  '/dashboard',
  '/sales',
  '/purchase',
  '/inventory',
  '/finance',
  '/organization',
  '/workflow',
  '/rbac',
  '/settings',
]

/**
 * 认证相关路径（已登录用户不应访问）
 */
const AUTH_PATHS = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
]

/**
 * 公开路径（无需认证）
 */
const PUBLIC_PATHS = [
  '/api', // API 路由由后端处理
  '/_next', // Next.js 内部
  '/favicon.ico',
  '/static',
]

/**
 * 中间件主函数
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // 从 cookie 获取 token
  const token = request.cookies.get('access_token')?.value

  // 检查是否为受保护路径
  const isProtectedPath = PROTECTED_PATHS.some(path => pathname.startsWith(path))

  // 检查是否为认证路径
  const isAuthPath = AUTH_PATHS.some(path => pathname.startsWith(path))

  // 受保护路径：没有 token 时重定向到登录页
  if (isProtectedPath && !token) {
    const loginUrl = new URL('/auth/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // 认证路径：已有 token 时重定向到首页
  if (isAuthPath && token) {
    const redirectUrl = request.nextUrl.searchParams.get('redirect') || '/dashboard'
    return NextResponse.redirect(new URL(redirectUrl, request.url))
  }

  // 根路径：根据认证状态重定向
  if (pathname === '/' && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  if (pathname === '/' && !token) {
    return NextResponse.redirect(new URL('/auth/login', request.url))
  }

  return NextResponse.next()
}

/**
 * Middleware 匹配配置
 *
 * @description 排除静态资源、API 路由和 Next.js 内部路径
 */
export const config = {
  matcher: [
    /*
     * 匹配所有路径除了：
     * - _next/static (静态文件)
     * - _next/image (图片优化文件)
     * - favicon.ico (favicon 文件)
     * - public 文件夹中的静态资源
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\..*$).*)',
  ],
}
