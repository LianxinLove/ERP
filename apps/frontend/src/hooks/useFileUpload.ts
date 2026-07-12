/**
 * 文件上传 Hook
 * @description 封装文件上传相关的状态管理和操作逻辑
 */

"use client";

import { useState, useCallback } from "react";
import { attachmentAPI } from "@/api/attachment";
import {
  Attachment,
  AttachmentUploadResponse,
  AttachmentUploadRequest,
} from "@/types/attachment";
import { toast } from "sonner";

/**
 * 上传中的文件状态
 */
interface UploadingFile {
  file: File;
  progress: number;
  status: "uploading" | "success" | "error";
  result?: AttachmentUploadResponse;
  error?: string;
}

interface UseFileUploadOptions {
  /** 成功回调 */
  onSuccess?: (result: AttachmentUploadResponse) => void;
  /** 错误回调 */
  onError?: (error: string) => void;
  /** 进度回调 */
  onProgress?: (fileName: string, progress: number) => void;
}

/**
 * 文件上传 Hook
 *
 * @features
 * - 管理上传队列
 * - 实时显示上传进度
 * - 支持多文件上传
 * - 文件类型和大小验证
 * - 上传失败重试
 *
 * @example
 * ```tsx
 * const {
 *   uploadingFiles,
 *   uploadFiles,
 *   retryUpload,
 *   removeFile,
 *   isUploading
 * } = useFileUpload({
 *   onSuccess: (result) => {
 *     toast.success('上传成功');
 *   }
 * });
 * ```
 */
export function useFileUpload(options: UseFileUploadOptions = {}) {
  const { onSuccess, onError, onProgress } = options;

  // 状态
  const [uploadingFiles, setUploadingFiles] = useState<Map<string, UploadingFile>>(
    new Map()
  );

  /**
   * 生成唯一ID
   */
  const generateId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  /**
   * 格式化文件大小
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  };

  /**
   * 验证文件类型
   */
  const validateFileType = (
    file: File,
    allowedTypes?: string
  ): boolean => {
    if (!allowedTypes) return true;

    const rules = allowedTypes.split(",").map((rule) => rule.trim());
    const fileExtension = `.${file.name.split(".").pop()?.toLowerCase()}`;

    return rules.some((rule) => {
      if (rule.startsWith("*")) {
        // 匹配文件扩展名
        return rule === `*${fileExtension}`;
      } else if (rule.includes("/*")) {
        // 匹配 MIME 类型
        const mimePrefix = rule.split("/*")[0];
        return file.type.startsWith(mimePrefix);
      } else if (rule.startsWith(".")) {
        // 匹配文件扩展名
        return fileExtension === rule.toLowerCase();
      }
      return false;
    });
  };

  /**
   * 验证文件大小
   */
  const validateFileSize = (file: File, maxSize?: number): boolean => {
    if (!maxSize) return true;
    return file.size <= maxSize;
  };

  /**
   * 上传单个文件
   */
  const uploadFile = useCallback(
    async (
      file: File,
      uploadData?: Omit<AttachmentUploadRequest, "file">
    ): Promise<string> => {
      const fileId = generateId();

      // 添加到上传队列
      setUploadingFiles((prev) => {
        const next = new Map(prev);
        next.set(fileId, {
          file,
          progress: 0,
          status: "uploading",
        });
        return next;
      });

      try {
        const result = await attachmentAPI.uploadAttachment(
          {
            file,
            ...uploadData,
          },
          (progress) => {
            // 更新进度
            setUploadingFiles((prev) => {
              const next = new Map(prev);
              const current = next.get(fileId);
              if (current) {
                next.set(fileId, { ...current, progress });
              }
              return next;
            });

            // 触发进度回调
            onProgress?.(file.name, progress);
          }
        );

        // 上传成功
        setUploadingFiles((prev) => {
          const next = new Map(prev);
          const current = next.get(fileId);
          if (current) {
            next.set(fileId, {
              ...current,
              status: "success",
              progress: 100,
              result,
            });
          }
          return next;
        });

        onSuccess?.(result);

        return fileId;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "上传失败";

        // 上传失败
        setUploadingFiles((prev) => {
          const next = new Map(prev);
          const current = next.get(fileId);
          if (current) {
            next.set(fileId, {
              ...current,
              status: "error",
              error: errorMessage,
            });
          }
          return next;
        });

        onError?.(errorMessage);
        toast.error(`${file.name} 上传失败`);

        return fileId;
      }
    },
    [onSuccess, onError, onProgress]
  );

  /**
   * 上传多个文件
   */
  const uploadFiles = useCallback(
    async (
      files: FileList | File[],
      uploadData?: Omit<AttachmentUploadRequest, "file">,
      validationOptions?: {
        allowedTypes?: string;
        maxSize?: number;
      }
    ) => {
      const fileArray = Array.from(files);
      const fileIds: string[] = [];

      for (const file of fileArray) {
        // 验证文件类型
        if (
          validationOptions?.allowedTypes &&
          !validateFileType(file, validationOptions.allowedTypes)
        ) {
          toast.error(`文件类型不支持: ${file.name}`);
          continue;
        }

        // 验证文件大小
        if (
          validationOptions?.maxSize &&
          !validateFileSize(file, validationOptions.maxSize)
        ) {
          toast.error(
            `文件过大: ${file.name} (最大 ${formatFileSize(validationOptions.maxSize)})`
          );
          continue;
        }

        const fileId = await uploadFile(file, uploadData);
        fileIds.push(fileId);
      }

      return fileIds;
    },
    [uploadFile]
  );

  /**
   * 重试上传
   */
  const retryUpload = useCallback(
    async (fileId: string, uploadData?: Omit<AttachmentUploadRequest, "file">) => {
      const uploadingFile = uploadingFiles.get(fileId);
      if (!uploadingFile) return;

      // 移除旧记录
      setUploadingFiles((prev) => {
        const next = new Map(prev);
        next.delete(fileId);
        return next;
      });

      // 重新上传
      await uploadFile(uploadingFile.file, uploadData);
    },
    [uploadingFiles, uploadFile]
  );

  /**
   * 移除文件记录
   */
  const removeFile = useCallback((fileId: string) => {
    setUploadingFiles((prev) => {
      const next = new Map(prev);
      next.delete(fileId);
      return next;
    });
  }, []);

  /**
   * 清空上传队列
   */
  const clearQueue = useCallback(() => {
    setUploadingFiles(new Map());
  }, []);

  // 是否正在上传
  const isUploading = Array.from(uploadingFiles.values()).some(
    (f) => f.status === "uploading"
  );

  // 上传成功的文件
  const successFiles = Array.from(uploadingFiles.values()).filter(
    (f) => f.status === "success"
  );

  // 上传失败的文件
  const errorFiles = Array.from(uploadingFiles.values()).filter(
    (f) => f.status === "error"
  );

  return {
    // 状态
    uploadingFiles: Array.from(uploadingFiles.entries()),
    isUploading,
    successCount: successFiles.length,
    errorCount: errorFiles.length,
    totalCount: uploadingFiles.size,

    // 方法
    uploadFile,
    uploadFiles,
    retryUpload,
    removeFile,
    clearQueue,
    formatFileSize,
    validateFileType,
    validateFileSize,
  };
}
