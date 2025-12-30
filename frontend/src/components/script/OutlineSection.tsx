import {
  FileText,
  CheckCircle,
  RefreshCw,
  Smile,
  Meh,
  Frown,
  Copy,
  Youtube,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import IconButton from "@/components/IconButton";
import type {
  ComedyOutline,
  SectionDefinition,
  YouTubeMetadata,
} from "@/types";

interface OutlineSectionProps {
  outline: ComedyOutline;
  youtubeMetadata?: YouTubeMetadata | null;
  isGenerating: boolean;
  isApprovingLoading?: boolean;
  isRegeneratingLoading?: boolean;
  onApprove: () => void;
  onRegenerate: () => void;
}

const OutlineSection = ({
  outline,
  youtubeMetadata,
  isGenerating,
  isApprovingLoading = false,
  isRegeneratingLoading = false,
  onApprove,
  onRegenerate,
}: OutlineSectionProps) => {
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

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

  const handleCopy = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success(`${label}をコピーしました`);
    } catch (error) {
      toast.error("コピーに失敗しました");
      console.error("Copy error:", error);
    }
  };

  const handleCopyTags = async () => {
    if (!youtubeMetadata) return;
    const tagsText = youtubeMetadata.tags.join(", ");
    await handleCopy(tagsText, "タグ");
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

        {/* キャラクター機嫌レベルと強制終了タイプ */}
        <div className="p-4 bg-warning-50 dark:bg-warning-900/20 rounded-lg border border-warning-200 dark:border-warning-800">
          <p className="text-sm font-medium text-warning-700 dark:text-warning-400 mb-3">
            キャラクター機嫌レベル（ランダム生成）
          </p>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex flex-col items-center">
              {getMoodIcon(outline.character_moods.zundamon)}
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                ずんだもん
              </span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {outline.character_moods.zundamon}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {getMoodLabel(outline.character_moods.zundamon)}
              </span>
            </div>
            <div className="flex flex-col items-center">
              {getMoodIcon(outline.character_moods.metan)}
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                めたん
              </span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {outline.character_moods.metan}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {getMoodLabel(outline.character_moods.metan)}
              </span>
            </div>
            <div className="flex flex-col items-center">
              {getMoodIcon(outline.character_moods.tsumugi)}
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">
                つむぎ
              </span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {outline.character_moods.tsumugi}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {getMoodLabel(outline.character_moods.tsumugi)}
              </span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-error-50 dark:bg-error-900/20 rounded-lg border border-error-200 dark:border-error-800">
          <p className="text-sm font-medium text-error-700 dark:text-error-400 mb-1">
            オチのタイプ
          </p>
          <p className="text-base font-semibold text-error-900 dark:text-error-100">
            {outline.ending_type}
          </p>
        </div>

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
                  <p className="text-xs text-primary-600 dark:text-primary-400 mt-1">
                    <span className="font-medium">背景:</span> {section.background}
                  </p>
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

        {/* YouTubeメタデータ */}
        {youtubeMetadata && (
          <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
            <div className="flex items-center gap-2 mb-4">
              <Youtube className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <h3 className="text-lg font-semibold text-primary-900 dark:text-primary-100">
                YouTubeメタデータ
              </h3>
            </div>

            <div className="space-y-4">
              {/* タグ */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-primary-700 dark:text-primary-300">
                    タグ ({youtubeMetadata.tags.length}個)
                  </label>
                  <IconButton
                    onClick={handleCopyTags}
                    variant="ghost"
                    size="sm"
                    aria-label="タグをコピー"
                  >
                    <Copy className="h-4 w-4" />
                  </IconButton>
                </div>
                <div className="flex flex-wrap gap-2">
                  {youtubeMetadata.tags.map((tag, index) => (
                    <Badge key={index} variant="default">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* 説明文 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-primary-700 dark:text-primary-300">
                    説明文 ({youtubeMetadata.description.length}文字)
                  </label>
                  <div className="flex items-center gap-2">
                    <IconButton
                      onClick={() =>
                        handleCopy(youtubeMetadata.description, "説明文")
                      }
                      variant="ghost"
                      size="sm"
                      aria-label="説明文をコピー"
                    >
                      <Copy className="h-4 w-4" />
                    </IconButton>
                    {youtubeMetadata.description.length > 200 && (
                      <IconButton
                        onClick={() =>
                          setIsDescriptionExpanded(!isDescriptionExpanded)
                        }
                        variant="ghost"
                        size="sm"
                        aria-label={
                          isDescriptionExpanded
                            ? "説明文を折りたたむ"
                            : "説明文を展開"
                        }
                      >
                        {isDescriptionExpanded ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </IconButton>
                    )}
                  </div>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded border border-primary-200 dark:border-primary-700">
                  <p
                    className={`text-sm text-primary-900 dark:text-primary-100 whitespace-pre-wrap ${
                      !isDescriptionExpanded &&
                      youtubeMetadata.description.length > 200
                        ? "line-clamp-6"
                        : ""
                    }`}
                  >
                    {youtubeMetadata.description}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

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
