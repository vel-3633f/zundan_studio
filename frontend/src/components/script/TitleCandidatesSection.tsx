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
  const getHookPatternColor = (pattern: string) => {
    const colors: Record<string, string> = {
      属性反転:
        "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
      理不尽な数値化:
        "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
      語彙の誤解:
        "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
      物理的解決:
        "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
      コンプラの暴走:
        "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
    };
    return (
      colors[pattern] ||
      "bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300"
    );
  };

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
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            気に入ったタイトルをクリックして選択してください
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

        {titleBatch.titles.map((candidate) => {
          const isExpanded = expandedId === candidate.id;
          return (
            <div
              key={candidate.id}
              className="rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-all overflow-hidden"
            >
              {/* タイトル部分（クリックで選択） */}
              <button
                onClick={() => onSelectTitle(candidate.id)}
                disabled={isGenerating}
                className="w-full text-left p-4 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
              >
                <div className="space-y-2">
                  {/* タイトル */}
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-primary-700 dark:group-hover:text-primary-300">
                    {candidate.title}
                  </h3>

                  {/* メタ情報 */}
                  <div className="flex flex-wrap gap-2">
                    <span
                      className={`text-xs px-2 py-1 rounded-full font-medium ${getHookPatternColor(
                        candidate.hook_pattern
                      )}`}
                    >
                      {candidate.hook_pattern}
                    </span>
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
                className="w-full px-4 py-2 flex items-center justify-between bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors border-t border-gray-200 dark:border-gray-700"
              >
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                  {isExpanded ? "詳細を隠す" : "詳細を見る"}
                </span>
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                )}
              </button>

              {/* 詳細情報（折りたたみ） */}
              {isExpanded && (
                <div className="p-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 animate-fade-in">
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
    </Card>
  );
};

export default TitleCandidatesSection;
