import { Sparkles, RefreshCw, ArrowLeft, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import type { ComedyTitleBatch } from "@/types";

interface TitleCandidatesSectionProps {
  titleBatch: ComedyTitleBatch;
  isGenerating: boolean;
  onSelectTitle: (candidateId: number) => void;
  onRegenerate: () => void;
  onBack?: () => void;
}

const TitleCandidatesSection = ({
  titleBatch,
  isGenerating,
  onSelectTitle,
  onRegenerate,
  onBack,
}: TitleCandidatesSectionProps) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

  const getHookPatternIcon = (pattern: string) => {
    const icons: Record<string, string> = {
      属性反転: "🔄",
      理不尽な数値化: "🔢",
      語彙の誤解: "❓",
      物理的解決: "💪",
      コンプラの暴走: "⚠️",
    };
    return icons[pattern] || "📌";
  };

  // カテゴリ別にグループ化
  const categorizedTitles = titleBatch.titles.reduce((acc, title) => {
    const category = title.hook_pattern;
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(title);
    return acc;
  }, {} as Record<string, typeof titleBatch.titles>);

  const categories = Object.keys(categorizedTitles).sort();

  return (
    <Card
      icon={<Sparkles className="h-6 w-6" />}
      title="ランダムタイトル候補"
      headerAction={
        <Button
          variant="outline"
          size="sm"
          onClick={onRegenerate}
          disabled={isGenerating}
          leftIcon={<RefreshCw className="h-4 w-4" />}
        >
          再生成
        </Button>
      }
      className="animate-fade-in"
    >
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            全{titleBatch.titles.length}個のタイトル候補 - カテゴリをクリックして表示
          </p>
          {onBack && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onBack}
              disabled={isGenerating}
              leftIcon={<ArrowLeft className="h-4 w-4" />}
            >
              戻る
            </Button>
          )}
        </div>

        {/* カテゴリ別表示 */}
        {categories.map((category) => {
          const isCategoryExpanded = expandedCategory === category;
          const titlesInCategory = categorizedTitles[category];
          
          return (
            <div
              key={category}
              className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
            >
              {/* カテゴリヘッダー */}
              <button
                onClick={() =>
                  setExpandedCategory(isCategoryExpanded ? null : category)
                }
                className="w-full px-4 py-3 flex items-center justify-between bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-750 hover:from-gray-100 hover:to-gray-200 dark:hover:from-gray-750 dark:hover:to-gray-700 transition-all"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getHookPatternIcon(category)}</span>
                  <div className="text-left">
                    <h3 className="font-bold text-gray-900 dark:text-white">
                      {category}
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {titlesInCategory.length}個のタイトル
                    </p>
                  </div>
                </div>
                {isCategoryExpanded ? (
                  <ChevronUp className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                )}
              </button>

              {/* カテゴリ内のタイトル一覧 */}
              {isCategoryExpanded && (
                <div className="p-3 space-y-2 bg-white dark:bg-gray-800 animate-fade-in">
                  {titlesInCategory.map((candidate) => {
                    const isExpanded = expandedId === candidate.id;
                    return (
                      <div
                        key={candidate.id}
                        className="rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-all overflow-hidden"
                      >
                        {/* タイトル部分（クリックで選択） */}
                        <button
                          onClick={() => onSelectTitle(candidate.id)}
                          disabled={isGenerating}
                          className="w-full text-left p-3 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
                        >
                          <div className="space-y-2">
                            {/* タイトル */}
                            <h4 className="text-base font-bold text-gray-900 dark:text-white group-hover:text-primary-700 dark:group-hover:text-primary-300">
                              {candidate.title}
                            </h4>

                            {/* メタ情報 */}
                            <div className="flex flex-wrap gap-2">
                              <Badge variant="default" className="text-xs">
                                {candidate.situation}
                              </Badge>
                            </div>
                          </div>
                        </button>

                        {/* 詳細表示トグル */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedId(isExpanded ? null : candidate.id);
                          }}
                          className="w-full px-3 py-1.5 flex items-center justify-between bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors border-t border-gray-200 dark:border-gray-700"
                        >
                          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                            {isExpanded ? "詳細を隠す" : "詳細を見る"}
                          </span>
                          {isExpanded ? (
                            <ChevronUp className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                          ) : (
                            <ChevronDown className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                          )}
                        </button>

                        {/* 詳細情報（折りたたみ） */}
                        {isExpanded && (
                          <div className="p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 animate-fade-in">
                            <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
                              <div>
                                <span className="font-medium text-gray-700 dark:text-gray-300">
                                  カオス要素:
                                </span>{" "}
                                {candidate.chaos_element}
                              </div>
                              <div>
                                <span className="font-medium text-gray-700 dark:text-gray-300">
                                  予想される対立:
                                </span>{" "}
                                {candidate.expected_conflict}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default TitleCandidatesSection;
