import { Info } from "lucide-react";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import type { JsonScriptData } from "@/types";

interface JsonMetadataProps {
  jsonScriptData: JsonScriptData;
}

export const JsonMetadata = ({ jsonScriptData }: JsonMetadataProps) => {
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

  return (
    <Card
      icon={<Info className="h-6 w-6" />}
      title="JSONメタ情報"
      className="animate-fade-in"
    >
      <div className="space-y-4">
        <div>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            タイトル
          </p>
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
      </div>
    </Card>
  );
};

