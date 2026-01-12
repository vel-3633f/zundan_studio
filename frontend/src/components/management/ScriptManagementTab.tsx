import { useState, useEffect } from "react";
import { FileText, RefreshCw, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";
import { videoApi } from "@/api/videos";
import type { JsonFileInfo } from "@/types";

export const ScriptManagementTab = () => {
  const [jsonFiles, setJsonFiles] = useState<JsonFileInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [updatingFiles, setUpdatingFiles] = useState<Set<string>>(new Set());
  const [deletingFiles, setDeletingFiles] = useState<Set<string>>(new Set());

  const loadJsonFiles = async () => {
    setIsLoading(true);
    try {
      const files = await videoApi.listJsonFiles();
      setJsonFiles(files);
    } catch (error: any) {
      console.error("JSONファイル一覧取得エラー:", error);
      toast.error("JSONファイル一覧の取得に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadJsonFiles();
  }, []);

  const handleToggleGenerated = async (filename: string, currentStatus: boolean) => {
    const newStatus = !currentStatus;
    setUpdatingFiles((prev) => new Set(prev).add(filename));

    try {
      const updated = await videoApi.updateJsonFileStatus(filename, {
        is_generated: newStatus,
      });

      // ローカル状態を更新
      setJsonFiles((prev) =>
        prev.map((file) =>
          file.filename === filename
            ? { ...file, is_generated: updated.is_generated }
            : file
        )
      );

      toast.success(
        newStatus
          ? "生成済みとしてマークしました"
          : "未生成としてマークしました"
      );
    } catch (error: any) {
      console.error("ステータス更新エラー:", error);
      toast.error("ステータスの更新に失敗しました");
    } finally {
      setUpdatingFiles((prev) => {
        const next = new Set(prev);
        next.delete(filename);
        return next;
      });
    }
  };

  const handleDeleteJson = async (filename: string) => {
    if (!confirm(`「${filename}」を削除してもよろしいですか？`)) {
      return;
    }

    setDeletingFiles((prev) => new Set(prev).add(filename));

    try {
      const result = await videoApi.deleteJsonFile(filename);
      if (result.success) {
        // ローカル状態から削除
        setJsonFiles((prev) => prev.filter((file) => file.filename !== filename));
        toast.success(result.message || "ファイルを削除しました");
      } else {
        toast.error("ファイルの削除に失敗しました");
      }
    } catch (error: any) {
      console.error("JSON削除エラー:", error);
      toast.error("ファイルの削除に失敗しました");
    } finally {
      setDeletingFiles((prev) => {
        const next = new Set(prev);
        next.delete(filename);
        return next;
      });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          台本JSONファイル管理
        </h2>
        <button
          onClick={loadJsonFiles}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw
            className={cn("h-4 w-4", isLoading && "animate-spin")}
          />
          {isLoading ? "読み込み中..." : "更新"}
        </button>
      </div>

      {isLoading && jsonFiles.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          読み込み中...
        </div>
      ) : jsonFiles.length === 0 ? (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          JSONファイルが見つかりませんでした
        </div>
      ) : (
        <div className="space-y-2">
          {jsonFiles.map((file) => {
            const isUpdating = updatingFiles.has(file.filename);
            const isDeleting = deletingFiles.has(file.filename);
            return (
              <div
                key={file.filename}
                className="flex items-center justify-between p-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <FileText className="h-5 w-5 text-gray-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {file.filename}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {file.path}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4 ml-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={file.is_generated}
                      onChange={() =>
                        handleToggleGenerated(file.filename, file.is_generated)
                      }
                      disabled={isUpdating}
                      className="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {isUpdating ? "更新中..." : "生成済み"}
                    </span>
                  </label>
                  <button
                    onClick={() => handleDeleteJson(file.filename)}
                    disabled={isDeleting}
                    className="p-2 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="削除"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

