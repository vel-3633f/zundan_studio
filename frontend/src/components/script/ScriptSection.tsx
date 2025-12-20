import { CheckCircle, Download, Smile, Meh, Frown } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import type { FoodScript, ComedyScript, ScriptMode } from "@/types";

interface ScriptSectionProps {
  mode: ScriptMode;
  script: FoodScript | ComedyScript;
}

const ScriptSection = ({ mode, script }: ScriptSectionProps) => {
  const isFoodMode = mode === "food";
  const comedyScript = !isFoodMode ? (script as ComedyScript) : null;

  const handleDownload = () => {
    const dataStr = JSON.stringify(script, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `script_${mode}_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // 機嫌レベルのアイコンを取得
  const getMoodIcon = (mood: number) => {
    if (mood >= 70) return <Smile className="h-4 w-4 text-success-500" />;
    if (mood >= 30) return <Meh className="h-4 w-4 text-warning-500" />;
    return <Frown className="h-4 w-4 text-error-500" />;
  };

  return (
    <Card
      icon={<CheckCircle className="h-6 w-6" />}
      title="台本生成完了！"
      headerAction={<Badge variant="success">完了</Badge>}
      className="animate-fade-in"
    >
      <div className="space-y-6">
        {/* 基本情報 */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
            <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
              タイトル
            </p>
            <p className="text-base font-semibold text-success-900 dark:text-success-300">
              {script.title}
            </p>
          </div>

          <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
            <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
              推定時間
            </p>
            <p className="text-base font-semibold text-success-900 dark:text-success-300">
              {script.estimated_duration}
            </p>
          </div>

          <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
            <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
              セリフ数
            </p>
            <p className="text-base font-semibold text-success-900 dark:text-success-300">
              {script.all_segments.length}
            </p>
          </div>
        </div>

        {/* お笑いモード専用情報 */}
        {!isFoodMode && comedyScript && (
          <div className="space-y-4">
            {/* 機嫌レベル */}
            <div className="p-4 bg-warning-50 dark:bg-warning-900/20 rounded-lg border border-warning-200 dark:border-warning-800">
              <p className="text-sm font-medium text-warning-700 dark:text-warning-400 mb-3">
                キャラクター機嫌レベル
              </p>
              <div className="flex gap-4 justify-around">
                <div className="flex items-center gap-2">
                  {getMoodIcon(comedyScript.character_moods.zundamon)}
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    ずんだもん: {comedyScript.character_moods.zundamon}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {getMoodIcon(comedyScript.character_moods.metan)}
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    めたん: {comedyScript.character_moods.metan}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {getMoodIcon(comedyScript.character_moods.tsumugi)}
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    つむぎ: {comedyScript.character_moods.tsumugi}
                  </span>
                </div>
              </div>
            </div>

            {/* 強制終了タイプ */}
            <div className="p-4 bg-error-50 dark:bg-error-900/20 rounded-lg border border-error-200 dark:border-error-800">
              <p className="text-sm font-medium text-error-700 dark:text-error-400 mb-1">
                強制終了タイプ
              </p>
              <p className="text-base font-semibold text-error-900 dark:text-error-100">
                {comedyScript.ending_type}
              </p>
            </div>
          </div>
        )}

        {/* セクション一覧 */}
        <div>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            セクション構成（{script.sections.length}セクション）
          </p>
          <div className="space-y-2">
            {script.sections.map((section, index) => (
              <div
                key={section.section_key || index}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {index + 1}. {section.section_name}
                </span>
                <Badge variant="default">{section.segments.length}セリフ</Badge>
              </div>
            ))}
          </div>
        </div>

        {/* ダウンロードボタン */}
        <Button
          variant="outline"
          className="w-full"
          leftIcon={<Download className="h-5 w-5" />}
          onClick={handleDownload}
        >
          JSONをダウンロード
        </Button>
      </div>
    </Card>
  );
};

export default ScriptSection;
