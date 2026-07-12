/**
 * 文件预览组件
 * @description 支持图片、PDF、Office文档等多种文件类型的预览
 */

"use client";

import { useState } from "react";
import {
  File,
  Image as ImageIcon,
  FileText,
  Archive,
  Music,
  Video,
  FileCode,
  Download,
  ExternalLink,
  X,
  ZoomIn,
  ZoomOut,
  RotateCw,
} from "lucide-react";
import { Attachment } from "@/types/attachment";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { attachmentAPI } from "@/api/attachment";
import { toast } from "sonner";

interface FilePreviewProps {
  /** 附件信息 */
  attachment: Attachment;
  /** 是否显示下载按钮 */
  showDownload?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 文件预览组件
 *
 * @features
 * - 支持图片预览
 * - 支持PDF预览
 * - 显示文件信息
 * - 下载功能
 * - 缩放和旋转（图片）
 *
 * @example
 * ```tsx
 * <FilePreview
 *   attachment={attachment}
 *   showDownload
 * />
 * ```
 */
export function FilePreview({
  attachment,
  showDownload = true,
  className = "",
}: FilePreviewProps) {
  const [open, setOpen] = useState(false);
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);

  /**
   * 获取文件类型图标
   */
  const getFileIcon = (attachment: Attachment) => {
    const type = attachment.file_type || "";
    const ext = attachment.file_extension || "";

    if (type.startsWith("image/")) {
      return { icon: ImageIcon, color: "text-green-500", label: "图片" };
    } else if (type === "application/pdf") {
      return { icon: FileText, color: "text-red-500", label: "PDF" };
    } else if (
      type.includes("word") ||
      type.includes("document") ||
      ext === ".doc" ||
      ext === ".docx"
    ) {
      return { icon: FileText, color: "text-blue-500", label: "Word" };
    } else if (
      type.includes("sheet") ||
      type.includes("excel") ||
      ext === ".xls" ||
      ext === ".xlsx"
    ) {
      return { icon: FileText, color: "text-green-600", label: "Excel" };
    } else if (
      type.includes("presentation") ||
      type.includes("powerpoint") ||
      ext === ".ppt" ||
      ext === ".pptx"
    ) {
      return { icon: FileText, color: "text-orange-500", label: "PPT" };
    } else if (
      type.includes("zip") ||
      type.includes("rar") ||
      type.includes("tar") ||
      type.includes("gzip") ||
      ext === ".zip" ||
      ext === ".rar"
    ) {
      return { icon: Archive, color: "text-yellow-600", label: "压缩包" };
    } else if (type.startsWith("audio/")) {
      return { icon: Music, color: "text-purple-500", label: "音频" };
    } else if (type.startsWith("video/")) {
      return { icon: Video, color: "text-pink-500", label: "视频" };
    } else if (type.startsWith("text/") || ext === ".txt") {
      return { icon: FileText, color: "text-gray-500", label: "文本" };
    } else if (
      type.includes("javascript") ||
      type.includes("json") ||
      type.includes("html") ||
      type.includes("css") ||
      ext === ".js" ||
      ext === ".json" ||
      ext === ".html" ||
      ext === ".css"
    ) {
      return { icon: FileCode, color: "text-yellow-500", label: "代码" };
    }
    return { icon: File, color: "text-gray-400", label: "文件" };
  };

  /**
   * 判断是否可预览
   */
  const isPreviewable = (attachment: Attachment) => {
    const type = attachment.file_type || "";
    return type.startsWith("image/") || type === "application/pdf";
  };

  /**
   * 获取预览URL
   */
  const getPreviewUrl = () => {
    // 对于图片，可以直接使用文件路径
    if (attachment.file_type?.startsWith("image/")) {
      return attachment.file_path;
    }
    // 其他文件使用下载URL
    return attachmentAPI.getDownloadUrl(attachment.id);
  };

  /**
   * 下载文件
   */
  const handleDownload = () => {
    const url = attachmentAPI.getDownloadUrl(attachment.id);
    const link = document.createElement("a");
    link.href = url;
    link.download = attachment.original_name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("开始下载");
  };

  /**
   * 打开预览
   */
  const handleOpenPreview = () => {
    if (!isPreviewable(attachment)) {
      handleDownload();
      return;
    }
    setOpen(true);
    setScale(1);
    setRotation(0);
  };

  /**
   * 放大
   */
  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.25, 3));
  };

  /**
   * 缩小
   */
  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.25, 0.5));
  };

  /**
   * 旋转
   */
  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360);
  };

  const fileInfo = getFileIcon(attachment);
  const Icon = fileInfo.icon;
  const canPreview = isPreviewable(attachment);
  const previewUrl = getPreviewUrl();

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  return (
    <>
      {/* 文件卡片 */}
      <div
        className={`group relative flex items-center gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors cursor-pointer ${className}`}
        onClick={handleOpenPreview}
      >
        {/* 图标 */}
        <div className={`flex-shrink-0 w-12 h-12 rounded-lg bg-muted flex items-center justify-center ${fileInfo.color}`}>
          <Icon className="h-6 w-6" />
        </div>

        {/* 文件信息 */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{attachment.original_name}</p>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{formatFileSize(attachment.file_size)}</span>
            <span>·</span>
            <Badge variant="outline" className="text-xs px-1.5 py-0">
              {fileInfo.label}
            </Badge>
            {attachment.download_count > 0 && (
              <>
                <span>·</span>
                <span>下载 {attachment.download_count} 次</span>
              </>
            )}
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {canPreview ? (
            <Button variant="ghost" size="icon" className="h-8 w-8" title="预览">
              <ExternalLink className="h-4 w-4" />
            </Button>
          ) : (
            <Button variant="ghost" size="icon" className="h-8 w-8" title="下载">
              <Download className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* 预览对话框 */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-4xl" onClose={() => setOpen(false)}>
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span className="truncate">{attachment.original_name}</span>
              <div className="flex items-center gap-2">
                {/* 图片工具栏 */}
                {attachment.file_type?.startsWith("image/") && (
                  <>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={handleZoomOut}
                      disabled={scale <= 0.5}
                    >
                      <ZoomOut className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={handleZoomIn}
                      disabled={scale >= 3}
                    >
                      <ZoomIn className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8"
                      onClick={handleRotate}
                    >
                      <RotateCw className="h-4 w-4" />
                    </Button>
                  </>
                )}
                {showDownload && (
                  <Button variant="outline" size="sm" onClick={handleDownload}>
                    <Download className="h-4 w-4 mr-2" />
                    下载
                  </Button>
                )}
              </div>
            </DialogTitle>
          </DialogHeader>

          {/* 预览内容 */}
          <div className="flex items-center justify-center min-h-[400px] bg-muted/50 rounded-lg overflow-hidden">
            {attachment.file_type?.startsWith("image/") ? (
              <img
                src={previewUrl}
                alt={attachment.original_name}
                className="max-w-full max-h-[600px] object-contain transition-transform"
                style={{
                  transform: `scale(${scale}) rotate(${rotation}deg)`,
                }}
              />
            ) : attachment.file_type === "application/pdf" ? (
              <iframe
                src={previewUrl}
                className="w-full h-[600px]"
                title={attachment.original_name}
              />
            ) : (
              <div className="flex flex-col items-center gap-4 text-muted-foreground">
                <Icon className="h-16 w-16" />
                <p>该文件类型不支持在线预览</p>
                {showDownload && (
                  <Button variant="outline" onClick={handleDownload}>
                    <Download className="h-4 w-4 mr-2" />
                    下载文件
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* 文件信息 */}
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-4">
              <span>大小: {formatFileSize(attachment.file_size)}</span>
              <span>类型: {attachment.file_type || "未知"}</span>
              {attachment.description && (
                <span>描述: {attachment.description}</span>
              )}
            </div>
            <span>上传于 {new Date(attachment.created_at).toLocaleString("zh-CN")}</span>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
