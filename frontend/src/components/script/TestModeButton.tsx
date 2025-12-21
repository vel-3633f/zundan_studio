import { useState } from "react";
import type { ScriptMode } from "@/types";

interface TestModeButtonProps {
  mode: ScriptMode;
  currentStep: "input" | "title" | "outline" | "script";
  disabled?: boolean;
  onLoadTestData: (step: "title" | "outline" | "script") => void;
}

const TestModeButton = ({
  mode,
  currentStep,
  disabled = false,
  onLoadTestData,
}: TestModeButtonProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const getAvailableSteps = () => {
    const steps: Array<{ key: "title" | "outline" | "script"; label: string }> =
      [];

    // 現在のステップに応じて利用可能なテストデータを表示
    if (currentStep === "input") {
      steps.push(
        { key: "title", label: "タイトル" },
        { key: "outline", label: "アウトライン" },
        { key: "script", label: "完成台本" }
      );
    } else if (currentStep === "title") {
      steps.push(
        { key: "outline", label: "アウトライン" },
        { key: "script", label: "完成台本" }
      );
    } else if (currentStep === "outline") {
      steps.push({ key: "script", label: "完成台本" });
    }

    return steps;
  };

  const availableSteps = getAvailableSteps();

  if (availableSteps.length === 0) {
    return null;
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className="px-4 py-2 text-sm font-medium text-purple-600 dark:text-purple-400 
                 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700
                 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-colors duration-200 flex items-center gap-2"
        title="テストデータを読み込んでUIを確認"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        テストモード
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* オーバーレイ */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* ドロップダウンメニュー */}
          <div
            className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 
                       border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-20
                       overflow-hidden"
          >
            <div className="px-4 py-3 bg-purple-50 dark:bg-purple-900/20 border-b border-purple-200 dark:border-purple-700">
              <p className="text-sm font-medium text-purple-900 dark:text-purple-100">
                テストデータを読み込む
              </p>
              <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
                {mode === "food" ? "食べ物モード" : "お笑いモード"}
              </p>
            </div>

            <div className="py-2">
              {availableSteps.map((step) => (
                <button
                  key={step.key}
                  onClick={() => {
                    onLoadTestData(step.key);
                    setIsOpen(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300
                           hover:bg-purple-50 dark:hover:bg-purple-900/20
                           transition-colors duration-150 flex items-center gap-2"
                >
                  <svg
                    className="w-4 h-4 text-purple-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  {step.label}まで読み込む
                </button>
              ))}
            </div>

            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                💡 LLMを実行せずにUIをテストできます
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TestModeButton;

