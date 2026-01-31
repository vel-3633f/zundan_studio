import { Zap, Hand } from "lucide-react";

interface AutoModeToggleProps {
  isAutoMode: boolean;
  onToggle: (isAuto: boolean) => void;
  disabled?: boolean;
}

const AutoModeToggle = ({
  isAutoMode,
  onToggle,
  disabled = false,
}: AutoModeToggleProps) => {
  return (
    <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 flex-1">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <Hand className="h-4 w-4" />
          <span>手動モード</span>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400">
          各段階で確認
        </div>
      </div>

      <button
        type="button"
        onClick={() => onToggle(!isAutoMode)}
        disabled={disabled}
        className={`
          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
          dark:focus:ring-offset-gray-900
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          ${
            isAutoMode
              ? "bg-primary-600 dark:bg-primary-500"
              : "bg-gray-300 dark:bg-gray-600"
          }
        `}
        aria-label="自動モード切り替え"
      >
        <span
          className={`
            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
            ${isAutoMode ? "translate-x-6" : "translate-x-1"}
          `}
        />
      </button>

      <div className="flex items-center gap-2 flex-1 justify-end">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          一括生成+自動保存
        </div>
        <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          <span>自動モード</span>
          <Zap className="h-4 w-4" />
        </div>
      </div>
    </div>
  );
};

export default AutoModeToggle;
