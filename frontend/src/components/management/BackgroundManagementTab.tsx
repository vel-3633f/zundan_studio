import { useState, useEffect } from "react";
import { Image, Loader2, RefreshCw, Trash2, CheckSquare, Square, Edit2, X, Check } from "lucide-react";
import toast from "react-hot-toast";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import { managementApi } from "@/api/management";
import type { Background } from "@/types";
import { cn } from "@/lib/utils";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const BackgroundManagementTab = () => {
  const [backgrounds, setBackgrounds] = useState<Background[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isDeleting, setIsDeleting] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState<string>("");
  const [isRenaming, setIsRenaming] = useState(false);
  const [imageCacheBuster, setImageCacheBuster] = useState<string>(Date.now().toString());

  const loadBackgrounds = async () => {
    setIsLoading(true);
    try {
      const data = await managementApi.backgrounds.list();
      setBackgrounds(data);
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        "背景画像の取得に失敗しました";
      toast.error(errorMessage);
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadBackgrounds();
  }, []);

  const getImageUrl = (path: string, cacheBuster?: string) => {
    // pathが既にフルパスの場合はそのまま返す
    if (path.startsWith("http")) {
      return path;
    }
    // パスからファイル名を抽出（例: assets/backgrounds/blue_sky.png -> blue_sky.png）
    const filename = path.split("/").pop() || path;
    // APIエンドポイントを使用（静的ファイル配信のフォールバック）
    const baseUrl = `${API_BASE_URL}/api/management/backgrounds/file/${filename}`;
    // キャッシュバスターを追加（ファイル名変更後の画像更新を確実にする）
    return cacheBuster ? `${baseUrl}?t=${cacheBuster}` : baseUrl;
  };

  const handleToggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedIds.size === backgrounds.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(backgrounds.map((bg) => bg.id)));
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) {
      toast.error("削除する画像を選択してください");
      return;
    }

    const confirmMessage = `選択した${selectedIds.size}件の背景画像を削除しますか？\nこの操作は取り消せません。`;
    if (!window.confirm(confirmMessage)) {
      return;
    }

    setIsDeleting(true);
    try {
      const ids = Array.from(selectedIds);
      const response = await managementApi.backgrounds.delete(ids);

      if (response.success) {
        toast.success(response.message);
        setSelectedIds(new Set());
        setSelectedImage(null);
        // 一覧を再読み込み
        await loadBackgrounds();
      } else {
        toast.error(response.message || "削除に失敗しました");
      }
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        "削除に失敗しました";
      toast.error(errorMessage);
      console.error(error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleStartEdit = (bg: Background) => {
    setEditingId(bg.id);
    setEditingName(bg.name);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName("");
  };

  const validateFileName = (name: string): string | null => {
    if (!name || !name.trim()) {
      return "ファイル名が空です";
    }
    const invalidChars = '<>:"/\\|?*';
    for (const char of invalidChars) {
      if (name.includes(char)) {
        return `ファイル名に無効な文字が含まれています: ${char}`;
      }
    }
    return null;
  };

  const handleSaveRename = async (id: string) => {
    const validationError = validateFileName(editingName);
    if (validationError) {
      toast.error(validationError);
      return;
    }

    const trimmedName = editingName.trim();
    if (trimmedName === "") {
      toast.error("ファイル名が空です");
      return;
    }

    setIsRenaming(true);
    try {
      const response = await managementApi.backgrounds.rename(id, trimmedName);

      if (response.success) {
        toast.success(response.message);
        setEditingId(null);
        setEditingName("");
        // 選択中の画像をリセット（ファイル名が変わったため）
        setSelectedImage(null);
        // キャッシュバスターを更新して画像を強制的に再読み込み
        setImageCacheBuster(Date.now().toString());
        // 一覧を再読み込み
        await loadBackgrounds();
      } else {
        toast.error(response.message || "ファイル名の変更に失敗しました");
      }
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        "ファイル名の変更に失敗しました";
      toast.error(errorMessage);
      console.error(error);
    } finally {
      setIsRenaming(false);
    }
  };

  return (
    <Card icon={<Image className="h-6 w-6" />} title="背景画像管理">
      <div className="space-y-6">
        {/* ヘッダーアクション */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {backgrounds.length}件の背景画像が見つかりました
              {selectedIds.size > 0 && (
                <span className="ml-2 text-primary-600 dark:text-primary-400 font-medium">
                  （{selectedIds.size}件選択中）
                </span>
              )}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {backgrounds.length > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSelectAll}
                  disabled={isLoading}
                  leftIcon={
                    selectedIds.size === backgrounds.length ? (
                      <CheckSquare className="h-4 w-4" />
                    ) : (
                      <Square className="h-4 w-4" />
                    )
                  }
                >
                  {selectedIds.size === backgrounds.length ? "すべて解除" : "すべて選択"}
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleDeleteSelected}
                  disabled={isLoading || isDeleting || selectedIds.size === 0}
                  leftIcon={
                    isDeleting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )
                  }
                >
                  {isDeleting ? "削除中..." : "選択を削除"}
                </Button>
              </>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={loadBackgrounds}
              disabled={isLoading || isDeleting}
              leftIcon={
                isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )
              }
            >
              更新
            </Button>
          </div>
        </div>

        {/* ローディング状態 */}
        {isLoading && backgrounds.length === 0 && (
          <div className="text-center py-12">
            <Loader2 className="h-8 w-8 text-gray-400 dark:text-gray-500 mx-auto mb-4 animate-spin" />
            <p className="text-sm text-gray-500 dark:text-gray-400">
              背景画像を読み込んでいます...
            </p>
          </div>
        )}

        {/* 背景画像一覧 */}
        {!isLoading && backgrounds.length === 0 && (
          <div className="text-center py-12">
            <Image className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              背景画像が見つかりませんでした
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              assets/backgrounds/ ディレクトリに画像を配置してください
            </p>
          </div>
        )}

        {/* 画像グリッド */}
        {backgrounds.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {backgrounds.map((bg) => {
              const imageUrl = getImageUrl(bg.path, imageCacheBuster);
              const isPreviewSelected = selectedImage === bg.id;
              const isDeleteSelected = selectedIds.has(bg.id);

              return (
                <div
                  key={bg.id}
                  className={cn(
                    "relative group rounded-lg overflow-hidden border-2 transition-all duration-200",
                    isPreviewSelected
                      ? "border-primary-500 dark:border-primary-400 shadow-lg"
                      : isDeleteSelected
                      ? "border-error-500 dark:border-error-400 shadow-md"
                      : "border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600 hover:shadow-md"
                  )}
                >
                  {/* チェックボックス */}
                  <div className="absolute top-2 left-2 z-10">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleSelect(bg.id);
                      }}
                      className={cn(
                        "p-1.5 rounded-md bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border transition-all",
                        isDeleteSelected
                          ? "border-error-500 dark:border-error-400 text-error-600 dark:text-error-400"
                          : "border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-primary-400 dark:hover:border-primary-500"
                      )}
                    >
                      {isDeleteSelected ? (
                        <CheckSquare className="h-4 w-4" />
                      ) : (
                        <Square className="h-4 w-4" />
                      )}
                    </button>
                  </div>

                  {/* 編集ボタン */}
                  {!isDeleteSelected && (
                    <div className="absolute top-2 right-2 z-10">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStartEdit(bg);
                        }}
                        className="p-1.5 rounded-md bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-primary-400 dark:hover:border-primary-500 hover:text-primary-600 dark:hover:text-primary-400 transition-all"
                        disabled={isRenaming || editingId !== null}
                        title="ファイル名を編集"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                    </div>
                  )}

                  {/* 画像 */}
                  <div
                    className="aspect-video bg-gray-100 dark:bg-gray-800 relative overflow-hidden cursor-pointer"
                    onClick={() => setSelectedImage(isPreviewSelected ? null : bg.id)}
                  >
                    <img
                      key={`${bg.id}-${imageCacheBuster}`}
                      src={imageUrl}
                      alt={bg.name}
                      className="w-full h-full object-cover"
                      loading="lazy"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = "none";
                        const parent = target.parentElement;
                        if (parent) {
                          parent.innerHTML = `
                            <div class="flex items-center justify-center h-full text-gray-400 dark:text-gray-600">
                              <p class="text-sm">画像を読み込めませんでした</p>
                            </div>
                          `;
                        }
                      }}
                    />
                    {/* オーバーレイ */}
                    <div
                      className={cn(
                        "absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-200 flex items-center justify-center",
                        isPreviewSelected && "bg-black/30"
                      )}
                    >
                      {isPreviewSelected && (
                        <Badge variant="success" className="opacity-90">
                          プレビュー中
                        </Badge>
                      )}
                      {isDeleteSelected && !isPreviewSelected && (
                        <Badge variant="error" className="opacity-90">
                          削除対象
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* 画像情報 */}
                  <div className="p-3 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                    {editingId === bg.id ? (
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              handleSaveRename(bg.id);
                            } else if (e.key === "Escape") {
                              handleCancelEdit();
                            }
                          }}
                          className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
                          autoFocus
                          disabled={isRenaming}
                        />
                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSaveRename(bg.id);
                            }}
                            disabled={isRenaming}
                            className="p-1 rounded text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors disabled:opacity-50"
                            title="保存"
                          >
                            <Check className="h-4 w-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleCancelEdit();
                            }}
                            disabled={isRenaming}
                            className="p-1 rounded text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50"
                            title="キャンセル"
                          >
                            <X className="h-4 w-4" />
                          </button>
                          {isRenaming && (
                            <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                          )}
                        </div>
                      </div>
                    ) : (
                      <>
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {bg.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-1">
                          {bg.path}
                        </p>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 選択された画像のプレビュー */}
        {selectedImage && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              プレビュー
            </h4>
            {(() => {
              const selectedBg = backgrounds.find((bg) => bg.id === selectedImage);
              if (!selectedBg) return null;

              const imageUrl = getImageUrl(selectedBg.path, imageCacheBuster);
              return (
                <div className="space-y-4">
                  <div className="relative rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800">
                    <img
                      key={`preview-${selectedBg.id}-${imageCacheBuster}`}
                      src={imageUrl}
                      alt={selectedBg.name}
                      className="w-full h-auto max-h-96 object-contain"
                    />
                  </div>
                  <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <div className="space-y-2">
                      <div>
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                          名前
                        </p>
                        <p className="text-sm text-gray-900 dark:text-white">
                          {selectedBg.name}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                          パス
                        </p>
                        <p className="text-sm font-mono text-gray-700 dark:text-gray-300 break-all">
                          {selectedBg.path}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                          URL
                        </p>
                        <p className="text-sm font-mono text-gray-700 dark:text-gray-300 break-all">
                          {imageUrl}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </div>
    </Card>
  );
};

