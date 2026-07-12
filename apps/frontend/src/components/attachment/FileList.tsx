/**
 * 文件列表组件
 * @description 显示关联到某个实体的附件列表
 */

"use client";

import { useEffect, useState } from "react";
import { FilePreview } from "./FilePreview";
import { FileUploader } from "./FileUploader";
import { Attachment, AttachmentQuery } from "@/types/attachment";
import { attachmentAPI } from "@/api/attachment";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, File, Plus, Trash2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { confirm } from "@/lib/ui-helpers";

interface FileListProps {
  /** 实体类型（如 purchase_order, sales_order） */
  entityType?: string;
  /** 实体ID */
  entityId?: number;
  /** 分类ID */
  categoryId?: number;
  /** 是否只读 */
  readonly?: boolean;
  /** 是否显示上传按钮 */
  showUpload?: boolean;
  /** 自定义类名 */
  className?: string;
  /** 文件列表变化回调 */
  onChange?: (attachments: Attachment[]) => void;
}

/**
 * 文件列表组件
 *
 * @features
 * - 显示关联实体的所有附件
 * - 支持上传新附件
 * - 支持删除附件
 * - 支持预览和下载
 * - 响应式网格布局
 *
 * @example
 * ```tsx
 * <FileList
 *   entityType="purchase_order"
 *   entityId={123}
 *   showUpload
 *   onChange={(attachments) => console.log(attachments)}
 * />
 * ```
 */
export function FileList({
  entityType,
  entityId,
  categoryId,
  readonly = false,
  showUpload = true,
  className = "",
  onChange,
}: FileListProps) {
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  /**
   * 获取附件列表
   */
  const fetchAttachments = async () => {
    if (!entityType && !entityId) {
      setAttachments([]);
      return;
    }

    setLoading(true);
    try {
      const query: AttachmentQuery = {
        entity_type: entityType,
        entity_id: entityId,
        category_id: categoryId,
        page: 1,
        page_size: 100,
      };

      const response = await attachmentAPI.getAttachments(query);
      setAttachments(response.items);
      onChange?.(response.items);
    } catch (error) {
      console.error("获取附件列表失败:", error);
      toast.error("获取附件列表失败");
    } finally {
      setLoading(false);
    }
  };

  /**
   * 上传成功回调
   */
  const handleUploadSuccess = () => {
    fetchAttachments();
    setUploadDialogOpen(false);
  };

  /**
   * 删除附件
   */
  const handleDelete = async (attachment: Attachment) => {
    const confirmed = await confirm({
      title: "确认删除",
      message: `确定要删除文件"${attachment.original_name}"吗？`,
      confirmText: "删除",
      cancelText: "取消",
    });

    if (!confirmed) return;

    try {
      await attachmentAPI.deleteAttachment(attachment.id);
      toast.success("删除成功");
      fetchAttachments();
    } catch (error) {
      console.error("删除失败:", error);
      toast.error("删除失败");
    }
  };

  // 初始化加载
  useEffect(() => {
    fetchAttachments();
  }, [entityType, entityId, categoryId]);

  // 统计信息
  const totalSize = attachments.reduce((sum, a) => sum + a.file_size, 0);
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3 className="font-semibold">附件</h3>
          <Badge variant="secondary">{attachments.length} 个文件</Badge>
          {attachments.length > 0 && (
            <span className="text-sm text-muted-foreground">
              总大小: {formatFileSize(totalSize)}
            </span>
          )}
        </div>

        {showUpload && !readonly && (
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Plus className="h-4 w-4 mr-2" />
                上传附件
              </Button>
            </DialogTrigger>
            <DialogContent onClose={() => setUploadDialogOpen(false)}>
              <DialogHeader>
                <DialogTitle>上传附件</DialogTitle>
              </DialogHeader>
              <FileUploader
                uploadData={{
                  entity_type: entityType,
                  entity_id: entityId,
                  category_id: categoryId,
                }}
                onSuccess={handleUploadSuccess}
              />
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* 文件列表 */}
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : attachments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg border-dashed">
          <File className="h-12 w-12 text-muted-foreground mb-3" />
          <p className="text-sm text-muted-foreground mb-1">暂无附件</p>
          {!readonly && showUpload && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setUploadDialogOpen(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              上传第一个附件
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {attachments.map((attachment) => (
            <div key={attachment.id} className="group relative">
              <FilePreview attachment={attachment} />

              {/* 删除按钮（悬浮显示） */}
              {!readonly && (
                <button
                  onClick={() => handleDelete(attachment)}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  title="删除"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
