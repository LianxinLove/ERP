/**
 * 财务管理类型定义
 * @description 财务模块相关的数据结构
 */

// ============ 科目相关 ============

/**
 * 科目类型
 */
export enum AccountType {
  ASSET = 'asset',
  ASSETS = 'asset',
  LIABILITY = 'liability',
  LIABILITIES = 'liability',
  EQUITY = 'equity',
  REVENUE = 'revenue',
  EXPENSE = 'expense',
}

/**
 * 创建科目请求
 */
export interface AccountCreate {
  code: string;
  name: string;
  account_type: AccountType;
  parent_id?: number;
  description?: string;
  is_active?: boolean;
}

/**
 * 更新科目请求
 */
export interface AccountUpdate {
  code?: string;
  name?: string;
  account_type?: AccountType;
  parent_id?: number;
  description?: string;
  is_active?: boolean;
}

/**
 * 科目响应
 */
export interface AccountResponse {
  id: number;
  code: string;
  name: string;
  account_type: AccountType;
  parent_id?: number;
  description?: string;
  is_active: boolean;
  level: number;
  full_code: string;
  full_name: string;
  created_at: string;
  updated_at: string;
}

/**
 * 科目树形结构
 */
export interface AccountTree extends AccountResponse {
  children: AccountTree[];
}

// ============ 付款方式相关 ============

/**
 * 创建付款方式请求
 */
export interface PaymentMethodCreate {
  name: string;
  code: string;
  description?: string;
  is_active?: boolean;
}

/**
 * 更新付款方式请求
 */
export interface PaymentMethodUpdate {
  name?: string;
  code?: string;
  description?: string;
  is_active?: boolean;
}

/**
 * 付款方式响应
 */
export interface PaymentMethodResponse {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============ 应收账款相关 ============

/**
 * 应收账款状态
 */
export enum ReceivableStatus {
  PENDING = 'pending',
  PARTIAL = 'partial',
  PARTIAL_PAID = 'partial_paid',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
  WRITE_OFF = 'write_off',
}

/**
 * 创建应收账款请求
 */
export interface ReceivableCreate {
  customer_id: number;
  sales_order_id?: number;
  amount: number;
  due_date: string;
  description?: string;
  notes?: string;
}

/**
 * 更新应收账款请求
 */
export interface ReceivableUpdate {
  customer_id?: number;
  sales_order_id?: number;
  amount?: number;
  due_date?: string;
  description?: string;
  status?: ReceivableStatus;
}

/**
 * 应收账款响应
 */
export interface ReceivableResponse {
  id: number;
  receivable_no: string;
  customer_id: number;
  customer_name?: string;
  sales_order_id?: number;
  amount: number;
  paid_amount: number;
  remaining_amount: number;
  status: ReceivableStatus;
  due_date: string;
  description?: string;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 应收账款详情
 */
export interface ReceivableDetail extends ReceivableResponse {
  payments: PaymentResponse[];
}

// ============ 应付账款相关 ============

/**
 * 应付账款状态
 */
export enum PayableStatus {
  PENDING = 'pending',
  PARTIAL = 'partial',
  PARTIAL_PAID = 'partial_paid',
  PAID = 'paid',
  OVERDUE = 'overdue',
  CANCELLED = 'cancelled',
  WRITE_OFF = 'write_off',
}

/**
 * 创建应付账款请求
 */
export interface PayableCreate {
  supplier_id: number;
  purchase_order_id?: number;
  amount: number;
  due_date: string;
  description?: string;
  notes?: string;
}

/**
 * 更新应付账款请求
 */
export interface PayableUpdate {
  supplier_id?: number;
  purchase_order_id?: number;
  amount?: number;
  due_date?: string;
  description?: string;
  status?: PayableStatus;
}

/**
 * 应付账款响应
 */
export interface PayableResponse {
  id: number;
  payable_no: string;
  supplier_id: number;
  supplier_name?: string;
  purchase_order_id?: number;
  amount: number;
  paid_amount: number;
  remaining_amount: number;
  status: PayableStatus;
  due_date: string;
  description?: string;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * 应付账款详情
 */
export interface PayableDetail extends PayableResponse {
  payments: PaymentResponse[];
}

// ============ 收付款记录相关 ============

/**
 * 收付款类型
 */
export enum PaymentType {
  RECEIVABLE = 'receivable',
  RECEIPT = 'receipt',
  PAYABLE = 'payable',
  PAYMENT = 'payment',
}

/**
 * 收付款状态
 */
export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/**
 * 创建收付款记录请求
 */
export interface PaymentCreate {
  payment_type: PaymentType;
  receivable_id?: number;
  payable_id?: number;
  amount: number;
  payment_method_id: number;
  payment_date?: string;
  reference?: string;
  reference_no?: string;
  notes?: string;
}

/**
 * 更新收付款记录请求
 */
export interface PaymentUpdate {
  amount?: number;
  payment_method_id?: number;
  payment_date?: string;
  reference?: string;
  notes?: string;
  status?: PaymentStatus;
}

/**
 * 收付款记录响应
 */
export interface PaymentResponse {
  id: number;
  payment_no: string;
  payment_type: PaymentType;
  receivable_id?: number;
  payable_id?: number;
  amount: number;
  payment_method_id: number;
  payment_method_name?: string;
  payment_date: string;
  reference?: string;
  reference_no?: string;
  notes?: string;
  status: PaymentStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 收付款记录详情
 */
export interface PaymentDetail extends PaymentResponse {
  receivable?: ReceivableResponse;
  payable?: PayableResponse;
}

// ============ 财务统计相关 ============

/**
 * 财务汇总
 */
export interface FinanceSummary {
  total_receivables: number;
  total_receivable: number;
  total_payables: number;
  total_payable: number;
  total_overdue_receivables: number;
  total_overdue_payables: number;
  current_month_revenue: number;
  current_month_expense: number;
  total_payment_in: number;
  total_payment_out: number;
  receivable_count: number;
  payable_count: number;
  overdue_receivable_count: number;
  overdue_payable_count: number;
}
