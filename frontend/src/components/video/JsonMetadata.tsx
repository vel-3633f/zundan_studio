import { Info, Copy, Youtube, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import IconButton from "@/components/IconButton";
import type { JsonScriptData } from "@/types";

interface JsonMetadataProps {
  jsonScriptData: JsonScriptData;
}

export const JsonMetadata = ({ jsonScriptData }: JsonMetadataProps) => {
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

  const getCharacterName = (character: string) => {
    switch (character) {
      case "zundamon":
        return "ずんだもん";
      case "metan":
        return "四国めたん";
      case "tsumugi":
        return "つむぎ";
      default:
        return character;
    }
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
    if (!jsonScriptData.youtube_metadata) return;
    const tagsText = jsonScriptData.youtube_metadata.tags.join(", ");
    await handleCopy(tagsText, "タグ");
  };

  const handleCopyAllMetadata = async () => {
    if (!jsonScriptData.youtube_metadata) return;
    const allText = jsonScriptData.youtube_metadata.description;
    await handleCopy(allText, "YouTubeメタデータ");
  };

  return (
    <Card
      icon={<Info className="h-6 w-6" />}
      title="JSONメタ情報"
      className="animate-fade-in"
    >
      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-1">
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              タイトル
            </p>
            <IconButton
              icon={<Copy className="h-4 w-4" />}
              onClick={() => handleCopy(jsonScriptData.title, "タイトル")}
              variant="ghost"
              size="sm"
              aria-label="タイトルをコピー"
            />
          </div>
          <p className="text-base font-semibold text-gray-900 dark:text-white">
            {jsonScriptData.title}
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              モード
            </p>
            <Badge variant="default">{jsonScriptData.mode}</Badge>
          </div>
          {jsonScriptData.estimated_duration && (
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                推定時間
              </p>
              <p className="text-sm text-gray-900 dark:text-white">
                {jsonScriptData.estimated_duration}
              </p>
            </div>
          )}
        </div>
        {jsonScriptData.theme && (
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              テーマ
            </p>
            <p className="text-sm text-gray-900 dark:text-white">
              {jsonScriptData.theme}
            </p>
          </div>
        )}
        {jsonScriptData.character_moods && (
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              キャラクターのムード
            </p>
            <div className="space-y-2">
              {Object.entries(jsonScriptData.character_moods).map(
                ([character, mood]) => (
                  <div key={character}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-gray-700 dark:text-gray-300">
                        {getCharacterName(character)}
                      </span>
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">
                        {mood}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full transition-all"
                        style={{ width: `${mood}%` }}
                      />
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}
        {jsonScriptData.youtube_metadata && (
          <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Youtube className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                <h3 className="text-lg font-semibold text-primary-900 dark:text-primary-100">
                  YouTubeメタデータ
                </h3>
              </div>
              <IconButton
                icon={<Copy className="h-4 w-4" />}
                onClick={handleCopyAllMetadata}
                variant="ghost"
                size="sm"
                aria-label="YouTubeメタデータ全体をコピー"
                title="説明文全体をコピー"
              />
            </div>

            <div className="space-y-4">
              {/* タグ */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-primary-700 dark:text-primary-300">
                    タグ ({jsonScriptData.youtube_metadata.tags.length}個)
                  </label>
                  <IconButton
                    icon={<Copy className="h-4 w-4" />}
                    onClick={handleCopyTags}
                    variant="ghost"
                    size="sm"
                    aria-label="タグをコピー"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  {jsonScriptData.youtube_metadata.tags.map((tag, index) => (
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
                    説明文 ({jsonScriptData.youtube_metadata.description.length}文字)
                  </label>
                  <div className="flex items-center gap-2">
                    <IconButton
                      icon={<Copy className="h-4 w-4" />}
                      onClick={() =>
                        handleCopy(
                          jsonScriptData.youtube_metadata!.description,
                          "説明文"
                        )
                      }
                      variant="ghost"
                      size="sm"
                      aria-label="説明文をコピー"
                    />
                    {jsonScriptData.youtube_metadata.description.length > 200 && (
                      <IconButton
                        icon={
                          isDescriptionExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )
                        }
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
                      />
                    )}
                  </div>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded border border-primary-200 dark:border-primary-700">
                  <p
                    className={`text-sm text-primary-900 dark:text-primary-100 whitespace-pre-wrap ${
                      !isDescriptionExpanded &&
                      jsonScriptData.youtube_metadata.description.length > 200
                        ? "line-clamp-6"
                        : ""
                    }`}
                  >
                    {jsonScriptData.youtube_metadata.description}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

