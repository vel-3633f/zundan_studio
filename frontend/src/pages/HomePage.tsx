import { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import ProgressBar from "@/components/ProgressBar";
import { useVideoStore } from "@/stores/videoStore";

const HomePage = () => {
  const [speaker, setSpeaker] = useState("zundamon");
  const [text, setText] = useState("");

  const {
    conversations,
    addConversation,
    removeConversation,
    isGenerating,
    progress,
    statusMessage,
    generatedVideoPath,
  } = useVideoStore();

  const handleAddConversation = () => {
    if (text.trim()) {
      addConversation({
        speaker,
        text: text.trim(),
        expression: "normal",
        background: "default",
      });
      setText("");
    }
  };

  const handleGenerate = async () => {
    // TODO: 動画生成APIを呼び出す
    console.log("Generate video with conversations:", conversations);
  };

  return (
    <div className="space-y-6">
      <Card title="🏠 ずんだもん会話動画生成">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          ずんだもんとゲストキャラクターの会話動画を作成できます
        </p>

        {/* 会話入力 */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-1">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                話者
              </label>
              <select
                value={speaker}
                onChange={(e) => setSpeaker(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option
                  value="zundamon"
                  className="bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  ずんだもん
                </option>
                <option
                  value="metan"
                  className="bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  四国めたん
                </option>
              </select>
            </div>
            <div className="md:col-span-3">
              <Input
                label="セリフ"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="セリフを入力してください"
                onKeyPress={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleAddConversation();
                  }
                }}
              />
            </div>
          </div>
          <Button onClick={handleAddConversation} disabled={!text.trim()}>
            セリフを追加
          </Button>
        </div>

        {/* 会話リスト */}
        {conversations.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              会話リスト ({conversations.length}件)
            </h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {conversations.map((conv, index) => (
                <div
                  key={index}
                  className="flex items-start justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex-1">
                    <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
                      {conv.speaker}:
                    </span>
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      {conv.text}
                    </span>
                  </div>
                  <button
                    onClick={() => removeConversation(index)}
                    className="ml-2 text-red-600 hover:text-red-700 dark:text-red-400"
                  >
                    削除
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 生成ボタン */}
        <div className="mt-6">
          <Button
            onClick={handleGenerate}
            disabled={conversations.length === 0 || isGenerating}
            isLoading={isGenerating}
            className="w-full"
          >
            {isGenerating ? "生成中..." : "🎭 会話動画を生成"}
          </Button>
          {conversations.length === 0 && (
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 text-center">
              ※ セリフを追加してから生成ボタンを押してください
            </p>
          )}
        </div>

        {/* 進捗表示 */}
        {isGenerating && (
          <div className="mt-4">
            <ProgressBar progress={progress * 100} message={statusMessage} />
          </div>
        )}

        {/* 結果表示 */}
        {generatedVideoPath && (
          <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <h4 className="text-lg font-medium text-green-800 dark:text-green-300 mb-2">
              🎉 動画生成完了！
            </h4>
            <p className="text-sm text-green-700 dark:text-green-400 mb-3">
              動画パス: {generatedVideoPath}
            </p>
            <Button variant="secondary">ダウンロード</Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default HomePage;
