/**
 * Organization模块布局
 * @description 为组织架构模块提供认证和导航布局
 */

'use client';

import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';

export default function OrganizationLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}
