import { useState } from "react";
import toast from "react-hot-toast";
import {
  Video,
  Plus,
  Play,
  Download,
  MessageSquare,
  Trash2,
  User,
} from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Select from "@/components/Select";
import ProgressBar from "@/components/ProgressBar";
import Badge from "@/components/Badge";
import IconButton from "@/components/IconButton";
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
      toast.success("セリフを追加しました");
    }
  };

  const handleGenerate = async () => {
    if (conversations.length === 0) {
      toast.error("セリフを追加してください");
      return;
    }
    // TODO: 動画生成APIを呼び出す
    toast.success("動画生成を開始します");
    console.log("Generate video with conversations:", conversations);
  };

  const handleRemove = (index: number) => {
    removeConversation(index);
    toast.success("セリフを削除しました");
  };

  const speakerColors = {
    zundamon:
      "bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700",
    metan:
      "bg-pink-100 dark:bg-pink-900/30 border-pink-300 dark:border-pink-700",
  };

  const speakerTextColors = {
    zundamon: "text-green-700 dark:text-green-400",
    metan: "text-pink-700 dark:text-pink-400",
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          会話動画生成
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          ずんだもんとゲストキャラクターの会話動画を作成できます
        </p>
      </div>

      <Card icon={<Video className="h-6 w-6" />} title="会話設定">
        <div className="space-y-6">
          {/* 会話入力 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-1">
              <Select
                label="話者"
                value={speaker}
                onChange={(e) => setSpeaker(e.target.value)}
                leftIcon={<User className="h-5 w-5" />}
              >
                <option value="zundamon">ずんだもん</option>
                <option value="metan">四国めたん</option>
              </Select>
            </div>
            <div className="md:col-span-3">
              <Input
                label="セリフ"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="セリフを入力してください"
                leftIcon={<MessageSquare className="h-5 w-5" />}
                onKeyPress={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleAddConversation();
                  }
                }}
              />
            </div>
          </div>

          <Button
            onClick={handleAddConversation}
            disabled={!text.trim()}
            leftIcon={<Plus className="h-5 w-5" />}
          >
            セリフを追加
          </Button>
        </div>
      </Card>

      {/* 会話リスト */}
      {conversations.length > 0 && (
        <Card
          icon={<MessageSquare className="h-6 w-6" />}
          title="会話リスト"
          headerAction={<Badge variant="info">{conversations.length}件</Badge>}
          className="animate-fade-in"
        >
          <div className="space-y-3 max-h-[500px] overflow-y-auto scrollbar-thin pr-2">
            {conversations.map((conv, index) => (
              <div
                key={index}
                className={`flex items-start gap-3 p-4 rounded-lg border-2 transition-all hover:shadow-md ${
                  speakerColors[conv.speaker as keyof typeof speakerColors]
                }`}
              >
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white dark:bg-gray-800 flex items-center justify-center shadow-sm">
                  <User className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm font-semibold mb-1 ${
                      speakerTextColors[
                        conv.speaker as keyof typeof speakerTextColors
                      ]
                    }`}
                  >
                    {conv.speaker === "zundamon" ? "ずんだもん" : "四国めたん"}
                  </p>
                  <p className="text-sm text-gray-700 dark:text-gray-300 break-words">
                    {conv.text}
                  </p>
                </div>
                <IconButton
                  icon={<Trash2 className="h-4 w-4" />}
                  variant="danger"
                  size="sm"
                  onClick={() => handleRemove(index)}
                  aria-label="削除"
                />
              </div>
            ))}
          </div>

          {/* 生成ボタン */}
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <Button
              onClick={handleGenerate}
              disabled={conversations.length === 0 || isGenerating}
              isLoading={isGenerating}
              className="w-full"
              leftIcon={<Play className="h-5 w-5" />}
            >
              会話動画を生成
            </Button>
          </div>
        </Card>
      )}

      {conversations.length === 0 && (
        <Card className="text-center py-12">
          <MessageSquare className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400 mb-2">
            まだセリフが追加されていません
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            上のフォームからセリフを追加してください
          </p>
        </Card>
      )}

      {/* 進捗表示 */}
      {isGenerating && (
        <Card className="animate-fade-in">
          <ProgressBar
            progress={progress * 100}
            message={statusMessage}
            variant="default"
          />
        </Card>
      )}

      {/* 結果表示 */}
      {generatedVideoPath && (
        <Card
          icon={<Video className="h-6 w-6" />}
          title="動画生成完了！"
          headerAction={<Badge variant="success">完了</Badge>}
          className="animate-fade-in"
        >
          <div className="space-y-4">
            <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
              <p className="text-sm font-medium text-success-700 dark:text-success-400 mb-1">
                動画パス
              </p>
              <p className="text-sm font-mono text-success-900 dark:text-success-300 break-all">
                {generatedVideoPath}
              </p>
            </div>

            <Button
              variant="outline"
              className="w-full"
              leftIcon={<Download className="h-5 w-5" />}
            >
              動画をダウンロード
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default HomePage;
