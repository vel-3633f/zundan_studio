import { FileText, CheckCircle, RefreshCw } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import type { ComedyTitle } from "@/types";

interface TitleSectionProps {
  title: ComedyTitle;
  isGenerating: boolean;
  isApprovingLoading?: boolean;
  isRegeneratingLoading?: boolean;
  onApprove: () => void;
  onRegenerate: () => void;
}

const TitleSection = ({
  title,
  isGenerating,
  isApprovingLoading = false,
  isRegeneratingLoading = false,
  onApprove,
  onRegenerate,
}: TitleSectionProps) => {

  return (
    <Card
      icon={<FileText className="h-6 w-6" />}
      title="生成されたタイトル"
      headerAction={<Badge variant="info">確認待ち</Badge>}
      className="animate-fade-in"
    >
      <div className="space-y-4">
        {/* タイトル表示 */}
        <div className="p-6 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/30 dark:to-primary-800/30 rounded-lg border-2 border-primary-200 dark:border-primary-700">
          <p className="text-sm font-medium text-primary-600 dark:text-primary-400 mb-2">
            YouTubeタイトル
          </p>
          <h2 className="text-2xl font-bold text-primary-900 dark:text-primary-100">
            {title.title}
          </h2>
        </div>

        {/* 詳細情報 */}
        <div className="grid gap-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
              テーマ
            </p>
            <p className="text-base text-gray-900 dark:text-white">
              {title.theme}
            </p>
          </div>
          <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
              煽り要素
            </p>
            <div className="flex flex-wrap gap-2">
              {title.clickbait_elements.map((element, index) => (
                <Badge key={index} variant="warning">
                  {element}
                </Badge>
              ))}
            </div>
          </div>
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
            このタイトルでアウトラインを生成
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

export default TitleSection;
