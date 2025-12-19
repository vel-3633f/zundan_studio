import { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import ProgressBar from "@/components/ProgressBar";
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

  const [error, setError] = useState<string | null>(null);

  const handleGenerateOutline = async () => {
    if (!foodName.trim()) return;

    setError(null);
    setGeneratingOutline(true);

    try {
      const result = await scriptApi.generateOutline({
        food_name: foodName,
        model,
        temperature,
      });
      setOutline(result.outline);
    } catch (err: any) {
      setError(err.response?.data?.detail || "アウトライン生成に失敗しました");
      console.error("Outline generation error:", err);
    } finally {
      setGeneratingOutline(false);
    }
  };

  const handleApproveOutline = async () => {
    // TODO: セクション生成APIを呼び出す
    console.log("Approve outline and generate sections");
  };

  return (
    <div className="space-y-6">
      <Card title="📚 動画台本生成">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          食べ物を食べすぎるとどうなるのか？をテーマに、ずんだもんたちが面白く解説する動画脚本を作成します
        </p>

        {/* 食べ物入力 */}
        <div className="space-y-4">
          <Input
            label="調べたい食べ物"
            value={foodName}
            onChange={(e) => setFoodName(e.target.value)}
            placeholder="例: チョコレート"
            helperText="一般的な食べ物や飲み物の名前を入力してください"
          />

          {/* 詳細設定 */}
          <details className="mt-4">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300">
              ⚙️ 詳細設定
            </summary>
            <div className="mt-4 space-y-4 pl-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  AIモデル
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="claude-3-5-sonnet">
                    Claude 3.5 Sonnet (推奨)
                  </option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gemini-pro">Gemini Pro</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  創造性レベル: {temperature.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  高いほど創造的ですが、一貫性が下がる可能性があります
                </p>
              </div>
            </div>
          </details>

          <Button
            onClick={handleGenerateOutline}
            disabled={!foodName.trim() || isGeneratingOutline}
            isLoading={isGeneratingOutline}
            className="w-full"
          >
            {isGeneratingOutline
              ? "アウトライン生成中..."
              : "📋 アウトラインを生成"}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}
        </div>

        {/* アウトライン表示 */}
        {outline && (
          <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h4 className="text-lg font-medium text-blue-900 dark:text-blue-300 mb-3">
              📋 生成されたアウトライン
            </h4>
            <div className="space-y-2 text-sm">
              <p>
                <strong>タイトル:</strong> {outline.title}
              </p>
              <p>
                <strong>食べ物:</strong> {outline.food_name}
              </p>
              <p>
                <strong>冒頭フック:</strong> {outline.hook_content}
              </p>
              <p>
                <strong>背景情報:</strong> {outline.background_content}
              </p>
            </div>
            <div className="mt-4 flex space-x-3">
              <Button
                onClick={handleApproveOutline}
                disabled={isGeneratingSections}
              >
                ✅ このアウトラインで動画を生成
              </Button>
              <Button variant="secondary" onClick={handleGenerateOutline}>
                🔄 別のアウトラインを生成
              </Button>
            </div>
          </div>
        )}

        {/* セクション生成進捗 */}
        {isGeneratingSections && (
          <div className="mt-6">
            <ProgressBar progress={progress * 100} message={statusMessage} />
          </div>
        )}

        {/* 生成結果 */}
        {generatedScript && (
          <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <h4 className="text-lg font-medium text-green-800 dark:text-green-300 mb-2">
              🎉 台本生成完了！
            </h4>
            <p className="text-sm text-green-700 dark:text-green-400 mb-3">
              タイトル: {generatedScript.title}
            </p>
            <p className="text-sm text-green-700 dark:text-green-400 mb-3">
              推定時間: {generatedScript.estimated_duration}
            </p>
            <p className="text-sm text-green-700 dark:text-green-400 mb-3">
              セリフ数: {generatedScript.all_segments.length}
            </p>
            <Button variant="secondary">JSONをダウンロード</Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ScriptGenerationPage;
