import { useState } from "react";
import toast from "react-hot-toast";
import {
  FileText,
  Sparkles,
  Settings as SettingsIcon,
  CheckCircle,
  RefreshCw,
  Download,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Select from "@/components/Select";
import ProgressBar from "@/components/ProgressBar";
import Badge from "@/components/Badge";
import { useScriptStore } from "@/stores/scriptStore";
import { scriptApi } from "@/api/scripts";

const ScriptGenerationPage = () => {
  const {
    foodName,
    setFoodName,
    model,
    setModel,
    temperature,
    setTemperature,
    outline,
    setOutline,
    isGeneratingOutline,
    setGeneratingOutline,
    isGeneratingSections,
    progress,
    statusMessage,
    generatedScript,
  } = useScriptStore();

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleGenerateOutline = async () => {
    if (!foodName.trim()) {
      toast.error("食べ物の名前を入力してください");
      return;
    }

    setGeneratingOutline(true);

    try {
      const result = await scriptApi.generateOutline({
        food_name: foodName,
        model,
        temperature,
      });
      setOutline(result.outline);
      toast.success("アウトラインを生成しました！");
    } catch (err: any) {
      toast.error(
        err.response?.data?.detail || "アウトライン生成に失敗しました"
      );
      console.error("Outline generation error:", err);
    } finally {
      setGeneratingOutline(false);
    }
  };

  const handleApproveOutline = async () => {
    // TODO: セクション生成APIを呼び出す
    toast.success("動画生成を開始します");
    console.log("Approve outline and generate sections");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          動画台本生成
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          食べ物を食べすぎるとどうなるのか？をテーマに、ずんだもんたちが面白く解説する動画脚本を作成します
        </p>
      </div>

      <Card icon={<FileText className="h-6 w-6" />} title="台本設定">
        <div className="space-y-6">
          {/* 食べ物入力 */}
          <Input
            label="調べたい食べ物"
            value={foodName}
            onChange={(e) => setFoodName(e.target.value)}
            placeholder="例: チョコレート"
            helperText="一般的な食べ物や飲み物の名前を入力してください"
            leftIcon={<Sparkles className="h-5 w-5" />}
          />

          {/* 詳細設定 */}
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
            >
              <div className="flex items-center gap-2">
                <SettingsIcon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  詳細設定
                </span>
              </div>
              {showAdvanced ? (
                <ChevronUp className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              )}
            </button>

            {showAdvanced && (
              <div className="p-4 space-y-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 animate-fade-in">
                <Select
                  label="AIモデル"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                >
                  <option value="claude-3-5-sonnet">
                    Claude 3.5 Sonnet (推奨)
                  </option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gemini-pro">Gemini Pro</option>
                </Select>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    創造性レベル: {temperature.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                    高いほど創造的ですが、一貫性が下がる可能性があります
                  </p>
                </div>
              </div>
            )}
          </div>

          <Button
            onClick={handleGenerateOutline}
            disabled={!foodName.trim() || isGeneratingOutline}
            isLoading={isGeneratingOutline}
            className="w-full"
            leftIcon={<FileText className="h-5 w-5" />}
          >
            アウトラインを生成
          </Button>
        </div>
      </Card>

      {/* アウトライン表示 */}
      {outline && (
        <Card
          icon={<FileText className="h-6 w-6" />}
          title="生成されたアウトライン"
          headerAction={<Badge variant="info">確認待ち</Badge>}
          className="animate-fade-in"
        >
          <div className="space-y-4">
            <div className="grid gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  タイトル
                </p>
                <p className="text-base font-semibold text-gray-900 dark:text-white">
                  {outline.title}
                </p>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  食べ物
                </p>
                <p className="text-base text-gray-900 dark:text-white">
                  {outline.food_name}
                </p>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  冒頭フック
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {outline.hook_content}
                </p>
              </div>

              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                  背景情報
                </p>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {outline.background_content}
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Button
                onClick={handleApproveOutline}
                disabled={isGeneratingSections}
                className="flex-1"
                leftIcon={<CheckCircle className="h-5 w-5" />}
              >
                このアウトラインで動画を生成
              </Button>
              <Button
                variant="outline"
                onClick={handleGenerateOutline}
                disabled={isGeneratingOutline}
                leftIcon={<RefreshCw className="h-5 w-5" />}
              >
                再生成
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* セクション生成進捗 */}
      {isGeneratingSections && (
        <Card className="animate-fade-in">
          <ProgressBar
            progress={progress * 100}
            message={statusMessage}
            variant="default"
          />
        </Card>
      )}

      {/* 生成結果 */}
      {generatedScript && (
        <Card
          icon={<CheckCircle className="h-6 w-6" />}
          title="台本生成完了！"
          headerAction={<Badge variant="success">完了</Badge>}
          className="animate-fade-in"
        >
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
                <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
                  タイトル
                </p>
                <p className="text-base font-semibold text-success-900 dark:text-success-300">
                  {generatedScript.title}
                </p>
              </div>

              <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
                <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
                  推定時間
                </p>
                <p className="text-base font-semibold text-success-900 dark:text-success-300">
                  {generatedScript.estimated_duration}
                </p>
              </div>

              <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
                <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
                  セリフ数
                </p>
                <p className="text-base font-semibold text-success-900 dark:text-success-300">
                  {generatedScript.all_segments.length}
                </p>
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full"
              leftIcon={<Download className="h-5 w-5" />}
            >
              JSONをダウンロード
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ScriptGenerationPage;
