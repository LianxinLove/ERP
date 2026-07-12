/**
 * 文件上传组件
 * @description 支持拖拽上传、多文件上传、上传进度显示
 */

"use client";

import { useCallback, useState } from "react";
import {
  Upload,
  X,
  File,
  Image as ImageIcon,
  FileText,
  Archive,
  AlertCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { useFileUpload } from "@/hooks/useFileUpload";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

interface FileUploaderProps {
  /** 上传成功回调 */
  onSuccess?: (result: any) => void;
  /** 上传参数（entity_type, entity_id等） */
  uploadData?: {
    entity_type?: string;
    entity_id?: number;
    category_id?: number;
    description?: string;
  };
  /** 验证选项 */
  validation?: {
    /** 允许的文件类型，如 "image/*,.pdf,.doc,.docx" */
    allowedTypes?: string;
    /** 最大文件大小（字节） */
    maxSize?: number;
    /** 最大文件数 */
    maxFiles?: number;
  };
  /** 是否多选 */
  multiple?: boolean;
  /** 是否禁用 */
  disabled?: boolean;
  /** 自定义类名 */
  className?: string;
}

/**
 * 文件上传组件
 *
 * @features
 * - 支持拖拽上传
 * - 支持点击选择文件
 * - 支持多文件上传
 * - 实时显示上传进度
 * - 文件类型和大小验证
 * - 上传失败重试
 *
 * @example
 * ```tsx
 * <FileUploader
 *   multiple
 *   uploadData={{ entity_type: "purchase_order", entity_id: 123 }}
 *   validation={{ allowedTypes: "image/*,.pdf", maxSize: 10 * 1024 * 1024 }}
 *   onSuccess={(result) => console.log(result)}
 * />
 * ```
 */
export function FileUploader({
  onSuccess,
  uploadData = {},
  validation = {},
  multiple = true,
  disabled = false,
  className = "",
}: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [showUploadArea, setShowUploadArea] = useState(true);

  const {
    uploadingFiles,
    isUploading,
    successCount,
    errorCount,
    totalCount,
    uploadFiles,
    retryUpload,
    removeFile,
    clearQueue,
    formatFileSize,
  } = useFileUpload({
    onSuccess: (result) => {
      onSuccess?.(result);
      toast.success("上传成功");
    },
  });

  /**
   * 获取文件图标
   */
  const getFileIcon = (file: File) => {
    const type = file.type;

    if (type.startsWith("image/")) {
      return <ImageIcon className="h-5 w-5" />;
    } else if (type.startsWith("text/")) {
      return <FileText className="h-5 w-5" />;
    } else if (
      type.includes("zip") ||
      type.includes("rar") ||
      type.includes("tar") ||
      type.includes("gzip")
    ) {
      return <Archive className="h-5 w-5" />;
    }
    return <File className="h-5 w-5" />;
  };

  /**
   * 处理文件选择
   */
  const handleFiles = async (files: FileList | File[]) => {
    if (validation.maxFiles && files.length > validation.maxFiles) {
      toast.error(`最多只能上传 ${validation.maxFiles} 个文件`);
      return;
    }

    await uploadFiles(files, uploadData, validation);
    setShowUploadArea(false);
  };

  /**
   * 拖拽事件处理
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        await handleFiles(files);
      }
    },
    [validation, uploadData]
  );

  /**
   * 文件选择处理
   */
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleFiles(files);
    }
    // 重置 input
    e.target.value = "";
  };

  /**
   * 继续添加文件
   */
  const handleContinueUpload = () => {
    setShowUploadArea(true);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* 上传区域 */}
      {showUploadArea && (
        <Card
          className={`border-2 border-dashed transition-colors ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-muted-foreground/50"
          } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
          onDragOver={disabled ? undefined : handleDragOver}
          onDragLeave={disabled ? undefined : handleDragLeave}
          onDrop={disabled ? undefined : handleDrop}
        >
          <CardContent className="flex flex-col items-center justify-center py-12 px-6">
            <input
              type="file"
              id="file-upload"
              className="hidden"
              multiple={multiple}
              onChange={handleFileSelect}
              disabled={disabled}
            />

            <label
              htmlFor="file-upload"
              className={`flex flex-col items-center ${disabled ? "cursor-not-allowed" : "cursor-pointer"}`}
            >
              <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>

              <div className="text-center">
                <p className="text-sm font-medium mb-1">
                  点击或拖拽文件到此处上传
                </p>
                <p className="text-xs text-muted-foreground">
                  {validation.allowedTypes && `支持格式：${validation.allowedTypes} `}
                  {validation.maxSize &&
                    `· 单个文件最大 ${formatFileSize(validation.maxSize)}`}
                  {validation.maxFiles && `· 最多 ${validation.maxFiles} 个文件`}
                </p>
              </div>
            </label>
          </CardContent>
        </Card>
      )}

      {/* 上传队列 */}
      {uploadingFiles.length > 0 && (
        <div className="space-y-3">
          {/* 统计信息 */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">
              共 {totalCount} 个文件 · 成功 {successCount} · 失败 {errorCount}
            </span>
            {!isUploading && (
              <div className="flex gap-2">
                {!showUploadArea && (
                  <Button variant="outline" size="sm" onClick={handleContinueUpload}>
                    继续添加
                  </Button>
                )}
                <Button variant="ghost" size="sm" onClick={clearQueue}>
                  清空列表
                </Button>
              </div>
            )}
          </div>

          {/* 文件列表 */}
          <div className="space-y-2">
            {uploadingFiles.map(([id, fileState]) => (
              <Card
                key={id}
                className={`${
                  fileState.status === "error"
                    ? "border-destructive/50 bg-destructive/5"
                    : ""
                }`}
              >
                <CardContent className="p-3">
                  <div className="flex items-center gap-3">
                    {/* 文件图标 */}
                    <div className="flex-shrink-0">
                      {getFileIcon(fileState.file)}
                    </div>

                    {/* 文件信息 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium truncate">
                          {fileState.file.name}
                        </p>
                        {fileState.status === "success" && (
                          <Badge variant="default" className="text-xs">
                            成功
                          </Badge>
                        )}
                        {fileState.status === "error" && (
                          <Badge variant="destructive" className="text-xs">
                            失败
                          </Badge>
                        )}
                        {fileState.status === "uploading" && (
                          <Badge variant="secondary" className="text-xs">
                            {fileState.progress}%
                          </Badge>
                        )}
                      </div>

                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{formatFileSize(fileState.file.size)}</span>

                        {/* 进度条 */}
                        {fileState.status === "uploading" && (
                          <div className="flex-1">
                            <Progress value={fileState.progress} className="h-1" />
                          </div>
                        )}

                        {/* 错误信息 */}
                        {fileState.status === "error" && (
                          <span className="text-destructive">{fileState.error}</span>
                        )}
                      </div>
                    </div>

                    {/* 操作按钮 */}
                    <div className="flex items-center gap-1">
                      {fileState.status === "uploading" && (
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      )}
                      {fileState.status === "error" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => retryUpload(id, uploadData)}
                          title="重试"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => removeFile(id)}
                        title="移除"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* 全部上传中提示 */}
          {isUploading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>上传中...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
