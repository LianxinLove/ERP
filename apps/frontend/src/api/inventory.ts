/**
 * 库存管理 API 客户端
 * @description 库存模块的 API 调用函数
 */

import { apiClient } from '@/lib/api/client';
import type {
  // 产品相关
  Product,
  ProductCreate,
  ProductUpdate,
  // 仓库相关
  Warehouse,
  WarehouseCreate,
  WarehouseUpdate,
  // 库存相关
  InventoryDetail,
  InventoryQueryParams,
  // 流水相关
  InventoryTransaction,
  TransactionQueryParams,
  // 调拨相关
  InventoryTransfer,
  InventoryTransferCreate,
  InventoryTransferDetail,
  TransferQueryParams,
} from '@/types/inventory';

// ============ 产品相关 API ============

/**
 * 获取产品列表
 */
export async function getProducts(params?: {
  category?: string;
  keyword?: string;
  status?: string;
  skip?: number;
  limit?: number;
}): Promise<Product[]> {
  const response = await apiClient.get<Product[]>('/api/inventory/products', { params });
  return response.data;
}

/**
 * 获取产品详情
 */
export async function getProduct(productId: number): Promise<Product> {
  const response = await apiClient.get<Product>(`/api/inventory/products/${productId}`);
  return response.data;
}

/**
 * 创建产品
 */
export async function createProduct(data: ProductCreate): Promise<Product> {
  const response = await apiClient.post<Product>('/api/inventory/products', data);
  return response.data;
}

/**
 * 更新产品
 */
export async function updateProduct(productId: number, data: ProductUpdate): Promise<Product> {
  const response = await apiClient.put<Product>(`/api/inventory/products/${productId}`, data);
  return response.data;
}

/**
 * 删除产品
 */
export async function deleteProduct(productId: number): Promise<void> {
  await apiClient.delete(`/api/inventory/products/${productId}`);
}

// ============ 仓库相关 API ============

/**
 * 获取仓库列表
 */
export async function getWarehouses(params?: {
  skip?: number;
  limit?: number;
}): Promise<Warehouse[]> {
  const response = await apiClient.get<Warehouse[]>('/api/inventory/warehouses', { params });
  return response.data;
}

/**
 * 获取仓库详情
 */
export async function getWarehouse(warehouseId: number): Promise<Warehouse> {
  const response = await apiClient.get<Warehouse>(`/api/inventory/warehouses/${warehouseId}`);
  return response.data;
}

/**
 * 创建仓库
 */
export async function createWarehouse(data: WarehouseCreate): Promise<Warehouse> {
  const response = await apiClient.post<Warehouse>('/api/inventory/warehouses', data);
  return response.data;
}

/**
 * 更新仓库
 */
export async function updateWarehouse(warehouseId: number, data: WarehouseUpdate): Promise<Warehouse> {
  const response = await apiClient.put<Warehouse>(`/api/inventory/warehouses/${warehouseId}`, data);
  return response.data;
}

/**
 * 删除仓库
 */
export async function deleteWarehouse(warehouseId: number): Promise<void> {
  await apiClient.delete(`/api/inventory/warehouses/${warehouseId}`);
}

// ============ 库存查询相关 API ============

/**
 * 获取库存列表
 */
export async function getInventories(params?: InventoryQueryParams): Promise<InventoryDetail[]> {
  const response = await apiClient.get<InventoryDetail[]>('/api/inventory/inventories', { params });
  return response.data;
}

/**
 * 获取库存流水列表
 */
export async function getInventoryTransactions(params?: TransactionQueryParams): Promise<InventoryTransaction[]> {
  const response = await apiClient.get<InventoryTransaction[]>('/api/inventory/transactions', { params });
  return response.data;
}

// ============ 库存调拨相关 API ============

/**
 * 获取调拨单列表
 */
export async function getInventoryTransfers(params?: TransferQueryParams): Promise<InventoryTransfer[]> {
  const response = await apiClient.get<InventoryTransfer[]>('/api/inventory/transfers', { params });
  return response.data;
}

/**
 * 获取调拨单详情
 */
export async function getInventoryTransfer(transferId: number): Promise<InventoryTransferDetail> {
  const response = await apiClient.get<InventoryTransferDetail>(`/api/inventory/transfers/${transferId}`);
  return response.data;
}

/**
 * 创建调拨单
 */
export async function createInventoryTransfer(data: InventoryTransferCreate): Promise<InventoryTransfer> {
  const response = await apiClient.post<InventoryTransfer>('/api/inventory/transfers', data);
  return response.data;
}

/**
 * 执行调拨
 */
export async function executeInventoryTransfer(transferId: number): Promise<InventoryTransfer> {
  const response = await apiClient.post<InventoryTransfer>(`/api/inventory/transfers/${transferId}/execute`);
  return response.data;
}

/**
 * 删除调拨单
 */
export async function deleteInventoryTransfer(transferId: number): Promise<void> {
  await apiClient.delete(`/api/inventory/transfers/${transferId}`);
}

// ============ API 对象导出 ============

export const inventoryApi = {
  // 产品
  products: {
    list: getProducts,
    get: getProduct,
    create: createProduct,
    update: updateProduct,
    delete: deleteProduct,
  },
  // 仓库
  warehouses: {
    list: getWarehouses,
    get: getWarehouse,
    create: createWarehouse,
    update: updateWarehouse,
    delete: deleteWarehouse,
  },
  // 库存
  inventories: {
    list: getInventories,
    transactions: getInventoryTransactions,
  },
  // 调拨
  transfers: {
    list: getInventoryTransfers,
    get: getInventoryTransfer,
    create: createInventoryTransfer,
    execute: executeInventoryTransfer,
    delete: deleteInventoryTransfer,
  },
};
