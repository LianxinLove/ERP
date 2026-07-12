/**
 * 销售管理API
 *
 * @description 销售模块的API调用
 */

import { apiClient } from '@/lib/api/client';
import type {
  Customer,
  CreateCustomerRequest,
  UpdateCustomerRequest,
  SalesOrder,
  SalesOrderDetail,
  CreateSalesOrderRequest,
  UpdateSalesOrderRequest,
  SalesReturn,
  SalesReturnDetail,
  CreateSalesReturnRequest,
} from '@/types/sales';

/**
 * 销售管理API类
 */
class SalesAPI {
  // ============ 客户相关 ============

  /**
   * 获取客户列表
   */
  async getCustomers(params?: {
    status?: string;
    keyword?: string;
    skip?: number;
    limit?: number;
  }): Promise<Customer[]> {
    const response = await apiClient.get('/api/sales/customers', { params });
    return response.data;
  }

  /**
   * 获取客户详情
   */
  async getCustomer(customerId: number): Promise<Customer> {
    const response = await apiClient.get(`/api/sales/customers/${customerId}`);
    return response.data;
  }

  /**
   * 创建客户
   */
  async createCustomer(data: CreateCustomerRequest): Promise<Customer> {
    const response = await apiClient.post('/api/sales/customers', data);
    return response.data;
  }

  /**
   * 更新客户
   */
  async updateCustomer(
    customerId: number,
    data: UpdateCustomerRequest
  ): Promise<Customer> {
    const response = await apiClient.put(`/api/sales/customers/${customerId}`, data);
    return response.data;
  }

  /**
   * 删除客户
   */
  async deleteCustomer(customerId: number): Promise<void> {
    await apiClient.delete(`/api/sales/customers/${customerId}`);
  }

  // ============ 销售订单相关 ============

  /**
   * 获取销售订单列表
   */
  async getOrders(params?: {
    customer_id?: number;
    status?: string;
    keyword?: string;
    skip?: number;
    limit?: number;
  }): Promise<SalesOrder[]> {
    const response = await apiClient.get('/api/sales/orders', { params });
    return response.data;
  }

  /**
   * 获取销售订单详情
   */
  async getOrder(orderId: number): Promise<SalesOrderDetail> {
    const response = await apiClient.get(`/api/sales/orders/${orderId}`);
    return response.data;
  }

  /**
   * 创建销售订单
   */
  async createOrder(data: CreateSalesOrderRequest): Promise<SalesOrder> {
    const response = await apiClient.post('/api/sales/orders', data);
    return response.data;
  }

  /**
   * 更新销售订单
   */
  async updateOrder(
    orderId: number,
    data: UpdateSalesOrderRequest
  ): Promise<SalesOrder> {
    const response = await apiClient.put(`/api/sales/orders/${orderId}`, data);
    return response.data;
  }

  /**
   * 确认销售订单
   */
  async confirmOrder(orderId: number): Promise<SalesOrder> {
    const response = await apiClient.post(`/api/sales/orders/${orderId}/confirm`);
    return response.data;
  }

  /**
   * 取消销售订单
   */
  async cancelOrder(orderId: number): Promise<SalesOrder> {
    const response = await apiClient.post(`/api/sales/orders/${orderId}/cancel`);
    return response.data;
  }

  /**
   * 删除销售订单
   */
  async deleteOrder(orderId: number): Promise<void> {
    await apiClient.delete(`/api/sales/orders/${orderId}`);
  }

  // ============ 销售退货相关 ============

  /**
   * 获取销售退货列表
   */
  async getReturns(params?: {
    customer_id?: number;
    status?: string;
    keyword?: string;
    skip?: number;
    limit?: number;
  }): Promise<SalesReturn[]> {
    const response = await apiClient.get('/api/sales/returns', { params });
    return response.data;
  }

  /**
   * 获取销售退货详情
   */
  async getReturn(returnId: number): Promise<SalesReturnDetail> {
    const response = await apiClient.get(`/api/sales/returns/${returnId}`);
    return response.data;
  }

  /**
   * 创建销售退货
   */
  async createReturn(data: CreateSalesReturnRequest): Promise<SalesReturn> {
    const response = await apiClient.post('/api/sales/returns', data);
    return response.data;
  }

  /**
   * 删除销售退货
   */
  async deleteReturn(returnId: number): Promise<void> {
    await apiClient.delete(`/api/sales/returns/${returnId}`);
  }
}

/**
 * 导出销售管理API实例
 */
export const salesApi = new SalesAPI();
