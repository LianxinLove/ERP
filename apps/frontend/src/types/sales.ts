/**
 * 销售管理相关类型定义
 *
 * @description 前后端共享的销售类型
 */

/**
 * 客户状态
 */
export type CustomerStatus = 'active' | 'inactive' | 'blacklist';

/**
 * 销售订单状态
 */
export type SalesOrderStatus = 'draft' | 'pending' | 'confirmed' | 'partial_shipped' | 'shipped' | 'partial_paid' | 'paid' | 'cancelled' | 'closed';

/**
 * 销售退货状态
 */
export type SalesReturnStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'completed' | 'cancelled';

/**
 * 客户
 */
export interface Customer {
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
  status: CustomerStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 创建客户请求
 */
export interface CreateCustomerRequest {
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
  status?: CustomerStatus;
}

/**
 * 更新客户请求
 */
export interface UpdateCustomerRequest {
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
  status?: CustomerStatus;
}

/**
 * 销售订单明细
 */
export interface SalesOrderItem {
  id?: number;
  product_code?: string;
  product_name: string;
  specification?: string;
  unit?: string;
  quantity: number;
  shipped_quantity?: number;
  unit_price?: number;
  discount_rate?: number;
  amount?: number;
  tax_rate?: number;
  notes?: string;
}

/**
 * 销售订单
 */
export interface SalesOrder {
  id: number;
  order_no: string;
  customer_id: number;
  order_date: string;
  delivery_date?: string;
  total_amount?: number;
  tax_amount?: number;
  tax_inclusive: boolean;
  discount_amount?: number;
  paid_amount?: number;
  payment_terms?: number;
  delivery_address?: string;
  contact?: string;
  contact_phone?: string;
  salesperson_id?: number;
  notes?: string;
  status: SalesOrderStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 销售订单详情
 */
export interface SalesOrderDetail extends SalesOrder {
  items: SalesOrderItem[];
  customer?: Customer;
}

/**
 * 创建销售订单请求
 */
export interface CreateSalesOrderRequest {
  customer_id: number;
  order_date: string;
  delivery_date?: string;
  tax_inclusive?: boolean;
  discount_amount?: number;
  payment_terms?: number;
  delivery_address?: string;
  contact?: string;
  contact_phone?: string;
  salesperson_id?: number;
  notes?: string;
  items: SalesOrderItem[];
}

/**
 * 更新销售订单请求
 */
export interface UpdateSalesOrderRequest {
  customer_id?: number;
  order_date?: string;
  delivery_date?: string;
  tax_inclusive?: boolean;
  discount_amount?: number;
  payment_terms?: number;
  delivery_address?: string;
  contact?: string;
  contact_phone?: string;
  salesperson_id?: number;
  notes?: string;
  items?: SalesOrderItem[];
  status?: SalesOrderStatus;
}

/**
 * 销售退货明细
 */
export interface SalesReturnItem {
  id?: number;
  product_code?: string;
  product_name: string;
  specification?: string;
  unit?: string;
  quantity: number;
  unit_price?: number;
  amount?: number;
  notes?: string;
}

/**
 * 销售退货
 */
export interface SalesReturn {
  id: number;
  return_no: string;
  order_id?: number;
  customer_id: number;
  return_date: string;
  total_amount?: number;
  refund_amount?: number;
  reason?: string;
  notes?: string;
  status: SalesReturnStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 销售退货详情
 */
export interface SalesReturnDetail extends SalesReturn {
  items: SalesReturnItem[];
  customer?: Customer;
}

/**
 * 创建销售退货请求
 */
export interface CreateSalesReturnRequest {
  customer_id: number;
  return_date: string;
  order_id?: number;
  reason?: string;
  notes?: string;
  items: SalesReturnItem[];
}

/**
 * 更新销售退货请求
 */
export interface UpdateSalesReturnRequest {
  customer_id?: number;
  return_date?: string;
  order_id?: number;
  reason?: string;
  notes?: string;
  items?: SalesReturnItem[];
  status?: SalesReturnStatus;
}
