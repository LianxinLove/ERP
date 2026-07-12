/**
 * 采购申请页面
 *
 * @description 管理采购申请的CRUD和提交审批操作
 */

'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Plus, Send, Search, FileText, Eye, Pencil, Trash2 } from 'lucide-react';
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
  PurchaseRequest,
  PurchaseRequestDetail,
  CreatePurchaseRequestRequest,
  PurchaseRequestItem,
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
import { cn } from '@/lib/utils';

/**
 * 采购申请状态徽章
 */
function RequestStatusBadge({ status }: { status: PurchaseRequest['status'] }) {
  switch (status) {
    case 'draft':
      return <Badge variant="secondary">草稿</Badge>;
    case 'pending':
      return <Badge variant="warning">待审批</Badge>;
    case 'approved':
      return <Badge variant="success">已批准</Badge>;
    case 'rejected':
      return <Badge variant="destructive">已拒绝</Badge>;
    case 'converted':
      return <Badge variant="info">已转订单</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

/**
 * 采购申请明细表单项
 */
interface RequestItemFormProps {
  item: PurchaseRequestItem;
  index: number;
  onChange: (index: number, item: PurchaseRequestItem) => void;
  onRemove: (index: number) => void;
  showRemove?: boolean;
}

function RequestItemForm({ item, index, onChange, onRemove, showRemove }: RequestItemFormProps) {
  const handleChange = (field: keyof PurchaseRequestItem, value: any) => {
    onChange(index, { ...item, [field]: value });
  };

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

      {/* 预估单价 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">预估单价</Label>
        <Input
          type="number"
          step="0.01"
          value={item.estimated_price || ''}
          onChange={(e) => handleChange('estimated_price', parseFloat(e.target.value) || undefined)}
          placeholder="单价"
        />
      </div>

      {/* 预估金额 */}
      <div className="col-span-1 space-y-1">
        <Label className="text-xs">预估金额</Label>
        <Input
          value={((item.estimated_price || 0) * item.quantity).toFixed(2)}
          readOnly
          className="bg-muted"
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
 * 采购申请表单对话框
 */
interface RequestFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePurchaseRequestRequest) => void;
  request?: PurchaseRequestDetail;
  isSubmitting?: boolean;
}

function RequestFormDialog({ open, onClose, onSubmit, request, isSubmitting }: RequestFormDialogProps) {
  const isEdit = !!request;
  const [formData, setFormData] = useState<Omit<CreatePurchaseRequestRequest, 'items'>>({
    title: request?.title || '',
    request_date: request?.request_date || new Date().toISOString().split('T')[0],
    department_id: request?.department_id || undefined,
    reason: request?.reason || '',
  });

  const [items, setItems] = useState<PurchaseRequestItem[]>(
    request?.items.map((item) => ({
      product_code: item.product_code,
      product_name: item.product_name,
      specification: item.specification,
      unit: item.unit,
      quantity: item.quantity,
      estimated_price: item.estimated_price,
      estimated_amount: item.estimated_amount,
      notes: item.notes,
    })) || [{ product_name: '', quantity: 1 }]
  );

  const totalAmount = items.reduce(
    (sum, item) => sum + (item.estimated_price || 0) * item.quantity,
    0
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

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
      request_date: new Date(formData.request_date).toISOString(),
    });
  };

  const handleChange = (field: keyof typeof formData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleItemChange = (index: number, item: PurchaseRequestItem) => {
    setItems((prev) => {
      const newItems = [...prev];
      newItems[index] = item;
      return newItems;
    });
  };

  const handleAddItem = () => {
    setItems((prev) => [...prev, { product_name: '', quantity: 1 }]);
  };

  const handleRemoveItem = (index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto" onClose={onClose}>
        <DialogHeader>
          <DialogTitle>{isEdit ? '编辑采购申请' : '新建采购申请'}</DialogTitle>
          <DialogDescription>
            {isEdit ? '修改采购申请信息' : '填写采购申请基本信息和明细'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 基本信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="title">申请标题 *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="请输入申请标题"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="request_date">需求日期 *</Label>
              <Input
                id="request_date"
                type="date"
                value={formData.request_date.split('T')[0]}
                onChange={(e) => handleChange('request_date', e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="reason">申请原因</Label>
            <Textarea
              id="reason"
              value={formData.reason || ''}
              onChange={(e) => handleChange('reason', e.target.value)}
              placeholder="请说明采购原因"
              rows={3}
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
                <RequestItemForm
                  key={index}
                  item={item}
                  index={index}
                  onChange={handleItemChange}
                  onRemove={handleRemoveItem}
                  showRemove={items.length > 1}
                />
              ))}
            </div>

            <div className="flex justify-end">
              <div className="text-sm">
                总金额: <span className="font-semibold">¥{totalAmount.toFixed(2)}</span>
              </div>
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
 * 采购申请列表表格
 */
interface RequestsTableProps {
  requests: PurchaseRequest[];
  onView: (request: PurchaseRequest) => void;
  onEdit: (request: PurchaseRequest) => void;
  onDelete: (request: PurchaseRequest) => void;
  onSubmit: (request: PurchaseRequest) => void;
}

function RequestsTable({ requests, onView, onEdit, onDelete, onSubmit }: RequestsTableProps) {
  if (requests.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <FileText className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">暂无采购申请</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>申请单号</TableHead>
          <TableHead>标题</TableHead>
          <TableHead>需求日期</TableHead>
          <TableHead>总金额</TableHead>
          <TableHead>状态</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {requests.map((request) => (
          <TableRow key={request.id}>
            <TableCell className="font-medium">{request.request_no}</TableCell>
            <TableCell>{request.title}</TableCell>
            <TableCell>
              {format(new Date(request.request_date), 'yyyy-MM-dd')}
            </TableCell>
            <TableCell>
              {request.total_amount ? `¥${request.total_amount.toLocaleString()}` : '-'}
            </TableCell>
            <TableCell>
              <RequestStatusBadge status={request.status} />
            </TableCell>
            <TableCell>
              {format(new Date(request.created_at), 'yyyy-MM-dd HH:mm')}
            </TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-1">
                <Button variant="ghost" size="sm" onClick={() => onView(request)}>
                  <Eye className="w-4 h-4" />
                </Button>
                {request.status === 'draft' && (
                  <>
                    <Button variant="ghost" size="sm" onClick={() => onEdit(request)}>
                      <Pencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onDelete(request)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onSubmit(request)}
                      className="text-primary hover:text-primary"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </>
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
function RequestsSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>申请单号</TableHead>
          <TableHead>标题</TableHead>
          <TableHead>需求日期</TableHead>
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
            <TableCell><Skeleton className="h-5 w-32" /></TableCell>
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
export default function PurchaseRequestsPage() {
  const queryClient = useQueryClient();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRequest, setEditingRequest] = useState<PurchaseRequestDetail | undefined>();

  // 获取采购申请列表
  const {
    data: requests = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['purchase', 'requests', searchKeyword],
    queryFn: () => purchaseApi.getRequests({ keyword: searchKeyword }),
  });

  // 获取申请详情（用于编辑）
  const { data: detailRequest } = useQuery({
    queryKey: ['purchase', 'requests', 'detail', editingRequest?.id],
    queryFn: () => purchaseApi.getRequest(editingRequest!.id),
    enabled: !!editingRequest && isFormOpen,
  });

  // 创建采购申请
  const createMutation = useMutation({
    mutationFn: (data: CreatePurchaseRequestRequest) => purchaseApi.createRequest(data),
    onSuccess: () => {
      toast.success('采购申请创建成功');
      setIsFormOpen(false);
      setEditingRequest(undefined);
      queryClient.invalidateQueries({ queryKey: ['purchase', 'requests'] });
    },
    onError: (error) => {
      toast.error('创建失败：' + (error as Error).message);
    },
  });

  // 提交审批
  const submitMutation = useMutation({
    mutationFn: (requestId: number) => purchaseApi.submitRequest(requestId),
    onSuccess: () => {
      toast.success('采购申请已提交审批');
      queryClient.invalidateQueries({ queryKey: ['purchase', 'requests'] });
    },
    onError: (error) => {
      toast.error('提交失败：' + (error as Error).message);
    },
  });

  // 删除采购申请
  const deleteMutation = useMutation({
    mutationFn: (requestId: number) => purchaseApi.deleteRequest(requestId),
    onSuccess: () => {
      toast.success('采购申请删除成功');
      queryClient.invalidateQueries({ queryKey: ['purchase', 'requests'] });
    },
    onError: (error) => {
      toast.error('删除失败：' + (error as Error).message);
    },
  });

  // 处理表单提交
  const handleFormSubmit = (data: CreatePurchaseRequestRequest) => {
    createMutation.mutate(data);
  };

  // 处理查看
  const handleView = (request: PurchaseRequest) => {
    // TODO: 打开详情对话框或跳转到详情页
    toast.info('查看详情功能开发中');
  };

  // 处理编辑
  const handleEdit = (request: PurchaseRequest) => {
    setEditingRequest(undefined); // 先清空，让query自动获取详情
    setTimeout(() => {
      setEditingRequest({ ...request, items: [] }); // 设置后query会自动填充
      setIsFormOpen(true);
    }, 0);
  };

  // 处理删除
  const handleDelete = (request: PurchaseRequest) => {
    if (confirm(`确定要删除采购申请「${request.title}」吗？`)) {
      deleteMutation.mutate(request.id);
    }
  };

  // 处理提交审批
  const handleSubmit = (request: PurchaseRequest) => {
    if (confirm(`确定要提交采购申请「${request.title}」进行审批吗？`)) {
      submitMutation.mutate(request.id);
    }
  };

  // 处理新建
  const handleNew = () => {
    setEditingRequest(undefined);
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
          <h1 className="text-3xl font-bold tracking-tight">采购申请</h1>
          <p className="text-muted-foreground mt-1">
            创建和管理采购申请，提交审批流程
          </p>
        </div>
        <Button onClick={handleNew}>
          <Plus className="w-4 h-4 mr-2" />
          新建申请
        </Button>
      </div>

      {/* 搜索栏 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Input
              placeholder="搜索申请单号、标题..."
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

      {/* 采购申请列表 */}
      <Card>
        <CardHeader>
          <CardTitle>采购申请列表</CardTitle>
          <CardDescription>
            共 {requests.length} 个申请
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <RequestsSkeleton />
          ) : error ? (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>加载失败</AlertTitle>
              <AlertDescription>
                加载采购申请列表失败，请稍后重试。
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
            <RequestsTable
              requests={requests}
              onView={handleView}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onSubmit={handleSubmit}
            />
          )}
        </CardContent>
      </Card>

      {/* 表单对话框 */}
      <RequestFormDialog
        open={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingRequest(undefined);
        }}
        onSubmit={handleFormSubmit}
        request={detailRequest || editingRequest}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
