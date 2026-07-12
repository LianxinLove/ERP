/**
 * Inventory模块布局
 * @description 为库存管理模块提供认证和导航布局
 */

'use client';

import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';

export default function InventoryLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
}
