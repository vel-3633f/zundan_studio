import { Laugh, Lightbulb } from "lucide-react";
import { cn } from "@/lib/utils";

interface ScriptModeSelectorProps {
  mode: "comedy" | "thought_experiment";
  onModeChange: (mode: "comedy" | "thought_experiment") => void;
  disabled?: boolean;
}

const ScriptModeSelector = ({
  mode,
  onModeChange,
  disabled = false,
}: ScriptModeSelectorProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* お笑いモードカード */}
      <button
        onClick={() => onModeChange("comedy")}
        disabled={disabled}
        className={cn(
          "p-6 rounded-lg border-2 transition-all text-left",
          mode === "comedy"
            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
            : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/10",
          disabled && "opacity-50 cursor-not-allowed",
        )}
      >
        <div className="flex flex-col items-center gap-3">
          <Laugh
            className={cn(
              "h-8 w-8",
              mode === "comedy"
                ? "text-blue-600 dark:text-blue-400"
                : "text-gray-500 dark:text-gray-400",
            )}
          />
          <div className="text-center">
            <h3
              className={cn(
                "text-lg font-bold",
                mode === "comedy"
                  ? "text-blue-900 dark:text-blue-100"
                  : "text-gray-700 dark:text-gray-300",
              )}
            >
              お笑いモード
            </h3>
            <p
              className={cn(
                "text-sm mt-1",
                mode === "comedy"
                  ? "text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-400",
              )}
            >
              バカバカしい漫談を繰り広げる
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-3">
              <span
                className={cn(
                  "inline-flex items-center px-2 py-1 rounded text-xs font-medium",
                  mode === "comedy"
                    ? "bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200"
                    : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
                )}
              >
                ユーモア重視
              </span>
              <span
                className={cn(
                  "inline-flex items-center px-2 py-1 rounded text-xs font-medium",
                  mode === "comedy"
                    ? "bg-blue-200 text-blue-800 dark:bg-blue-800 dark:text-blue-200"
                    : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
                )}
              >
                カオス展開
              </span>
            </div>
          </div>
        </div>
      </button>

      {/* 思考実験モードカード */}
      <button
        onClick={() => onModeChange("thought_experiment")}
        disabled={disabled}
        className={cn(
          "p-6 rounded-lg border-2 transition-all text-left",
          mode === "thought_experiment"
            ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
            : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-purple-400 dark:hover:border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/10",
          disabled && "opacity-50 cursor-not-allowed",
        )}
      >
        <div className="flex flex-col items-center gap-3">
          <Lightbulb
            className={cn(
              "h-8 w-8",
              mode === "thought_experiment"
                ? "text-purple-600 dark:text-purple-400"
                : "text-gray-500 dark:text-gray-400",
            )}
          />
          <div className="text-center">
            <h3
              className={cn(
                "text-lg font-bold",
                mode === "thought_experiment"
                  ? "text-purple-900 dark:text-purple-100"
                  : "text-gray-700 dark:text-gray-300",
              )}
            >
              思考実験モード
            </h3>
            <p
              className={cn(
                "text-sm mt-1",
                mode === "thought_experiment"
                  ? "text-purple-700 dark:text-purple-300"
                  : "text-gray-600 dark:text-gray-400",
              )}
            >
              「もしも系」思考実験バラエティ
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-3">
              <span
                className={cn(
                  "inline-flex items-center px-2 py-1 rounded text-xs font-medium",
                  mode === "thought_experiment"
                    ? "bg-purple-200 text-purple-800 dark:bg-purple-800 dark:text-purple-200"
                    : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
                )}
              >
                論理的分析
              </span>
              <span
                className={cn(
                  "inline-flex items-center px-2 py-1 rounded text-xs font-medium",
                  mode === "thought_experiment"
                    ? "bg-purple-200 text-purple-800 dark:bg-purple-800 dark:text-purple-200"
                    : "bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
                )}
              >
                科学的検証
              </span>
            </div>
          </div>
        </div>
      </button>
    </div>
  );
};

export default ScriptModeSelector;
