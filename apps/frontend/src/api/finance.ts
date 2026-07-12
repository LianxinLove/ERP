/**
 * 财务管理 API 调用
 * @description 财务模块的 API 接口
 */

import { apiClient } from '@/lib/api/client';
import type {
  // 科目相关
  AccountCreate,
  AccountUpdate,
  AccountResponse,
  AccountTree,
  // 付款方式相关
  PaymentMethodCreate,
  PaymentMethodUpdate,
  PaymentMethodResponse,
  // 应收账款相关
  ReceivableCreate,
  ReceivableUpdate,
  ReceivableResponse,
  ReceivableDetail,
  // 应付账款相关
  PayableCreate,
  PayableUpdate,
  PayableResponse,
  PayableDetail,
  // 收付款记录相关
  PaymentCreate,
  PaymentUpdate,
  PaymentResponse,
  PaymentDetail,
  // 统计相关
  FinanceSummary,
} from '@/types/finance';

// ============ 科目相关 API ============

/** 获取科目树形结构 */
export const getAccountTree = async (): Promise<AccountTree[]> => {
  const response = await apiClient.get<AccountTree[]>('/api/finance/accounts/tree');
  return response.data;
};

/** 获取科目列表 */
export const getAccounts = async (params?: {
  account_type?: string;
  is_active?: boolean;
  skip?: number;
  limit?: number;
}): Promise<AccountResponse[]> => {
  const response = await apiClient.get<AccountResponse[]>('/api/finance/accounts', { params });
  return response.data;
};

/** 获取科目详情 */
export const getAccount = async (accountId: number): Promise<AccountResponse> => {
  const response = await apiClient.get<AccountResponse>(`/api/finance/accounts/${accountId}`);
  return response.data;
};

/** 创建科目 */
export const createAccount = async (data: AccountCreate): Promise<AccountResponse> => {
  const response = await apiClient.post<AccountResponse>('/api/finance/accounts', data);
  return response.data;
};

/** 更新科目 */
export const updateAccount = async (accountId: number, data: AccountUpdate): Promise<AccountResponse> => {
  const response = await apiClient.put<AccountResponse>(`/api/finance/accounts/${accountId}`, data);
  return response.data;
};

/** 删除科目 */
export const deleteAccount = async (accountId: number): Promise<void> => {
  await apiClient.delete(`/api/finance/accounts/${accountId}`);
};

// ============ 付款方式相关 API ============

/** 获取付款方式列表 */
export const getPaymentMethods = async (params?: {
  is_active?: boolean;
  skip?: number;
  limit?: number;
}): Promise<PaymentMethodResponse[]> => {
  const response = await apiClient.get<PaymentMethodResponse[]>('/api/finance/payment-methods', { params });
  return response.data;
};

/** 获取付款方式详情 */
export const getPaymentMethod = async (methodId: number): Promise<PaymentMethodResponse> => {
  const response = await apiClient.get<PaymentMethodResponse>(`/api/finance/payment-methods/${methodId}`);
  return response.data;
};

/** 创建付款方式 */
export const createPaymentMethod = async (data: PaymentMethodCreate): Promise<PaymentMethodResponse> => {
  const response = await apiClient.post<PaymentMethodResponse>('/api/finance/payment-methods', data);
  return response.data;
};

/** 更新付款方式 */
export const updatePaymentMethod = async (methodId: number, data: PaymentMethodUpdate): Promise<PaymentMethodResponse> => {
  const response = await apiClient.put<PaymentMethodResponse>(`/api/finance/payment-methods/${methodId}`, data);
  return response.data;
};

/** 删除付款方式 */
export const deletePaymentMethod = async (methodId: number): Promise<void> => {
  await apiClient.delete(`/api/finance/payment-methods/${methodId}`);
};

// ============ 应收账款相关 API ============

/** 获取应收账款列表 */
export const getReceivables = async (params?: {
  customer_id?: number;
  status?: string;
  keyword?: string;
  skip?: number;
  limit?: number;
}): Promise<ReceivableResponse[]> => {
  const response = await apiClient.get<ReceivableResponse[]>('/api/finance/receivables', { params });
  return response.data;
};

/** 获取应收账款详情 */
export const getReceivable = async (receivableId: number): Promise<ReceivableDetail> => {
  const response = await apiClient.get<ReceivableDetail>(`/api/finance/receivables/${receivableId}`);
  return response.data;
};

/** 创建应收账款 */
export const createReceivable = async (data: ReceivableCreate): Promise<ReceivableResponse> => {
  const response = await apiClient.post<ReceivableResponse>('/api/finance/receivables', data);
  return response.data;
};

/** 更新应收账款 */
export const updateReceivable = async (receivableId: number, data: ReceivableUpdate): Promise<ReceivableResponse> => {
  const response = await apiClient.put<ReceivableResponse>(`/api/finance/receivables/${receivableId}`, data);
  return response.data;
};

/** 删除应收账款 */
export const deleteReceivable = async (receivableId: number): Promise<void> => {
  await apiClient.delete(`/api/finance/receivables/${receivableId}`);
};

/** 检查逾期应收账款 */
export const checkOverdueReceivables = async (): Promise<ReceivableResponse[]> => {
  const response = await apiClient.post<ReceivableResponse[]>('/api/finance/receivables/check-overdue');
  return response.data;
};

// ============ 应付账款相关 API ============

/** 获取应付账款列表 */
export const getPayables = async (params?: {
  supplier_id?: number;
  status?: string;
  keyword?: string;
  skip?: number;
  limit?: number;
}): Promise<PayableResponse[]> => {
  const response = await apiClient.get<PayableResponse[]>('/api/finance/payables', { params });
  return response.data;
};

/** 获取应付账款详情 */
export const getPayable = async (payableId: number): Promise<PayableDetail> => {
  const response = await apiClient.get<PayableDetail>(`/api/finance/payables/${payableId}`);
  return response.data;
};

/** 创建应付账款 */
export const createPayable = async (data: PayableCreate): Promise<PayableResponse> => {
  const response = await apiClient.post<PayableResponse>('/api/finance/payables', data);
  return response.data;
};

/** 更新应付账款 */
export const updatePayable = async (payableId: number, data: PayableUpdate): Promise<PayableResponse> => {
  const response = await apiClient.put<PayableResponse>(`/api/finance/payables/${payableId}`, data);
  return response.data;
};

/** 删除应付账款 */
export const deletePayable = async (payableId: number): Promise<void> => {
  await apiClient.delete(`/api/finance/payables/${payableId}`);
};

/** 检查逾期应付账款 */
export const checkOverduePayables = async (): Promise<PayableResponse[]> => {
  const response = await apiClient.post<PayableResponse[]>('/api/finance/payables/check-overdue');
  return response.data;
};

// ============ 收付款记录相关 API ============

/** 获取收付款记录列表 */
export const getPayments = async (params?: {
  payment_type?: string;
  status?: string;
  receivable_id?: number;
  payable_id?: number;
  skip?: number;
  limit?: number;
}): Promise<PaymentResponse[]> => {
  const response = await apiClient.get<PaymentResponse[]>('/api/finance/payments', { params });
  return response.data;
};

/** 获取收付款记录详情 */
export const getPayment = async (paymentId: number): Promise<PaymentDetail> => {
  const response = await apiClient.get<PaymentDetail>(`/api/finance/payments/${paymentId}`);
  return response.data;
};

/** 创建收付款记录 */
export const createPayment = async (data: PaymentCreate): Promise<PaymentResponse> => {
  const response = await apiClient.post<PaymentResponse>('/api/finance/payments', data);
  return response.data;
};

/** 更新收付款记录 */
export const updatePayment = async (paymentId: number, data: PaymentUpdate): Promise<PaymentResponse> => {
  const response = await apiClient.put<PaymentResponse>(`/api/finance/payments/${paymentId}`, data);
  return response.data;
};

/** 完成收付款 */
export const completePayment = async (paymentId: number): Promise<PaymentResponse> => {
  const response = await apiClient.post<PaymentResponse>(`/api/finance/payments/${paymentId}/complete`);
  return response.data;
};

/** 取消收付款 */
export const cancelPayment = async (paymentId: number): Promise<PaymentResponse> => {
  const response = await apiClient.post<PaymentResponse>(`/api/finance/payments/${paymentId}/cancel`);
  return response.data;
};

/** 删除收付款记录 */
export const deletePayment = async (paymentId: number): Promise<void> => {
  await apiClient.delete(`/api/finance/payments/${paymentId}`);
};

// ============ 财务统计 API ============

/** 获取财务汇总 */
export const getFinanceSummary = async (): Promise<FinanceSummary> => {
  const response = await apiClient.get<FinanceSummary>('/api/finance/summary');
  return response.data;
};

// 导出统一的 API 对象
export const financeApi = {
  // 科目
  getAccountTree,
  getAccounts,
  getAccount,
  createAccount,
  updateAccount,
  deleteAccount,
  // 付款方式
  getPaymentMethods,
  getPaymentMethod,
  createPaymentMethod,
  updatePaymentMethod,
  deletePaymentMethod,
  // 应收账款
  getReceivables,
  getReceivable,
  createReceivable,
  updateReceivable,
  deleteReceivable,
  checkOverdueReceivables,
  // 应付账款
  getPayables,
  getPayable,
  createPayable,
  updatePayable,
  deletePayable,
  checkOverduePayables,
  // 收付款记录
  getPayments,
  getPayment,
  createPayment,
  updatePayment,
  completePayment,
  cancelPayment,
  deletePayment,
  // 统计
  getFinanceSummary,
};
