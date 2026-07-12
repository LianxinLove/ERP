/**
 * 采购管理API
 *
 * @description 采购模块的API调用
 */

import { apiClient } from '@/lib/api/client';
import type {
  Supplier,
  CreateSupplierRequest,
  UpdateSupplierRequest,
  PurchaseRequest,
  PurchaseRequestDetail,
  CreatePurchaseRequestRequest,
  UpdatePurchaseRequestRequest,
  PurchaseOrder,
  PurchaseOrderDetail,
  CreatePurchaseOrderRequest,
  UpdatePurchaseOrderRequest,
} from '@/types/purchase';

/**
 * 采购管理API类
 */
class PurchaseAPI {
  // ============ 供应商相关 ============

  /**
   * 获取供应商列表
   */
  async getSuppliers(params?: {
    status?: string;
    keyword?: string;
    skip?: number;
    limit?: number;
  }): Promise<Supplier[]> {
    const response = await apiClient.get('/api/purchase/suppliers', { params });
    return response.data;
  }

  /**
   * 获取供应商详情
   */
  async getSupplier(supplierId: number): Promise<Supplier> {
    const response = await apiClient.get(`/api/purchase/suppliers/${supplierId}`);
    return response.data;
  }

  /**
   * 创建供应商
   */
  async createSupplier(data: CreateSupplierRequest): Promise<Supplier> {
    const response = await apiClient.post('/api/purchase/suppliers', data);
    return response.data;
  }

  /**
   * 更新供应商
   */
  async updateSupplier(
    supplierId: number,
    data: UpdateSupplierRequest
  ): Promise<Supplier> {
    const response = await apiClient.put(`/api/purchase/suppliers/${supplierId}`, data);
    return response.data;
  }

  /**
   * 删除供应商
   */
  async deleteSupplier(supplierId: number): Promise<void> {
    await apiClient.delete(`/api/purchase/suppliers/${supplierId}`);
  }

  // ============ 采购申请相关 ============

  /**
   * 获取采购申请列表
   */
  async getRequests(params?: {
    applicant_id?: number;
    status?: string;
    department_id?: number;
    keyword?: string;
    skip?: number;
    limit?: number;
  }): Promise<PurchaseRequest[]> {
    const response = await apiClient.get('/api/purchase/requests', { params });
    return response.data;
  }

  /**
   * 获取采购申请详情
   */
  async getRequest(requestId: number): Promise<PurchaseRequestDetail> {
    const response = await apiClient.get(`/api/purchase/requests/${requestId}`);
    return response.data;
  }

  /**
   * 创建采购申请
   */
  async createRequest(data: CreatePurchaseRequestRequest): Promise<PurchaseRequest> {
    const response = await apiClient.post('/api/purchase/requests', data);
    return response.data;
  }

  /**
   * 更新采购申请
   */
  async updateRequest(
    requestId: number,
    data: UpdatePurchaseRequestRequest
  ): Promise<PurchaseRequest> {
    const response = await apiClient.put(`/api/purchase/requests/${requestId}`, data);
    return response.data;
  }

  /**
   * 提交采购申请（启动审批流程）
   */
  async submitRequest(requestId: number): Promise<PurchaseRequest> {
    const response = await apiClient.post(`/api/purchase/requests/${requestId}/submit`);
    return response.data;
  }

  /**
   * 删除采购申请
   */
  async deleteRequest(requestId: number): Promise<void> {
    await apiClient.delete(`/api/purchase/requests/${requestId}`);
  }

  // ============ 采购订单相关 ============

  /**
   * 获取采购订单列表
   */
  async getOrders(params?: {
    supplier_id?: number;
    status?: string;
    keyword?: string;
    skip?: number;
    limit?: number;
  }): Promise<PurchaseOrder[]> {
    const response = await apiClient.get('/api/purchase/orders', { params });
    return response.data;
  }

  /**
   * 获取采购订单详情
   */
  async getOrder(orderId: number): Promise<PurchaseOrderDetail> {
    const response = await apiClient.get(`/api/purchase/orders/${orderId}`);
    return response.data;
  }

  /**
   * 创建采购订单
   */
  async createOrder(data: CreatePurchaseOrderRequest): Promise<PurchaseOrder> {
    const response = await apiClient.post('/api/purchase/orders', data);
    return response.data;
  }

  /**
   * 更新采购订单
   */
  async updateOrder(
    orderId: number,
    data: UpdatePurchaseOrderRequest
  ): Promise<PurchaseOrder> {
    const response = await apiClient.put(`/api/purchase/orders/${orderId}`, data);
    return response.data;
  }

  /**
   * 确认采购订单
   */
  async confirmOrder(orderId: number): Promise<PurchaseOrder> {
    const response = await apiClient.post(`/api/purchase/orders/${orderId}/confirm`);
    return response.data;
  }

  /**
   * 取消采购订单
   */
  async cancelOrder(orderId: number): Promise<PurchaseOrder> {
    const response = await apiClient.post(`/api/purchase/orders/${orderId}/cancel`);
    return response.data;
  }

  /**
   * 删除采购订单
   */
  async deleteOrder(orderId: number): Promise<void> {
    await apiClient.delete(`/api/purchase/orders/${orderId}`);
  }
}

/**
 * 导出采购管理API实例
 */
export const purchaseApi = new PurchaseAPI();
