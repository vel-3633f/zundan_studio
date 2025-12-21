import {
  FileText,
  CheckCircle,
  RefreshCw,
  Smile,
  Meh,
  Frown,
} from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import type {
  FoodOutline,
  ComedyOutline,
  ScriptMode,
  SectionDefinition,
} from "@/types";

interface OutlineSectionProps {
  mode: ScriptMode;
  outline: FoodOutline | ComedyOutline;
  isGenerating: boolean;
  isApprovingLoading?: boolean;
  isRegeneratingLoading?: boolean;
  onApprove: () => void;
  onRegenerate: () => void;
}

const OutlineSection = ({
  mode,
  outline,
  isGenerating,
  isApprovingLoading = false,
  isRegeneratingLoading = false,
  onApprove,
  onRegenerate,
}: OutlineSectionProps) => {
  const isFoodMode = mode === "food";
  const comedyOutline = !isFoodMode ? (outline as ComedyOutline) : null;

  // 機嫌レベルのアイコンを取得
  const getMoodIcon = (mood: number) => {
    if (mood >= 70) return <Smile className="h-5 w-5 text-success-500" />;
    if (mood >= 30) return <Meh className="h-5 w-5 text-warning-500" />;
    return <Frown className="h-5 w-5 text-error-500" />;
  };

  const getMoodLabel = (mood: number) => {
    if (mood >= 70) return "高い";
    if (mood >= 30) return "普通";
    return "低い";
  };

  return (
    <Card
      icon={<FileText className="h-6 w-6" />}
      title="生成されたアウトライン"
      headerAction={<Badge variant="info">確認待ち</Badge>}
      className="animate-fade-in"
    >
      <div className="space-y-6">
        {/* タイトル表示 */}
        <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
            タイトル
          </p>
          <p className="text-lg font-semibold text-gray-900 dark:text-white">
            {outline.title}
          </p>
        </div>

        {/* ストーリー要約 */}
        <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
            ストーリー概要
          </p>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {outline.story_summary}
          </p>
        </div>

        {/* お笑いモード専用: 機嫌レベルと強制終了タイプ */}
        {!isFoodMode && comedyOutline && (
          <>
            <div className="p-4 bg-warning-50 dark:bg-warning-900/20 rounded-lg border border-warning-200 dark:border-warning-800">
              <p className="text-sm font-medium text-warning-700 dark:text-warning-400 mb-3">
                キャラクター機嫌レベル（ランダム生成）
              </p>
              <div className="grid grid-cols-3 gap-4">
                <div className="flex flex-col items-center">
                  {getMoodIcon(comedyOutline.character_moods.zundamon)}
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                    ずんだもん
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {comedyOutline.character_moods.zundamon}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {getMoodLabel(comedyOutline.character_moods.zundamon)}
                  </span>
                </div>
                <div className="flex flex-col items-center">
                  {getMoodIcon(comedyOutline.character_moods.metan)}
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                    めたん
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {comedyOutline.character_moods.metan}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {getMoodLabel(comedyOutline.character_moods.metan)}
                  </span>
                </div>
                <div className="flex flex-col items-center">
                  {getMoodIcon(comedyOutline.character_moods.tsumugi)}
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                    つむぎ
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {comedyOutline.character_moods.tsumugi}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {getMoodLabel(comedyOutline.character_moods.tsumugi)}
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-error-50 dark:bg-error-900/20 rounded-lg border border-error-200 dark:border-error-800">
              <p className="text-sm font-medium text-error-700 dark:text-error-400 mb-1">
                強制終了タイプ
              </p>
              <p className="text-base font-semibold text-error-900 dark:text-error-100">
                {comedyOutline.forced_ending_type}
              </p>
            </div>
          </>
        )}

        {/* セクション構成 */}
        <div>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            セクション構成（{outline.sections.length}セクション）
          </p>
          <div className="space-y-3">
            {outline.sections.map(
              (section: SectionDefinition, index: number) => (
                <div
                  key={section.section_key}
                  className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                      {index + 1}. {section.section_name}
                    </h4>
                    <Badge variant="default">
                      {section.min_lines}-{section.max_lines}セリフ
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                    <span className="font-medium">目的:</span> {section.purpose}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    <span className="font-medium">内容:</span>{" "}
                    {section.content_summary}
                  </p>
                  {section.fixed_background && (
                    <p className="text-xs text-primary-600 dark:text-primary-400 mt-1">
                      固定背景: {section.fixed_background}
                    </p>
                  )}
                </div>
              )
            )}
          </div>
        </div>

        {/* 合計セリフ数の目安 */}
        <div className="p-3 bg-info-50 dark:bg-info-900/20 rounded-lg border border-info-200 dark:border-info-800">
          <p className="text-sm text-info-700 dark:text-info-300">
            推定セリフ数:{" "}
            {outline.sections.reduce((sum, s) => sum + s.min_lines, 0)} 〜{" "}
            {outline.sections.reduce((sum, s) => sum + s.max_lines, 0)} セリフ
          </p>
        </div>

        {/* アクションボタン */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <Button
            onClick={onApprove}
            disabled={isGenerating}
            isLoading={isApprovingLoading}
            className="flex-1"
            leftIcon={<CheckCircle className="h-5 w-5" />}
          >
            このアウトラインで台本を生成
          </Button>
          <Button
            variant="outline"
            onClick={onRegenerate}
            disabled={isGenerating}
            isLoading={isRegeneratingLoading}
            leftIcon={<RefreshCw className="h-5 w-5" />}
          >
            再生成
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default OutlineSection;
