import { Sparkles, CheckCircle, RefreshCw, ArrowLeft } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import type { FoodTitle, ComedyTitle, ScriptMode } from "@/types";

interface SingleTitleCandidateSectionProps {
  mode: ScriptMode;
  title: FoodTitle | ComedyTitle;
  isGenerating: boolean;
  onSelectTitle: () => void;
  onRegenerate: () => void;
  onBack?: () => void;
}

const SingleTitleCandidateSection = ({
  mode,
  title,
  isGenerating,
  onSelectTitle,
  onRegenerate,
  onBack,
}: SingleTitleCandidateSectionProps) => {
  const isFoodMode = mode === "food";
  const foodTitle = isFoodMode ? (title as FoodTitle) : null;
  const comedyTitle = !isFoodMode ? (title as ComedyTitle) : null;

  return (
    <Card
      icon={<Sparkles className="h-6 w-6" />}
      title="生成されたタイトル"
      headerAction={<Badge variant="info">選択待ち</Badge>}
      className="animate-fade-in"
    >
      <div className="space-y-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          このタイトルで次に進むか、再生成してください
        </p>

        {/* タイトル表示 */}
        <div className="p-6 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/30 dark:to-primary-800/30 rounded-lg border-2 border-primary-200 dark:border-primary-700">
          <p className="text-sm font-medium text-primary-600 dark:text-primary-400 mb-2">
            YouTubeタイトル
          </p>
          <h2 className="text-2xl font-bold text-primary-900 dark:text-primary-100">
            {title.title}
          </h2>
        </div>

        {/* モード別の詳細情報 */}
        <div className="grid gap-4">
          {isFoodMode && foodTitle && (
            <>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  食べ物
                </p>
                <p className="text-base text-gray-900 dark:text-white">
                  {foodTitle.food_name}
                </p>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  フック要素
                </p>
                <p className="text-base text-gray-900 dark:text-white">
                  {foodTitle.hook_phrase}
                </p>
              </div>
            </>
          )}

          {!isFoodMode && comedyTitle && (
            <>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  テーマ
                </p>
                <p className="text-base text-gray-900 dark:text-white">
                  {comedyTitle.theme}
                </p>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                  煽り要素
                </p>
                <div className="flex flex-wrap gap-2">
                  {comedyTitle.clickbait_elements.map((element, index) => (
                    <Badge key={index} variant="warning">
                      {element}
                    </Badge>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* アクションボタン */}
        <div className="space-y-3 pt-2">
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onSelectTitle}
              disabled={isGenerating}
              className="flex-1"
              leftIcon={<CheckCircle className="h-5 w-5" />}
            >
              このタイトルで次へ進む
            </Button>
            <Button
              variant="outline"
              onClick={onRegenerate}
              disabled={isGenerating}
              leftIcon={<RefreshCw className="h-5 w-5" />}
            >
              再生成
            </Button>
          </div>
          {onBack && (
            <Button
              variant="ghost"
              onClick={onBack}
              disabled={isGenerating}
              className="w-full"
              leftIcon={<ArrowLeft className="h-5 w-5" />}
            >
              入力画面に戻る
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default SingleTitleCandidateSection;

