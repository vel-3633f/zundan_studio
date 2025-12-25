import { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import {
  Video,
  Plus,
  Play,
  Download,
  MessageSquare,
  Trash2,
  User,
  Upload,
} from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Select from "@/components/Select";
import ProgressBar from "@/components/ProgressBar";
import Badge from "@/components/Badge";
import IconButton from "@/components/IconButton";
import { useVideoStore } from "@/stores/videoStore";
import { videoApi } from "@/api/videos";
import type { ConversationLine, VideoSection, ConversationSegment } from "@/types";

const HomePage = () => {
  const [speaker, setSpeaker] = useState("zundamon");
  const [text, setText] = useState("");
  const [jsonFiles, setJsonFiles] = useState<Array<{ filename: string; path: string }>>([]);
  const [selectedJsonFile, setSelectedJsonFile] = useState<string>("");
  const [isLoadingJsonFiles, setIsLoadingJsonFiles] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const {
    conversations,
    addConversation,
    removeConversation,
    setConversations,
    setSections,
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

  // 話者名の変換マップ
  const speakerMap: Record<string, string> = {
    "めたん": "metan",
    "ずんだもん": "zundamon",
    "つむぎ": "tsumugi",
  };

  // JSONデータを処理してvideoStoreに設定する共通関数
  const processJsonData = (jsonData: any) => {
    // JSON構造の検証
    if (!jsonData.sections || !Array.isArray(jsonData.sections)) {
      toast.error("無効なJSON形式です。sections配列が見つかりません。");
      return false;
    }

    // セクション情報をVideoSection形式に変換
    const videoSections: VideoSection[] = jsonData.sections.map(
      (section: any) => ({
        section_name: section.section_name || "",
        section_key: section.section_key,
        scene_background: section.scene_background || "",
        bgm_id: section.bgm_id || "none",
        bgm_volume: section.bgm_volume ?? 0,
        segments: section.segments || [],
      })
    );

    // 全セクションのsegmentsをフラット化してConversationLineに変換
    const conversationLines: ConversationLine[] = [];
    videoSections.forEach((section) => {
      section.segments.forEach((segment: ConversationSegment) => {
        // 話者名を変換
        const speakerKey = speakerMap[segment.speaker] || segment.speaker;

        conversationLines.push({
          speaker: speakerKey,
          text: segment.text,
          text_for_voicevox: segment.text_for_voicevox,
          expression: segment.expression || "normal",
          background: section.scene_background,
        });
      });
    });

    if (conversationLines.length === 0) {
      toast.error("会話データが見つかりませんでした。");
      return false;
    }

    // videoStoreに設定
    setConversations(conversationLines);
    setSections(videoSections);

    toast.success(`${conversationLines.length}件の会話を読み込みました`);
    return true;
  };

  // JSONファイル一覧を取得
  useEffect(() => {
    const loadJsonFiles = async () => {
      try {
        setIsLoadingJsonFiles(true);
        const files = await videoApi.listJsonFiles();
        setJsonFiles(files);
        if (files.length > 0 && !selectedJsonFile) {
          setSelectedJsonFile(files[0].filename);
        }
      } catch (error) {
        console.error("JSONファイル一覧取得エラー:", error);
        toast.error("JSONファイル一覧の取得に失敗しました");
      } finally {
        setIsLoadingJsonFiles(false);
      }
    };

    loadJsonFiles();
  }, []);

  // 選択されたJSONファイルから会話データを読み込む
  const handleLoadSelectedJson = async () => {
    if (!selectedJsonFile) {
      toast.error("JSONファイルを選択してください");
      return;
    }

    try {
      const jsonData = await videoApi.getJsonFile(selectedJsonFile);
      processJsonData(jsonData);
    } catch (error: any) {
      console.error("JSON読み込みエラー:", error);
      if (error.response?.status === 404) {
        toast.error("ファイルが見つかりませんでした。");
      } else {
        toast.error("ファイルの読み込みに失敗しました。");
      }
    }
  };

  // ファイルアップロード用（後方互換性のため保持）
  const handleLoadJson = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    // ファイル拡張子の確認
    if (!file.name.endsWith(".json")) {
      toast.error("JSONファイルを選択してください");
      return;
    }

    try {
      const fileContent = await file.text();
      const jsonData = JSON.parse(fileContent);
      processJsonData(jsonData);

      // ファイル入力のリセット（同じファイルを再度選択できるように）
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("JSON読み込みエラー:", error);
      if (error instanceof SyntaxError) {
        toast.error("JSONファイルの形式が正しくありません。");
      } else {
        toast.error("ファイルの読み込みに失敗しました。");
      }
    }
  };

  const handleJsonLoadClick = () => {
    fileInputRef.current?.click();
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
        <div className="space-y-6">
          {/* JSON読み込み */}
          <div className="space-y-3">
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <Select
                  label="JSONファイルを選択"
                  value={selectedJsonFile}
                  onChange={(e) => setSelectedJsonFile(e.target.value)}
                  disabled={isLoadingJsonFiles || jsonFiles.length === 0}
                >
                  <option value="">
                    {isLoadingJsonFiles
                      ? "読み込み中..."
                      : jsonFiles.length === 0
                      ? "JSONファイルが見つかりません"
                      : "ファイルを選択してください"}
                  </option>
                  {jsonFiles.map((file) => (
                    <option key={file.filename} value={file.filename}>
                      {file.filename}
                    </option>
                  ))}
                </Select>
              </div>
              <Button
                onClick={handleLoadSelectedJson}
                variant="outline"
                disabled={!selectedJsonFile || isLoadingJsonFiles}
                leftIcon={<Upload className="h-5 w-5" />}
              >
                読み込む
              </Button>
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              または
            </div>
            <div className="flex gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept=".json"
                onChange={handleLoadJson}
                className="hidden"
              />
              <Button
                onClick={handleJsonLoadClick}
                variant="outline"
                leftIcon={<Upload className="h-5 w-5" />}
              >
                ファイルから読み込む
              </Button>
            </div>
          </div>

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
                      ] || "text-gray-700 dark:text-gray-400"
                    }`}
                  >
                    {conv.speaker === "zundamon"
                      ? "ずんだもん"
                      : conv.speaker === "metan"
                      ? "四国めたん"
                      : conv.speaker === "tsumugi"
                      ? "つむぎ"
                      : conv.speaker === "narrator"
                      ? "ナレーター"
                      : conv.speaker}
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
