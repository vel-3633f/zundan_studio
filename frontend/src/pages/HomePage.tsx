import toast from "react-hot-toast";
import { Video, Play, Download, MessageSquare } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import ProgressBar from "@/components/ProgressBar";
import Badge from "@/components/Badge";
import { useVideoStore } from "@/stores/videoStore";
import { ConversationList } from "@/components/video/ConversationList";
import { JsonLoader } from "@/components/video/JsonLoader";
import { JsonMetadata } from "@/components/video/JsonMetadata";
import { useJsonLoader } from "@/hooks/useJsonLoader";
import { useVideoGeneration } from "@/hooks/useVideoGeneration";
import BackgroundCheckCard from "@/components/resources/BackgroundCheckCard";

const HomePage = () => {
  const {
    conversations,
    removeConversation,
    jsonScriptData,
    isGenerating,
    progress,
    statusMessage,
    generatedVideoPath,
  } = useVideoStore();

  const {
    jsonFiles,
    selectedJsonFile,
    isLoadingJsonFiles,
    setSelectedJsonFile,
    handleLoadSelectedJson,
    handleLoadJson,
    backgroundCheckResult,
    isCheckingBackgrounds,
    isGeneratingBackgrounds,
    generateMissingBackgrounds,
  } = useJsonLoader();

  const { handleGenerate } = useVideoGeneration();

  const handleRemove = (index: number) => {
    removeConversation(index);
    toast.success("セリフを削除しました");
  };

  const speakerColors = {
    zundamon:
      "bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700",
    metan:
      "bg-pink-100 dark:bg-pink-900/30 border-pink-300 dark:border-pink-700",
    tsumugi:
      "bg-purple-100 dark:bg-purple-900/30 border-purple-300 dark:border-purple-700",
    narrator:
      "bg-gray-100 dark:bg-gray-800/30 border-gray-300 dark:border-gray-700",
  };

  const speakerTextColors = {
    zundamon: "text-green-700 dark:text-green-400",
    metan: "text-pink-700 dark:text-pink-400",
    tsumugi: "text-purple-700 dark:text-purple-400",
    narrator: "text-gray-700 dark:text-gray-400",
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
        <JsonLoader
          jsonFiles={jsonFiles}
          selectedJsonFile={selectedJsonFile}
          isLoadingJsonFiles={isLoadingJsonFiles}
          onSelectedFileChange={setSelectedJsonFile}
          onLoadSelected={handleLoadSelectedJson}
          onLoadFromFile={handleLoadJson}
        />
      </Card>

      <BackgroundCheckCard
        result={backgroundCheckResult}
        isLoading={isCheckingBackgrounds}
        isGenerating={isGeneratingBackgrounds}
        onGenerateMissing={
          selectedJsonFile
            ? () => generateMissingBackgrounds(selectedJsonFile)
            : undefined
        }
      />

      {jsonScriptData && <JsonMetadata jsonScriptData={jsonScriptData} />}

      {conversations.length > 0 && (
        <Card
          icon={<MessageSquare className="h-6 w-6" />}
          title="会話リスト"
          headerAction={<Badge variant="info">{conversations.length}件</Badge>}
          className="animate-fade-in"
        >
          <ConversationList
            conversations={conversations}
            speakerColors={speakerColors}
            speakerTextColors={speakerTextColors}
            onRemove={handleRemove}
          />

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
            まだ会話データが読み込まれていません
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500">
            上のフォームからJSONファイルを読み込んでください
          </p>
        </Card>
      )}

      {isGenerating && (
        <Card className="animate-fade-in">
          <ProgressBar
            progress={progress * 100}
            message={statusMessage}
            variant="default"
          />
        </Card>
      )}

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
