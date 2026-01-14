import { useState } from "react";
import { Play, CheckCircle2, XCircle, Loader2, Eye, EyeOff, MessageSquare } from "lucide-react";
import Button from "@/components/Button";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import ProgressBar from "@/components/ProgressBar";
import { JsonFilePreview } from "./JsonFilePreview";
import { JsonMetadata } from "./JsonMetadata";
import { ConversationList } from "./ConversationList";
import BackgroundCheckCard from "@/components/resources/BackgroundCheckCard";
import type { JsonFileInfo, ConversationLine, VideoSection, JsonScriptData, BackgroundCheckResponse } from "@/types";

interface BatchVideoGeneratorProps {
  jsonFiles: JsonFileInfo[];
  isLoadingJsonFiles: boolean;
  onStartBatchGeneration: (selectedFiles: JsonFileInfo[]) => void;
  batchState: {
    isGenerating: boolean;
    currentFileIndex: number;
    totalFiles: number;
    completedFiles: string[];
    failedFiles: { filename: string; error: string }[];
    currentProgress: number;
    currentMessage: string;
  };
  previewData: {
    conversations: ConversationLine[];
    sections: VideoSection[] | null;
    jsonScriptData: JsonScriptData | null;
  } | null;
  backgroundCheckResult: BackgroundCheckResponse | null;
  isCheckingBackgrounds: boolean;
  isLoadingPreview: boolean;
  onFilesSelected: (files: JsonFileInfo[]) => void;
}

export const BatchVideoGenerator = ({
  jsonFiles,
  isLoadingJsonFiles,
  onStartBatchGeneration,
  batchState,
  previewData,
  backgroundCheckResult,
  isCheckingBackgrounds,
  isLoadingPreview,
  onFilesSelected,
}: BatchVideoGeneratorProps) => {
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [confirmed, setConfirmed] = useState(false);
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set());
  const [showFileDetails, setShowFileDetails] = useState(false);
  const [showConversations, setShowConversations] = useState(true);
  const [activePreviewFile, setActivePreviewFile] = useState<string | null>(null);

  const speakerColors = {
    zundamon:
      "bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700",
    metan:
      "bg-pink-100 dark:bg-pink-900/30 border-pink-300 dark:border-pink-700",
    tsumugi:
      "bg-purple-100 dark:bg-purple-900/30 border-purple-300 dark:border-purple-700",
    narrator:
      "bg-gray-100 dark:bg-gray-800/30 border-gray-300 dark:border-gray-700",
  };

  const speakerTextColors = {
    zundamon: "text-green-700 dark:text-green-400",
    metan: "text-pink-700 dark:text-pink-400",
    tsumugi: "text-purple-700 dark:text-purple-400",
    narrator: "text-gray-700 dark:text-gray-400",
  };

  const handleToggleFile = (filename: string) => {
    const newSelected = new Set(selectedFiles);
    if (newSelected.has(filename)) {
      newSelected.delete(filename);
      // 削除したファイルがアクティブだった場合、別のファイルをアクティブに
      if (activePreviewFile === filename) {
        const remaining = Array.from(newSelected);
        setActivePreviewFile(remaining.length > 0 ? remaining[0] : null);
      }
    } else {
      newSelected.add(filename);
      // 最初に選択したファイルをアクティブに
      if (activePreviewFile === null) {
        setActivePreviewFile(filename);
      }
    }
    setSelectedFiles(newSelected);
    setConfirmed(false); // 選択が変わったら確認をリセット
    
    // 選択されたファイルのプレビューを読み込む
    const selected = jsonFiles.filter((f) => newSelected.has(f.filename));
    onFilesSelected(selected);
  };

  const handleToggleExpand = (filename: string) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(filename)) {
      newExpanded.delete(filename);
    } else {
      newExpanded.add(filename);
    }
    setExpandedFiles(newExpanded);
  };

  const handleSelectAll = () => {
    const newSelected = selectedFiles.size === jsonFiles.length 
      ? new Set<string>() 
      : new Set(jsonFiles.map((f) => f.filename));
    
    setSelectedFiles(newSelected);
    setConfirmed(false);
    
    // 選択されたファイルのプレビューを読み込む
    const selected = jsonFiles.filter((f) => newSelected.has(f.filename));
    onFilesSelected(selected);
  };

  const hasNoBackgrounds = () => {
    if (!backgroundCheckResult) {
      return false;
    }
    return (
      backgroundCheckResult.total === 0 ||
      (backgroundCheckResult.available === 0 && backgroundCheckResult.total > 0)
    );
  };

  const handleStartGeneration = () => {
    const filesToGenerate = jsonFiles.filter((f) =>
      selectedFiles.has(f.filename)
    );
    onStartBatchGeneration(filesToGenerate);
    setConfirmed(false);
    setSelectedFiles(new Set());
  };

  const getFileStatus = (filename: string) => {
    if (batchState.completedFiles.includes(filename)) {
      return "completed";
    }
    if (batchState.failedFiles.some((f) => f.filename === filename)) {
      return "failed";
    }
    if (
      batchState.isGenerating &&
      batchState.currentFileIndex < batchState.totalFiles
    ) {
      const currentFile =
        jsonFiles.find((_, idx) => idx === batchState.currentFileIndex)
          ?.filename || "";
      if (currentFile === filename) {
        return "processing";
      }
    }
    return "pending";
  };

  const getOverallProgress = () => {
    if (!batchState.isGenerating || batchState.totalFiles === 0) return 0;
    const completed = batchState.completedFiles.length + batchState.failedFiles.length;
    return (completed / batchState.totalFiles) * 100;
  };

  return (
    <div className="space-y-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            バッチ動画生成
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            複数のJSONファイルを選択して、順番に動画を生成します
          </p>
        </div>
        {jsonFiles.length > 0 && !batchState.isGenerating && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleSelectAll}
            disabled={isLoadingJsonFiles}
          >
            {selectedFiles.size === jsonFiles.length
              ? "すべて解除"
              : "すべて選択"}
          </Button>
        )}
      </div>

      {/* 全体進捗 */}
      {batchState.isGenerating && (
        <Card className="animate-fade-in">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                全体進捗: {batchState.completedFiles.length + batchState.failedFiles.length} / {batchState.totalFiles}
              </span>
              <Badge variant="info">
                処理中 ({batchState.currentFileIndex + 1}/{batchState.totalFiles})
              </Badge>
            </div>
            <ProgressBar
              progress={getOverallProgress()}
              message={batchState.currentMessage}
              variant="default"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400">
              現在の個別ファイル進捗: {Math.round(batchState.currentProgress * 100)}%
            </div>
          </div>
        </Card>
      )}

      {/* ファイルリスト */}
      {isLoadingJsonFiles ? (
        <div className="text-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            ファイルを読み込み中...
          </p>
        </div>
      ) : jsonFiles.length === 0 ? (
        <Card className="text-center py-8">
          <p className="text-gray-500 dark:text-gray-400">
            生成可能なJSONファイルがありません
          </p>
        </Card>
      ) : (
        <div className="space-y-2">
          {jsonFiles.map((file) => {
            const status = getFileStatus(file.filename);
            const isSelected = selectedFiles.has(file.filename);
            const isExpanded = expandedFiles.has(file.filename);

            return (
              <Card
                key={file.filename}
                className={`transition-all ${
                  isSelected
                    ? "ring-2 ring-primary-500 dark:ring-primary-400"
                    : ""
                } ${status === "completed" ? "bg-green-50 dark:bg-green-900/10" : ""} ${
                  status === "failed" ? "bg-red-50 dark:bg-red-900/10" : ""
                } ${status === "processing" ? "ring-2 ring-blue-500 dark:ring-blue-400" : ""}`}
              >
                <div className="space-y-2">
                  <div className="flex items-start gap-3">
                    {!batchState.isGenerating && (
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleToggleFile(file.filename)}
                        className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        disabled={batchState.isGenerating}
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleToggleExpand(file.filename)}
                          className="text-left flex-1 min-w-0"
                        >
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {file.filename}
                          </p>
                        </button>
                        {status === "completed" && (
                          <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0" />
                        )}
                        {status === "failed" && (
                          <XCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0" />
                        )}
                        {status === "processing" && (
                          <Loader2 className="h-5 w-5 text-blue-600 dark:text-blue-400 animate-spin flex-shrink-0" />
                        )}
                      </div>
                      {status === "failed" && (
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                          エラー:{" "}
                          {
                            batchState.failedFiles.find(
                              (f) => f.filename === file.filename
                            )?.error
                          }
                        </p>
                      )}
                      {isExpanded && (
                        <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 space-y-1">
                          <p>パス: {file.path}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* 選択ファイルのプレビュー */}
      {selectedFiles.size > 0 && !batchState.isGenerating && (
        <>
          {/* ファイル詳細の表示/非表示切り替え */}
          <Card className="animate-fade-in">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                選択中: {selectedFiles.size}件
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFileDetails(!showFileDetails)}
                leftIcon={showFileDetails ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              >
                {showFileDetails ? "ファイル詳細を閉じる" : "ファイル詳細を表示"}
              </Button>
            </div>

            {showFileDetails && (
              <div className="mt-4 space-y-2 animate-fade-in">
                {jsonFiles
                  .filter((f) => selectedFiles.has(f.filename))
                  .map((file) => (
                    <JsonFilePreview key={file.filename} file={file} />
                  ))}
              </div>
            )}
          </Card>

          {/* 背景画像チェック */}
          {isLoadingPreview ? (
            <Card className="animate-fade-in">
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400 mr-2" />
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  プレビューを読み込み中...
                </span>
              </div>
            </Card>
          ) : (
            <>
              <BackgroundCheckCard
                result={backgroundCheckResult}
                isLoading={isCheckingBackgrounds}
              />

              {/* JSONメタ情報 */}
              {previewData?.jsonScriptData && (
                <JsonMetadata jsonScriptData={previewData.jsonScriptData} />
              )}

              {/* 会話リスト */}
              {previewData?.conversations && previewData.conversations.length > 0 && (
                <Card
                  icon={<MessageSquare className="h-6 w-6" />}
                  title="会話プレビュー（全ファイル統合）"
                  headerAction={
                    <div className="flex items-center gap-2">
                      <Badge variant="info">
                        {selectedFiles.size}ファイル
                      </Badge>
                      <Badge variant="default">
                        {previewData.conversations.length}セリフ
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowConversations(!showConversations)}
                      >
                        {showConversations ? "折りたたむ" : "展開"}
                      </Button>
                    </div>
                  }
                  className="animate-fade-in"
                >
                  {showConversations && (
                    <>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                        ※ 選択した全ファイルの会話を統合して表示しています（ファイル名がセクション区切りとして表示されます）
                      </p>
                      <ConversationList
                        conversations={previewData.conversations}
                        speakerColors={speakerColors}
                        speakerTextColors={speakerTextColors}
                        onRemove={() => {}} // バッチモードでは削除不可
                        readOnly={true}
                      />
                    </>
                  )}
                </Card>
              )}
            </>
          )}

          {/* 確認と開始ボタン */}
          <Card className="animate-fade-in">
            <div className="space-y-4">
              {hasNoBackgrounds() && (
                <div className="p-3 bg-warning-50 dark:bg-warning-900/20 rounded-lg border border-warning-200 dark:border-warning-800">
                  <p className="text-sm text-warning-700 dark:text-warning-400">
                    ⚠️ 背景画像が不足しています。生成に失敗する可能性があります。
                  </p>
                </div>
              )}
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="confirm-batch"
                  checked={confirmed}
                  onChange={(e) => setConfirmed(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  disabled={isLoadingPreview}
                />
                <label
                  htmlFor="confirm-batch"
                  className="text-sm text-gray-700 dark:text-gray-300"
                >
                  選択した {selectedFiles.size} 件のファイルの内容を確認しました
                </label>
              </div>
              <Button
                onClick={handleStartGeneration}
                disabled={!confirmed || isLoadingPreview || isCheckingBackgrounds}
                className="w-full"
                leftIcon={<Play className="h-5 w-5" />}
              >
                バッチ生成を開始 ({selectedFiles.size}件)
              </Button>
            </div>
          </Card>
        </>
      )}

      {/* 完了サマリー */}
      {!batchState.isGenerating &&
        (batchState.completedFiles.length > 0 ||
          batchState.failedFiles.length > 0) && (
          <Card className="animate-fade-in">
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900 dark:text-white">
                生成結果
              </h4>
              <div className="flex gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <span className="text-gray-700 dark:text-gray-300">
                    成功: {batchState.completedFiles.length}件
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <span className="text-gray-700 dark:text-gray-300">
                    失敗: {batchState.failedFiles.length}件
                  </span>
                </div>
              </div>
            </div>
          </Card>
        )}
    </div>
  );
};
