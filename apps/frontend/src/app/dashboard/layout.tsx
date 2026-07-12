/**
 * Dashboard布局
 * @description 为Dashboard页面提供认证和导航布局
 */

'use client';

import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}
