import { useState, useEffect } from "react";
import { ChevronDown, ChevronUp, FileText, Clock, Hash } from "lucide-react";
import Badge from "@/components/Badge";
import type { JsonFileInfo } from "@/types";
import { videoApi } from "@/api/videos";

interface JsonFilePreviewProps {
  file: JsonFileInfo;
}

export const JsonFilePreview = ({ file }: JsonFilePreviewProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [jsonData, setJsonData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isExpanded && !jsonData && !isLoading) {
      loadJsonData();
    }
  }, [isExpanded]);

  const loadJsonData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await videoApi.getJsonFile(file.filename);
      setJsonData(data);
    } catch (err: any) {
      console.error("JSONファイル読み込みエラー:", err);
      setError("ファイルの読み込みに失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const getTotalSegments = () => {
    if (!jsonData?.sections) return 0;
    return jsonData.sections.reduce(
      (total: number, section: any) => total + (section.segments?.length || 0),
      0
    );
  };

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-900 dark:text-white">
            {file.filename}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-500" />
        )}
      </button>

      {isExpanded && (
        <div className="p-4 space-y-3 bg-white dark:bg-gray-900">
          {isLoading && (
            <p className="text-sm text-gray-500 dark:text-gray-400">
              読み込み中...
            </p>
          )}

          {error && (
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          )}

          {jsonData && (
            <>
              {/* タイトル */}
              {jsonData.title && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    タイトル
                  </p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {jsonData.title}
                  </p>
                </div>
              )}

              {/* メタ情報 */}
              <div className="flex flex-wrap gap-2">
                {jsonData.estimated_duration && (
                  <Badge variant="info" className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {jsonData.estimated_duration}
                  </Badge>
                )}
                {jsonData.sections && (
                  <Badge variant="default" className="flex items-center gap-1">
                    <Hash className="h-3 w-3" />
                    {jsonData.sections.length}セクション
                  </Badge>
                )}
                {jsonData.sections && (
                  <Badge variant="default" className="flex items-center gap-1">
                    <Hash className="h-3 w-3" />
                    {getTotalSegments()}セリフ
                  </Badge>
                )}
                {jsonData.mode && (
                  <Badge variant="default">{jsonData.mode}</Badge>
                )}
              </div>

              {/* テーマ */}
              {jsonData.theme && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    テーマ
                  </p>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {jsonData.theme}
                  </p>
                </div>
              )}

              {/* セクション一覧 */}
              {jsonData.sections && jsonData.sections.length > 0 && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                    セクション構成
                  </p>
                  <div className="space-y-1">
                    {jsonData.sections.map((section: any, idx: number) => (
                      <div
                        key={idx}
                        className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2"
                      >
                        <span className="font-mono text-gray-400">
                          {idx + 1}.
                        </span>
                        <span>{section.section_name || "無題"}</span>
                        <span className="text-gray-400">
                          ({section.segments?.length || 0}セリフ)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* YouTubeメタデータ */}
              {jsonData.youtube_metadata && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    YouTubeタグ
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {jsonData.youtube_metadata.tags?.map(
                      (tag: string, idx: number) => (
                        <span
                          key={idx}
                          className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded"
                        >
                          {tag}
                        </span>
                      )
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};
