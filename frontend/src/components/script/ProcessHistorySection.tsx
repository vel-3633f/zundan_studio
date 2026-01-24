import { useState } from "react";
import { ChevronDown, ChevronUp, FileText, List } from "lucide-react";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import type { ComedyTitle, ComedyOutline, YouTubeMetadata } from "@/types";

interface ProcessHistorySectionProps {
  title: ComedyTitle | null;
  outline: ComedyOutline | null;
  youtubeMetadata: YouTubeMetadata | null;
}

const ProcessHistorySection = ({
  title,
  outline,
  youtubeMetadata,
}: ProcessHistorySectionProps) => {
  const [isTitleExpanded, setIsTitleExpanded] = useState(false);
  const [isOutlineExpanded, setIsOutlineExpanded] = useState(false);

  if (!title && !outline) {
    return null;
  }

  return (
    <Card
      icon={<List className="h-6 w-6" />}
      title="生成過程"
      className="animate-fade-in"
    >
      <div className="space-y-3">
        {/* タイトル */}
        {title && (
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => setIsTitleExpanded(!isTitleExpanded)}
              className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                <span className="font-medium text-gray-900 dark:text-white">
                  1. タイトル
                </span>
                <Badge variant="success">生成済み</Badge>
              </div>
              {isTitleExpanded ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>

            {isTitleExpanded && (
              <div className="p-4 space-y-3 bg-white dark:bg-gray-900">
                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    タイトル
                  </div>
                  <div className="text-base text-gray-900 dark:text-white">
                    {title.title}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    テーマ
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {title.theme}
                  </div>
                </div>
                {title.clickbait_elements &&
                  title.clickbait_elements.length > 0 && (
                    <div>
                      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        クリックベイト要素
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {title.clickbait_elements.map((element, idx) => (
                          <Badge key={idx} variant="info">
                            {element}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            )}
          </div>
        )}

        {/* アウトライン */}
        {outline && (
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => setIsOutlineExpanded(!isOutlineExpanded)}
              className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <div className="flex items-center gap-3">
                <List className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                <span className="font-medium text-gray-900 dark:text-white">
                  2. アウトライン
                </span>
                <Badge variant="success">生成済み</Badge>
              </div>
              {isOutlineExpanded ? (
                <ChevronUp className="h-5 w-5 text-gray-500" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-500" />
              )}
            </button>

            {isOutlineExpanded && (
              <div className="p-4 space-y-4 bg-white dark:bg-gray-900">
                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    ストーリー概要
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {outline.story_summary}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    セクション構成（{outline.sections.length}セクション）
                  </div>
                  <div className="space-y-2">
                    {outline.sections.map((section, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700"
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <div className="font-medium text-sm text-gray-900 dark:text-white">
                            {idx + 1}. {section.section_name}
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {section.min_lines}-{section.max_lines}セリフ
                          </Badge>
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          {section.content_summary}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    オチのタイプ
                  </div>
                  <Badge variant="info">{outline.ending_type}</Badge>
                </div>

                {youtubeMetadata && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      YouTube メタデータ
                    </div>
                    <div className="space-y-2">
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          タグ
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {youtubeMetadata.tags.map((tag, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                          説明文
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap p-2 bg-gray-50 dark:bg-gray-800/50 rounded">
                          {youtubeMetadata.description}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

export default ProcessHistorySection;
