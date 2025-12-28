import { useState } from "react";
import { User, Trash2, ChevronDown, ChevronUp } from "lucide-react";
import Badge from "@/components/Badge";
import IconButton from "@/components/IconButton";
import type { ConversationLine } from "@/types";
import { getSpeakerName, getExpressionLabel } from "@/utils/speakerUtils";
import { ConversationItemDetails } from "./ConversationItemDetails";

interface ConversationItemProps {
  conv: ConversationLine;
  index: number;
  speakerColors: Record<string, string>;
  speakerTextColors: Record<string, string>;
  onRemove: (index: number) => void;
}

export const ConversationItem = ({
  conv,
  index,
  speakerColors,
  speakerTextColors,
  onRemove,
}: ConversationItemProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className={`rounded-lg border-2 transition-all hover:shadow-md ${
        speakerColors[conv.speaker as keyof typeof speakerColors] ||
        "bg-gray-100 dark:bg-gray-800/30 border-gray-300 dark:border-gray-700"
      }`}
    >
      <div className="flex items-start gap-3 p-4">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white dark:bg-gray-800 flex items-center justify-center shadow-sm">
          <User className="h-4 w-4 text-gray-600 dark:text-gray-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <p
              className={`text-sm font-semibold ${
                speakerTextColors[
                  conv.speaker as keyof typeof speakerTextColors
                ] || "text-gray-700 dark:text-gray-400"
              }`}
            >
              {getSpeakerName(conv.speaker)}
            </p>
            {conv.expression && (
              <Badge variant="default" className="text-xs">
                {getExpressionLabel(conv.expression)}
              </Badge>
            )}
          </div>
          <p className="text-sm text-gray-700 dark:text-gray-300 break-words mb-2">
            {conv.text}
          </p>

          {isExpanded && <ConversationItemDetails conv={conv} />}

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="mt-2 text-xs text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center gap-1"
          >
            {isExpanded ? (
              <>
                <ChevronUp className="h-3 w-3" />
                詳細を折りたたむ
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" />
                詳細を表示
              </>
            )}
          </button>
        </div>
        <IconButton
          icon={<Trash2 className="h-4 w-4" />}
          variant="danger"
          size="sm"
          onClick={() => onRemove(index)}
          aria-label="削除"
        />
      </div>
    </div>
  );
};

