/**
 * 库存管理类型定义
 * @description 库存模块的 TypeScript 类型接口
 */

// ============ 枚举类型 ============

/**
 * 产品状态
 */
export enum ProductStatus {
  ACTIVE = 'active',           // 正常
  DISCONTINUED = 'discontinued', // 停产
  OBSOLETE = 'obsolete',        // 淘汰
}

/**
 * 库存流水类型
 */
export enum TransactionType {
  PURCHASE_IN = 'purchase_in',         // 采购入库
  PURCHASE_RETURN = 'purchase_return', // 采购退货
  SALES_OUT = 'sales_out',             // 销售出库
  SALES_RETURN = 'sales_return',       // 销售退货
  TRANSFER_IN = 'transfer_in',         // 调拨入库
  TRANSFER_OUT = 'transfer_out',       // 调拨出库
  ADJUSTMENT_IN = 'adjustment_in',     // 盘盈
  ADJUSTMENT_OUT = 'adjustment_out',   // 盘亏
  OTHER_IN = 'other_in',               // 其他入库
  OTHER_OUT = 'other_out',             // 其他出库
}

/**
 * 调拨状态
 */
export enum TransferStatus {
  DRAFT = 'draft',           // 草稿
  PENDING = 'pending',       // 待审核
  APPROVED = 'approved',     // 已批准
  REJECTED = 'rejected',     // 已拒绝
  IN_TRANSIT = 'in_transit', // 调拨中
  COMPLETED = 'completed',   // 已完成
  CANCELLED = 'cancelled',   // 已取消
}

// ============ 产品相关 ============

/**
 * 产品基础信息
 */
export interface ProductBase {
  code: string;               // 产品编码
  name: string;               // 产品名称
  specification?: string;     // 规格型号
  unit?: string;              // 单位
  category?: string;          // 分类
  barcode?: string;           // 条码
  cost_price?: number;        // 成本价
  selling_price?: number;     // 销售价
  min_stock?: number;         // 最小库存
  max_stock?: number;         // 最大库存
  lead_time?: number;         // 采购提前期（天）
  notes?: string;             // 备注
}

/**
 * 创建产品请求
 */
export interface ProductCreate extends ProductBase {
  status?: ProductStatus;
}

/**
 * 更新产品请求
 */
export interface ProductUpdate {
  name?: string;
  specification?: string;
  unit?: string;
  category?: string;
  barcode?: string;
  cost_price?: number;
  selling_price?: number;
  min_stock?: number;
  max_stock?: number;
  lead_time?: number;
  notes?: string;
  status?: ProductStatus;
}

/**
 * 产品响应
 */
export interface Product extends ProductBase {
  id: number;
  status: ProductStatus;
  created_at: string;
  updated_at: string;
}

// ============ 仓库相关 ============

/**
 * 仓库基础信息
 */
export interface WarehouseBase {
  code: string;               // 仓库编码
  name: string;               // 仓库名称
  address?: string;           // 地址
  manager_id?: number;        // 负责人ID
  contact?: string;           // 联系电话
  capacity?: number;          // 容量
  notes?: string;             // 备注
}

/**
 * 创建仓库请求
 */
export interface WarehouseCreate extends WarehouseBase {}

/**
 * 更新仓库请求
 */
export interface WarehouseUpdate {
  name?: string;
  address?: string;
  manager_id?: number;
  contact?: string;
  capacity?: number;
  notes?: string;
}

/**
 * 仓库响应
 */
export interface Warehouse extends WarehouseBase {
  id: number;
  created_at: string;
  updated_at: string;
}

// ============ 库存相关 ============

/**
 * 库存响应
 */
export interface Inventory {
  id: number;
  warehouse_id: number;
  product_id: number;
  quantity: number;
  allocated_quantity: number;
  available_quantity: number;
  last_updated?: string;
}

/**
 * 库存详情（含关联信息）
 */
export interface InventoryDetail {
  id: number;
  warehouse_id: number;
  warehouse_name?: string;
  product_id: number;
  product_code?: string;
  product_name?: string;
  quantity: number;
  allocated_quantity: number;
  available_quantity: number;
  last_updated?: string;
}

/**
 * 库存查询参数
 */
export interface InventoryQueryParams {
  warehouse_id?: number;
  product_id?: number;
  low_stock_only?: boolean;
  skip?: number;
  limit?: number;
}

// ============ 库存流水相关 ============

/**
 * 库存流水响应
 */
export interface InventoryTransaction {
  id: number;
  warehouse_id: number;
  product_id: number;
  transaction_type: TransactionType;
  quantity: number;
  before_quantity?: number;
  after_quantity?: number;
  reference_type?: string;
  reference_id?: number;
  reference_no?: string;
  notes?: string;
  created_by?: number;
  created_at: string;
}

/**
 * 流水查询参数
 */
export interface TransactionQueryParams {
  warehouse_id?: number;
  product_id?: number;
  transaction_type?: TransactionType;
  skip?: number;
  limit?: number;
}

// ============ 库存调拨相关 ============

/**
 * 调拨明细基础信息
 */
export interface TransferItemBase {
  product_id: number;
  quantity: number;
  notes?: string;
}

/**
 * 创建调拨明细
 */
export interface TransferItemCreate extends TransferItemBase {}

/**
 * 调拨明细响应
 */
export interface TransferItemResponse extends TransferItemBase {
  id: number;
}

/**
 * 调拨基础信息
 */
export interface TransferBase {
  from_warehouse_id: number;
  to_warehouse_id: number;
  transfer_date: string;
  notes?: string;
}

/**
 * 创建调拨请求
 */
export interface InventoryTransferCreate extends TransferBase {
  items: TransferItemCreate[];
}

/**
 * 更新调拨请求
 */
export interface InventoryTransferUpdate {
  from_warehouse_id?: number;
  to_warehouse_id?: number;
  transfer_date?: string;
  notes?: string;
  items?: TransferItemCreate[];
  status?: TransferStatus;
}

/**
 * 调拨响应
 */
export interface InventoryTransfer extends TransferBase {
  id: number;
  transfer_no: string;
  status: TransferStatus;
  created_at: string;
  updated_at: string;
}

/**
 * 调拨详情（含明细）
 */
export interface InventoryTransferDetail extends InventoryTransfer {
  items: TransferItemResponse[];
}

/**
 * 调拨查询参数
 */
export interface TransferQueryParams {
  status?: TransferStatus;
  skip?: number;
  limit?: number;
}

// ============ 辅助类型 ============

/**
 * 产品状态标签
 */
export const ProductStatusLabels: Record<ProductStatus, string> = {
  [ProductStatus.ACTIVE]: '正常',
  [ProductStatus.DISCONTINUED]: '停产',
  [ProductStatus.OBSOLETE]: '淘汰',
};

/**
 * 产品状态颜色
 */
export const ProductStatusColors: Record<ProductStatus, string> = {
  [ProductStatus.ACTIVE]: 'default',
  [ProductStatus.DISCONTINUED]: 'secondary',
  [ProductStatus.OBSOLETE]: 'destructive',
} as const;

/**
 * 流水类型标签
 */
export const TransactionTypeLabels: Record<TransactionType, string> = {
  [TransactionType.PURCHASE_IN]: '采购入库',
  [TransactionType.PURCHASE_RETURN]: '采购退货',
  [TransactionType.SALES_OUT]: '销售出库',
  [TransactionType.SALES_RETURN]: '销售退货',
  [TransactionType.TRANSFER_IN]: '调拨入库',
  [TransactionType.TRANSFER_OUT]: '调拨出库',
  [TransactionType.ADJUSTMENT_IN]: '盘盈',
  [TransactionType.ADJUSTMENT_OUT]: '盘亏',
  [TransactionType.OTHER_IN]: '其他入库',
  [TransactionType.OTHER_OUT]: '其他出库',
};

/**
 * 流水类型颜色（入库为绿色，出库为红色）
 */
export const TransactionTypeColors: Record<TransactionType, 'default' | 'success' | 'destructive'> = {
  [TransactionType.PURCHASE_IN]: 'success',
  [TransactionType.PURCHASE_RETURN]: 'destructive',
  [TransactionType.SALES_OUT]: 'destructive',
  [TransactionType.SALES_RETURN]: 'success',
  [TransactionType.TRANSFER_IN]: 'success',
  [TransactionType.TRANSFER_OUT]: 'destructive',
  [TransactionType.ADJUSTMENT_IN]: 'success',
  [TransactionType.ADJUSTMENT_OUT]: 'destructive',
  [TransactionType.OTHER_IN]: 'default',
  [TransactionType.OTHER_OUT]: 'default',
};

/**
 * 调拨状态标签
 */
export const TransferStatusLabels: Record<TransferStatus, string> = {
  [TransferStatus.DRAFT]: '草稿',
  [TransferStatus.PENDING]: '待审核',
  [TransferStatus.APPROVED]: '已批准',
  [TransferStatus.REJECTED]: '已拒绝',
  [TransferStatus.IN_TRANSIT]: '调拨中',
  [TransferStatus.COMPLETED]: '已完成',
  [TransferStatus.CANCELLED]: '已取消',
};

/**
 * 调拨状态颜色
 */
export const TransferStatusColors: Record<TransferStatus, 'default' | 'secondary' | 'destructive' | 'success'> = {
  [TransferStatus.DRAFT]: 'default',
  [TransferStatus.PENDING]: 'secondary',
  [TransferStatus.APPROVED]: 'default',
  [TransferStatus.REJECTED]: 'destructive',
  [TransferStatus.IN_TRANSIT]: 'secondary',
  [TransferStatus.COMPLETED]: 'success',
  [TransferStatus.CANCELLED]: 'destructive',
} as const;
