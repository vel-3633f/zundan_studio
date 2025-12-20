import { Sparkles, RefreshCw } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import type { ComedyTitleBatch } from "@/types";

interface TitleCandidatesSectionProps {
  titleBatch: ComedyTitleBatch;
  isGenerating: boolean;
  onSelectTitle: (candidateId: number) => void;
  onRegenerate: () => void;
}

const TitleCandidatesSection = ({
  titleBatch,
  isGenerating,
  onSelectTitle,
  onRegenerate,
}: TitleCandidatesSectionProps) => {
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
        <p className="text-sm text-gray-600 dark:text-gray-400">
          気に入ったタイトルをクリックして選択してください
        </p>

        {titleBatch.titles.map((candidate) => (
          <button
            key={candidate.id}
            onClick={() => onSelectTitle(candidate.id)}
            disabled={isGenerating}
            className="w-full text-left p-4 rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all group"
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

              {/* 詳細情報 */}
              <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p>
                  <span className="font-medium">カオス要素:</span>{" "}
                  {candidate.chaos_element}
                </p>
                <p>
                  <span className="font-medium">予想される対立:</span>{" "}
                  {candidate.expected_conflict}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </Card>
  );
};

export default TitleCandidatesSection;
