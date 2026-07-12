/**
 * 采购订单页面
 *
 * @description 管理采购订单的CRUD和状态流转操作
 */

'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Plus, Search, ShoppingBag, Eye, Pencil, Trash2, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { purchaseApi } from '@/api/purchase';
import type {
  PurchaseOrder,
  PurchaseOrderDetail,
  CreatePurchaseOrderRequest,
  PurchaseOrderItem,
  Supplier,
} from '@/types/purchase';
import { toast } from 'sonner';
import { AlertCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';

/**
 * 采购订单状态徽章
 */
function OrderStatusBadge({ status }: { status: PurchaseOrder['status'] }) {
  switch (status) {
    case 'draft':
      return <Badge variant="secondary">草稿</Badge>;
    case 'pending':
      return <Badge variant="warning">待审核</Badge>;
    case 'confirmed':
      return <Badge variant="info">已确认</Badge>;
    case 'partial_received':
      return <Badge variant="default">部分收货</Badge>;
    case 'received':
      return <Badge variant="success">已收货</Badge>;
    case 'cancelled':
      return <Badge variant="destructive">已取消</Badge>;
    case 'closed':
      return <Badge variant="outline">已关闭</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

/**
 * 采购订单明细表单项
 */
interface OrderItemFormProps {
  item: PurchaseOrderItem;
  index: number;
  onChange: (index: number, item: PurchaseOrderItem) => void;
  onRemove: (index: number) => void;
  showRemove?: boolean;
}

function OrderItemForm({ item, index, onChange, onRemove, showRemove }: OrderItemFormProps) {
  const handleChange = (field: keyof PurchaseOrderItem, value: any) => {
    onChange(index, { ...item, [field]: value });
  };

  const amount = (item.unit_price || 0) * item.quantity;
  const taxAmount = item.tax_rate ? amount * (item.tax_rate / 100) : 0;

  return (
    <div className="grid grid-cols-12 gap-2 items-start">
      {/* 产品名称 */}
      <div className="col-span-3 space-y-1">
        <Label className="text-xs">产品名称 *</Label>
        <Input
          value={item.product_name}
          onChange={(e) => handleChange('product_name', e.target.value)}
          placeholder="产品名称"
          required
        />
      </div>

      {/* 规格型号 */}
      <div className="col-span-2 space-y-1">
        <Label className="text-xs">规格型号</Label>
        <Input
          value={item.specification || ''}
          onChange={(e) => handleChange('specification', e.target.value)}
          placeholder="规格"
        />
      </div>

      {/* 单位 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">单位</Label>
        <Input
          value={item.unit || ''}
          onChange={(e) => handleChange('unit', e.target.value)}
          placeholder="单位"
        />
      </div>

      {/* 数量 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">数量 *</Label>
        <Input
          type="number"
          step="0.01"
          value={item.quantity}
          onChange={(e) => handleChange('quantity', parseFloat(e.target.value) || 0)}
          placeholder="数量"
          required
        />
      </div>

      {/* 单价 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">单价 *</Label>
        <Input
          type="number"
          step="0.01"
          value={item.unit_price || ''}
          onChange={(e) => handleChange('unit_price', parseFloat(e.target.value) || undefined)}
          placeholder="单价"
          required
        />
      </div>

      {/* 金额 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">金额</Label>
        <Input
          value={amount.toFixed(2)}
          readOnly
          className="bg-muted"
        />
      </div>

      {/* 税率 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">税率(%)</Label>
        <Input
          type="number"
          step="0.01"
          value={item.tax_rate || ''}
          onChange={(e) => handleChange('tax_rate', parseFloat(e.target.value) || undefined)}
          placeholder="税率"
        />
      </div>

      {/* 备注 */}
      <div className="col-span-2 space-y-1">
        <Label className="text-xs">备注</Label>
        <Input
          value={item.notes || ''}
          onChange={(e) => handleChange('notes', e.target.value)}
          placeholder="备注"
        />
      </div>

      {/* 删除按钮 */}
      <div className="col-span-1 flex items-end">
        {showRemove && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => onRemove(index)}
            className="w-full"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
}

/**
 * 采购订单表单对话框
 */
interface OrderFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePurchaseOrderRequest) => void;
  order?: PurchaseOrderDetail;
  suppliers?: Supplier[];
  isSubmitting?: boolean;
}

function OrderFormDialog({ open, onClose, onSubmit, order, suppliers, isSubmitting }: OrderFormDialogProps) {
  const isEdit = !!order;
  const [formData, setFormData] = useState<Omit<CreatePurchaseOrderRequest, 'items'>>({
    supplier_id: order?.supplier_id || 0,
    order_date: order?.order_date || new Date().toISOString().split('T')[0],
    expected_date: order?.expected_date?.split('T')[0] || '',
    tax_inclusive: order?.tax_inclusive || false,
    payment_terms: order?.payment_terms || undefined,
    delivery_address: order?.delivery_address || '',
    contact: order?.contact || '',
    contact_phone: order?.contact_phone || '',
    notes: order?.notes || '',
  });

  const [items, setItems] = useState<PurchaseOrderItem[]>(
    order?.items.map((item) => ({
      product_code: item.product_code,
      product_name: item.product_name,
      specification: item.specification,
      unit: item.unit,
      quantity: item.quantity,
      unit_price: item.unit_price,
      amount: item.amount,
      tax_rate: item.tax_rate,
      notes: item.notes,
    })) || [{ product_name: '', quantity: 1, unit_price: 0 }]
  );

  const totalAmount = items.reduce(
    (sum, item) => {
      const amount = (item.unit_price || 0) * item.quantity;
      if (formData.tax_inclusive && item.tax_rate) {
        // 含税，计算不含税金额
        return sum + amount / (1 + item.tax_rate / 100);
      }
      return sum + amount;
    },
    0
  );

  const totalTax = items.reduce(
    (sum, item) => {
      const amount = (item.unit_price || 0) * item.quantity;
      if (formData.tax_inclusive && item.tax_rate) {
        return sum + (amount - amount / (1 + item.tax_rate / 100));
      } else if (item.tax_rate) {
        return sum + amount * (item.tax_rate / 100);
      }
      return sum;
    },
    0
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.supplier_id) {
      toast.error('请选择供应商');
      return;
    }

    if (items.length === 0) {
      toast.error('请至少添加一项采购明细');
      return;
    }

    const validItems = items.filter((item) => item.product_name && item.quantity > 0);

    if (validItems.length === 0) {
      toast.error('请完善采购明细信息');
      return;
    }

    onSubmit({
      ...formData,
      items: validItems,
      order_date: new Date(formData.order_date).toISOString(),
      expected_date: formData.expected_date ? new Date(formData.expected_date).toISOString() : undefined,
    });
  };

  const handleChange = (field: keyof typeof formData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleItemChange = (index: number, item: PurchaseOrderItem) => {
    setItems((prev) => {
      const newItems = [...prev];
      newItems[index] = item;
      return newItems;
    });
  };

  const handleAddItem = () => {
    setItems((prev) => [...prev, { product_name: '', quantity: 1, unit_price: 0 }]);
  };

  const handleRemoveItem = (index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto" onClose={onClose}>
        <DialogHeader>
          <DialogTitle>{isEdit ? '编辑采购订单' : '新建采购订单'}</DialogTitle>
          <DialogDescription>
            {isEdit ? '修改采购订单信息' : '填写采购订单基本信息和明细'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 基本信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="supplier_id">供应商 *</Label>
              <Select
                value={formData.supplier_id?.toString()}
                onValueChange={(value) => handleChange('supplier_id', parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="请选择供应商" />
                </SelectTrigger>
                <SelectContent>
                  {suppliers?.map((supplier) => (
                    <SelectItem key={supplier.id} value={supplier.id.toString()}>
                      {supplier.code} - {supplier.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="order_date">订单日期 *</Label>
              <Input
                id="order_date"
                type="date"
                value={formData.order_date.split('T')[0]}
                onChange={(e) => handleChange('order_date', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="expected_date">预计到货日期</Label>
              <Input
                id="expected_date"
                type="date"
                value={formData.expected_date || ''}
                onChange={(e) => handleChange('expected_date', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="payment_terms">付款条件（天数）</Label>
              <Input
                id="payment_terms"
                type="number"
                value={formData.payment_terms || ''}
                onChange={(e) => handleChange('payment_terms', parseInt(e.target.value) || undefined)}
                placeholder="如: 30"
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="tax_inclusive"
              checked={formData.tax_inclusive}
              onChange={(e) => handleChange('tax_inclusive', e.target.checked)}
              className="h-4 w-4"
            />
            <Label htmlFor="tax_inclusive" className="cursor-pointer">
              单价含税
            </Label>
          </div>

          <div className="space-y-2">
            <Label htmlFor="delivery_address">送货地址</Label>
            <Input
              id="delivery_address"
              value={formData.delivery_address || ''}
              onChange={(e) => handleChange('delivery_address', e.target.value)}
              placeholder="请输入送货地址"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact">联系人</Label>
              <Input
                id="contact"
                value={formData.contact || ''}
                onChange={(e) => handleChange('contact', e.target.value)}
                placeholder="请输入联系人"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact_phone">联系电话</Label>
              <Input
                id="contact_phone"
                value={formData.contact_phone || ''}
                onChange={(e) => handleChange('contact_phone', e.target.value)}
                placeholder="请输入联系电话"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">备注</Label>
            <Textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="请输入备注信息"
              rows={2}
            />
          </div>

          {/* 采购明细 */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>采购明细 *</Label>
              <Button type="button" variant="outline" size="sm" onClick={handleAddItem}>
                <Plus className="w-4 h-4 mr-1" />
                添加明细
              </Button>
            </div>

            <div className="space-y-2">
              {items.map((item, index) => (
                <OrderItemForm
                  key={index}
                  item={item}
                  index={index}
                  onChange={handleItemChange}
                  onRemove={handleRemoveItem}
                  showRemove={items.length > 1}
                />
              ))}
            </div>

            <div className="flex justify-end gap-4 text-sm">
              <span>不含税金额: <span className="font-semibold">¥{(totalAmount - totalTax).toFixed(2)}</span></span>
              <span>税额: <span className="font-semibold">¥{totalTax.toFixed(2)}</span></span>
              <span>总金额: <span className="font-semibold">¥{totalAmount.toFixed(2)}</span></span>
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              取消
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '提交中...' : isEdit ? '保存' : '创建'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

/**
 * 采购订单列表表格
 */
interface OrdersTableProps {
  orders: PurchaseOrder[];
  onView: (order: PurchaseOrder) => void;
  onEdit: (order: PurchaseOrder) => void;
  onDelete: (order: PurchaseOrder) => void;
  onConfirm: (order: PurchaseOrder) => void;
  onCancel: (order: PurchaseOrder) => void;
}

function OrdersTable({ orders, onView, onEdit, onDelete, onConfirm, onCancel }: OrdersTableProps) {
  if (orders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <ShoppingBag className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">暂无采购订单</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>订单号</TableHead>
          <TableHead>供应商ID</TableHead>
          <TableHead>订单日期</TableHead>
          <TableHead>预计到货日期</TableHead>
          <TableHead>总金额</TableHead>
          <TableHead>状态</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {orders.map((order) => (
          <TableRow key={order.id}>
            <TableCell className="font-medium">{order.order_no}</TableCell>
            <TableCell>{order.supplier_id}</TableCell>
            <TableCell>
              {format(new Date(order.order_date), 'yyyy-MM-dd')}
            </TableCell>
            <TableCell>
              {order.expected_date
                ? format(new Date(order.expected_date), 'yyyy-MM-dd')
                : '-'}
            </TableCell>
            <TableCell>
              {order.total_amount ? `¥${order.total_amount.toLocaleString()}` : '-'}
            </TableCell>
            <TableCell>
              <OrderStatusBadge status={order.status} />
            </TableCell>
            <TableCell>
              {format(new Date(order.created_at), 'yyyy-MM-dd')}
            </TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-1">
                <Button variant="ghost" size="sm" onClick={() => onView(order)}>
                  <Eye className="w-4 h-4" />
                </Button>
                {order.status === 'draft' && (
                  <>
                    <Button variant="ghost" size="sm" onClick={() => onEdit(order)}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(order)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onConfirm(order)}
                      className="text-green-600 hover:text-green-600"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </Button>
                  </>
                )}
                {order.status === 'confirmed' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onCancel(order)}
                    className="text-destructive hover:text-destructive"
                  >
                    <XCircle className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/**
 * 加载骨架屏
 */
function OrdersSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>订单号</TableHead>
          <TableHead>供应商ID</TableHead>
          <TableHead>订单日期</TableHead>
          <TableHead>预计到货日期</TableHead>
          <TableHead>总金额</TableHead>
          <TableHead>状态</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3, 4, 5].map((i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-16" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
            <TableCell><Skeleton className="h-5 w-16" /></TableCell>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-32" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/**
 * 页面主体
 */
export default function PurchaseOrdersPage() {
  const queryClient = useQueryClient();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<PurchaseOrderDetail | undefined>();

  // 获取供应商列表
  const { data: suppliers = [] } = useQuery({
    queryKey: ['purchase', 'suppliers'],
    queryFn: () => purchaseApi.getSuppliers(),
  });

  // 获取采购订单列表
  const {
    data: orders = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['purchase', 'orders', searchKeyword],
    queryFn: () => purchaseApi.getOrders({ keyword: searchKeyword }),
  });

  // 获取订单详情（用于编辑）
  const { data: detailOrder } = useQuery({
    queryKey: ['purchase', 'orders', 'detail', editingOrder?.id],
    queryFn: () => purchaseApi.getOrder(editingOrder!.id),
    enabled: !!editingOrder && isFormOpen,
  });

  // 创建采购订单
  const createMutation = useMutation({
    mutationFn: (data: CreatePurchaseOrderRequest) => purchaseApi.createOrder(data),
    onSuccess: () => {
      toast.success('采购订单创建成功');
      setIsFormOpen(false);
      setEditingOrder(undefined);
      queryClient.invalidateQueries({ queryKey: ['purchase', 'orders'] });
    },
    onError: (error) => {
      toast.error('创建失败：' + (error as Error).message);
    },
  });

  // 确认订单
  const confirmMutation = useMutation({
    mutationFn: (orderId: number) => purchaseApi.confirmOrder(orderId),
    onSuccess: () => {
      toast.success('采购订单已确认');
      queryClient.invalidateQueries({ queryKey: ['purchase', 'orders'] });
    },
    onError: (error) => {
      toast.error('确认失败：' + (error as Error).message);
    },
  });

  // 取消订单
  const cancelMutation = useMutation({
    mutationFn: (orderId: number) => purchaseApi.cancelOrder(orderId),
    onSuccess: () => {
      toast.success('采购订单已取消');
      queryClient.invalidateQueries({ queryKey: ['purchase', 'orders'] });
    },
    onError: (error) => {
      toast.error('取消失败：' + (error as Error).message);
    },
  });

  // 删除采购订单
  const deleteMutation = useMutation({
    mutationFn: (orderId: number) => purchaseApi.deleteOrder(orderId),
    onSuccess: () => {
      toast.success('采购订单删除成功');
      queryClient.invalidateQueries({ queryKey: ['purchase', 'orders'] });
    },
    onError: (error) => {
      toast.error('删除失败：' + (error as Error).message);
    },
  });

  // 处理表单提交
  const handleFormSubmit = (data: CreatePurchaseOrderRequest) => {
    createMutation.mutate(data);
  };

  // 处理查看
  const handleView = (order: PurchaseOrder) => {
    toast.info('查看详情功能开发中');
  };

  // 处理编辑
  const handleEdit = (order: PurchaseOrder) => {
    setEditingOrder(undefined);
    setTimeout(() => {
      setEditingOrder({ ...order, items: [], supplier: undefined });
      setIsFormOpen(true);
    }, 0);
  };

  // 处理删除
  const handleDelete = (order: PurchaseOrder) => {
    if (confirm(`确定要删除采购订单「${order.order_no}」吗？`)) {
      deleteMutation.mutate(order.id);
    }
  };

  // 处理确认
  const handleConfirm = (order: PurchaseOrder) => {
    if (confirm(`确定要确认采购订单「${order.order_no}」吗？`)) {
      confirmMutation.mutate(order.id);
    }
  };

  // 处理取消
  const handleCancel = (order: PurchaseOrder) => {
    if (confirm(`确定要取消采购订单「${order.order_no}」吗？`)) {
      cancelMutation.mutate(order.id);
    }
  };

  // 处理新建
  const handleNew = () => {
    setEditingOrder(undefined);
    setIsFormOpen(true);
  };

  // 处理搜索
  const handleSearch = () => {
    refetch();
  };

  const isSubmitting = createMutation.isPending;

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">采购订单</h1>
          <p className="text-muted-foreground mt-1">
            管理采购订单，跟踪订单状态
          </p>
        </div>
        <Button onClick={handleNew}>
          <Plus className="w-4 h-4 mr-2" />
          新建订单
        </Button>
      </div>

      {/* 搜索栏 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Input
              placeholder="搜索订单号..."
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="max-w-sm"
            />
            <Button onClick={handleSearch} variant="outline">
              <Search className="w-4 h-4 mr-2" />
              搜索
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 采购订单列表 */}
      <Card>
        <CardHeader>
          <CardTitle>采购订单列表</CardTitle>
          <CardDescription>
            共 {orders.length} 个订单
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <OrdersSkeleton />
          ) : error ? (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>加载失败</AlertTitle>
              <AlertDescription>
                加载采购订单列表失败，请稍后重试。
                <Button
                  variant="outline"
                  size="sm"
                  className="ml-2"
                  onClick={() => refetch()}
                >
                  重试
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <OrdersTable
              orders={orders}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onConfirm={handleConfirm}
              onCancel={handleCancel}
            />
          )}
        </CardContent>
      </Card>

      {/* 表单对话框 */}
      <OrderFormDialog
        open={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingOrder(undefined);
        }}
        onSubmit={handleFormSubmit}
        order={detailOrder || editingOrder}
        suppliers={suppliers}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
