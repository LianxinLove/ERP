/**
 * 采购管理相关类型定义
 *
 * @description 前后端共享的采购类型
 */

/**
 * 供应商状态
 */
export type SupplierStatus = 'active' | 'inactive' | 'blacklist';

/**
 * 采购申请状态
 */
export type PurchaseRequestStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'converted';

/**
 * 采购订单状态
 */
export type PurchaseOrderStatus = 'draft' | 'pending' | 'confirmed' | 'partial_received' | 'received' | 'cancelled' | 'closed';

/**
 * 供应商
 */
export interface Supplier {
  id: number;
  code: string;
  name: string;
  contact?: string;
  phone?: string;
  email?: string;
  address?: string;
  tax_number?: string;
  bank_name?: string;
  bank_account?: string;
  credit_limit?: number;
  payment_terms?: number;
  notes?: string;
  status: SupplierStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 创建供应商请求
 */
export interface CreateSupplierRequest {
  code: string;
  name: string;
  contact?: string;
  phone?: string;
  email?: string;
  address?: string;
  tax_number?: string;
  bank_name?: string;
  bank_account?: string;
  credit_limit?: number;
  payment_terms?: number;
  notes?: string;
  status?: SupplierStatus;
}

/**
 * 更新供应商请求
 */
export interface UpdateSupplierRequest {
  name?: string;
  contact?: string;
  phone?: string;
  email?: string;
  address?: string;
  tax_number?: string;
  bank_name?: string;
  bank_account?: string;
  credit_limit?: number;
  payment_terms?: number;
  notes?: string;
  status?: SupplierStatus;
}

/**
 * 采购申请明细
 */
export interface PurchaseRequestItem {
  id?: number;
  product_code?: string;
  product_name: string;
  specification?: string;
  unit?: string;
  quantity: number;
  estimated_price?: number;
  estimated_amount?: number;
  notes?: string;
}

/**
 * 采购申请
 */
export interface PurchaseRequest {
  id: number;
  request_no: string;
  title: string;
  request_date: string;
  applicant_id: number;
  department_id?: number;
  total_amount?: number;
  reason?: string;
  status: PurchaseRequestStatus;
  workflow_instance_id?: number;
  created_at: string;
  updated_at: string;
}

/**
 * 采购申请详情
 */
export interface PurchaseRequestDetail extends PurchaseRequest {
  items: PurchaseRequestItem[];
}

/**
 * 创建采购申请请求
 */
export interface CreatePurchaseRequestRequest {
  title: string;
  request_date: string;
  department_id?: number;
  reason?: string;
  items: PurchaseRequestItem[];
}

/**
 * 更新采购申请请求
 */
export interface UpdatePurchaseRequestRequest {
  title?: string;
  request_date?: string;
  department_id?: number;
  reason?: string;
  items?: PurchaseRequestItem[];
  status?: PurchaseRequestStatus;
}

/**
 * 采购订单明细
 */
export interface PurchaseOrderItem {
  id?: number;
  product_code?: string;
  product_name: string;
  specification?: string;
  unit?: string;
  quantity: number;
  received_quantity?: number;
  unit_price?: number;
  amount?: number;
  tax_rate?: number;
  notes?: string;
}

/**
 * 采购订单
 */
export interface PurchaseOrder {
  id: number;
  order_no: string;
  request_id?: number;
  supplier_id: number;
  order_date: string;
  expected_date?: string;
  total_amount?: number;
  tax_amount?: number;
  tax_inclusive: boolean;
  payment_terms?: number;
  delivery_address?: string;
  contact?: string;
  contact_phone?: string;
  notes?: string;
  status: PurchaseOrderStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 采购订单详情
 */
export interface PurchaseOrderDetail extends PurchaseOrder {
  items: PurchaseOrderItem[];
  supplier?: Supplier;
}

/**
 * 创建采购订单请求
 */
export interface CreatePurchaseOrderRequest {
  supplier_id: number;
  order_date: string;
  expected_date?: string;
  request_id?: number;
  tax_inclusive?: boolean;
  payment_terms?: number;
  delivery_address?: string;
  contact?: string;
  contact_phone?: string;
  notes?: string;
  items: PurchaseOrderItem[];
}

/**
 * 更新采购订单请求
 */
export interface UpdatePurchaseOrderRequest {
  supplier_id?: number;
  order_date?: string;
  expected_date?: string;
  tax_inclusive?: boolean;
  payment_terms?: number;
  delivery_address?: string;
  contact?: string;
  contact_phone?: string;
  notes?: string;
  items?: PurchaseOrderItem[];
  status?: PurchaseOrderStatus;
}
