import { Utensils, Laugh } from "lucide-react";
import type { ScriptMode } from "@/types";

interface ModeSelectorProps {
  mode: ScriptMode;
  onModeChange: (mode: ScriptMode) => void;
  disabled?: boolean;
}

const ModeSelector = ({
  mode,
  onModeChange,
  disabled = false,
}: ModeSelectorProps) => {
  return (
    <div className="flex gap-4">
      <button
        onClick={() => onModeChange("comedy")}
        disabled={disabled}
        className={`
          flex-1 p-6 rounded-lg border-2 transition-all
          ${
            mode === "comedy"
              ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
              : "border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700"
          }
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
        `}
      >
        <div className="flex flex-col items-center gap-3">
          <Laugh
            className={`h-8 w-8 ${
              mode === "comedy"
                ? "text-primary-600 dark:text-primary-400"
                : "text-gray-400 dark:text-gray-500"
            }`}
          />
          <div className="text-center">
            <h3
              className={`text-lg font-bold ${
                mode === "comedy"
                  ? "text-primary-900 dark:text-primary-100"
                  : "text-gray-700 dark:text-gray-300"
              }`}
            >
              😂 お笑いモード
            </h3>
            <p
              className={`text-sm mt-1 ${
                mode === "comedy"
                  ? "text-primary-700 dark:text-primary-300"
                  : "text-gray-500 dark:text-gray-400"
              }`}
            >
              バカバカしい漫談・教訓なし
            </p>
          </div>
        </div>
      </button>

      <button
        onClick={() => onModeChange("food")}
        disabled={disabled}
        className={`
          flex-1 p-6 rounded-lg border-2 transition-all
          ${
            mode === "food"
              ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
              : "border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700"
          }
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
        `}
      >
        <div className="flex flex-col items-center gap-3">
          <Utensils
            className={`h-8 w-8 ${
              mode === "food"
                ? "text-primary-600 dark:text-primary-400"
                : "text-gray-400 dark:text-gray-500"
            }`}
          />
          <div className="text-center">
            <h3
              className={`text-lg font-bold ${
                mode === "food"
                  ? "text-primary-900 dark:text-primary-100"
                  : "text-gray-700 dark:text-gray-300"
              }`}
            >
              🍔 食べ物モード
            </h3>
            <p
              className={`text-sm mt-1 ${
                mode === "food"
                  ? "text-primary-700 dark:text-primary-300"
                  : "text-gray-500 dark:text-gray-400"
              }`}
            >
              医学的検証型・教育的
            </p>
          </div>
        </div>
      </button>
    </div>
  );
};

export default ModeSelector;
