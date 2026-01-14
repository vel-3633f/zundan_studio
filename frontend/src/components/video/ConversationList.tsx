import type { ConversationLine } from "@/types";
import { ConversationItem } from "./ConversationItem";

interface ConversationListProps {
  conversations: ConversationLine[];
  speakerColors: Record<string, string>;
  speakerTextColors: Record<string, string>;
  onRemove: (index: number) => void;
  readOnly?: boolean;
}

export const ConversationList = ({
  conversations,
  speakerColors,
  speakerTextColors,
  onRemove,
  readOnly = false,
}: ConversationListProps) => {
  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto scrollbar-thin pr-2">
      {conversations.map((conv, index) => {
        const prevConv = index > 0 ? conversations[index - 1] : null;
        const showSectionDivider =
          conv.section_name &&
          (!prevConv || prevConv.section_name !== conv.section_name);

        return (
          <div key={index} className="space-y-0">
            {showSectionDivider && (
              <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700 mb-3 rounded-t-lg">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                  📍 セクション: {conv.section_name}
                </p>
              </div>
            )}
            <ConversationItem
              conv={conv}
              index={index}
              speakerColors={speakerColors}
              speakerTextColors={speakerTextColors}
              onRemove={readOnly ? undefined : onRemove}
            />
          </div>
        );
      })}
    </div>
  );
};

