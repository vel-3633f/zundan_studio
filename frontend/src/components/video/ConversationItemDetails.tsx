import { getSpeakerName, getExpressionLabel } from "@/utils/speakerUtils";
import type { ConversationLine } from "@/types";

interface ConversationItemDetailsProps {
  conv: ConversationLine;
}

export const ConversationItemDetails = ({
  conv,
}: ConversationItemDetailsProps) => {
  return (
    <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2 text-xs">
      {conv.scene_background && (
        <div>
          <span className="font-medium text-gray-600 dark:text-gray-400">
            背景:{" "}
          </span>
          <span className="text-gray-700 dark:text-gray-300">
            {conv.scene_background}
          </span>
        </div>
      )}
      {conv.visible_characters && conv.visible_characters.length > 0 && (
        <div>
          <span className="font-medium text-gray-600 dark:text-gray-400">
            表示キャラクター:{" "}
          </span>
          <span className="text-gray-700 dark:text-gray-300">
            {conv.visible_characters.join(", ")}
          </span>
        </div>
      )}
      {conv.character_expressions &&
        Object.keys(conv.character_expressions).length > 0 && (
          <div>
            <span className="font-medium text-gray-600 dark:text-gray-400">
              キャラクター表情:{" "}
            </span>
            <div className="mt-1 space-y-1">
              {Object.entries(conv.character_expressions).map(
                ([char, expr]) => (
                  <div
                    key={char}
                    className="text-gray-700 dark:text-gray-300"
                  >
                    {getSpeakerName(char)}: {getExpressionLabel(expr)}
                  </div>
                )
              )}
            </div>
          </div>
        )}
      {conv.bgm_id && (
        <div>
          <span className="font-medium text-gray-600 dark:text-gray-400">
            BGM:{" "}
          </span>
          <span className="text-gray-700 dark:text-gray-300">
            {conv.bgm_id === "none" ? "なし" : conv.bgm_id}
            {conv.bgm_volume !== undefined &&
              conv.bgm_volume > 0 &&
              ` (volume: ${conv.bgm_volume})`}
          </span>
        </div>
      )}
      {conv.text_for_voicevox && (
        <div>
          <span className="font-medium text-gray-600 dark:text-gray-400">
            VOICEVOX用テキスト:{" "}
          </span>
          <span className="text-gray-700 dark:text-gray-300 break-words">
            {conv.text_for_voicevox}
          </span>
        </div>
      )}
    </div>
  );
};

