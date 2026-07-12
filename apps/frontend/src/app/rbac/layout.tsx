/**
 * RBAC模块布局
 * @description 为用户权限模块提供认证和导航布局
 */

'use client';

import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';

export default function RbacLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}
