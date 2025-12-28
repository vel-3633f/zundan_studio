import { useState } from "react";
import {
  Image,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  XCircle,
  Loader2,
} from "lucide-react";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import type { BackgroundCheckResponse } from "@/types";
import { cn } from "@/lib/utils";

interface BackgroundCheckCardProps {
  result: BackgroundCheckResponse | null;
  isLoading?: boolean;
}

const BackgroundCheckCard = ({
  result,
  isLoading = false,
}: BackgroundCheckCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusVariant = () => {
    if (!result) return "default";
    if (result.missing === 0) return "success";
    if (result.available === 0) return "error";
    return "warning";
  };

  const getStatusIcon = () => {
    if (isLoading) {
      return <Loader2 className="h-5 w-5 animate-spin text-gray-400" />;
    }
    if (!result) return null;
    if (result.missing === 0) {
      return <CheckCircle2 className="h-5 w-5 text-success-500" />;
    }
    return <XCircle className="h-5 w-5 text-warning-500" />;
  };

  const getStatusText = () => {
    if (isLoading) return "確認中...";
    if (!result) return "JSONファイルを読み込んでください";
    if (result.total === 0) return "背景画像が指定されていません";
    if (result.missing === 0) {
      return `すべての画像が利用可能です (${result.available}/${result.total})`;
    }
    return `${result.available}個利用可能、${result.missing}個不足 (合計${result.total}個)`;
  };

  if (!result && !isLoading) {
    return null;
  }

  return (
    <Card
      icon={<Image className="h-6 w-6" />}
      title="背景画像確認"
      headerAction={
        result && (
          <Badge variant={getStatusVariant()}>
            {result.available}/{result.total}
          </Badge>
        )
      }
    >
      {isLoading && !result && (
        <div className="flex items-center gap-3 py-4">
          <Loader2 className="h-5 w-5 animate-spin text-primary-600" />
          <span className="text-gray-600 dark:text-gray-400">
            背景画像を確認中...
          </span>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          {/* ステータス表示 */}
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {getStatusText()}
            </p>
          </div>

          {/* 詳細リスト（展開可能） */}
          {result.files.length > 0 && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center justify-between w-full text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg p-2 -m-2 transition-colors"
              >
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  詳細を表示 ({result.files.length}件)
                </span>
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4 text-gray-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                )}
              </button>

              {isExpanded && (
                <div className="mt-3 space-y-2 max-h-96 overflow-y-auto">
                  {result.files.map((file) => (
                    <div
                      key={file.name}
                      className={cn(
                        "flex items-center justify-between p-3 rounded-lg border",
                        file.exists
                          ? "bg-success-50/50 dark:bg-success-900/10 border-success-200 dark:border-success-800"
                          : "bg-error-50/50 dark:bg-error-900/10 border-error-200 dark:border-error-800"
                      )}
                    >
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {file.exists ? (
                          <CheckCircle2 className="h-4 w-4 text-success-500 flex-shrink-0" />
                        ) : (
                          <XCircle className="h-4 w-4 text-error-500 flex-shrink-0" />
                        )}
                        <span
                          className={cn(
                            "text-sm font-mono truncate",
                            file.exists
                              ? "text-success-700 dark:text-success-400"
                              : "text-error-700 dark:text-error-400"
                          )}
                        >
                          {file.name}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {result.files.length === 0 && (
            <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                JSONファイルに背景画像の指定がありません
              </p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

export default BackgroundCheckCard;

