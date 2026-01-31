import { Check } from "lucide-react";
import type { ScriptStep } from "@/stores/scriptStore";

interface StepIndicatorProps {
  currentStep: ScriptStep;
  mode?: "long" | "short"; // 長尺動画(4ステップ)かショート動画(2ステップ)か
}

const longSteps = [
  { key: "input" as ScriptStep, label: "入力", number: 1 },
  { key: "title" as ScriptStep, label: "タイトル", number: 2 },
  { key: "outline" as ScriptStep, label: "アウトライン", number: 3 },
  { key: "script" as ScriptStep, label: "台本", number: 4 },
];

const shortSteps = [
  { key: "input" as ScriptStep, label: "入力", number: 1 },
  { key: "title" as ScriptStep, label: "タイトル", number: 2 },
  { key: "script" as ScriptStep, label: "台本", number: 3 },
];

const StepIndicator = ({ currentStep, mode = "long" }: StepIndicatorProps) => {
  const steps = mode === "short" ? shortSteps : longSteps;
  const currentIndex = steps.findIndex((s) => s.key === currentStep);

  return (
    <div className="w-full py-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <div key={step.key} className="flex items-center flex-1">
              {/* ステップ */}
              <div className="flex flex-col items-center">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                    transition-all
                    ${
                      isCompleted
                        ? "bg-success-500 text-white"
                        : isCurrent
                        ? "bg-primary-500 text-white ring-4 ring-primary-100 dark:ring-primary-900"
                        : "bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500"
                    }
                  `}
                >
                  {isCompleted ? <Check className="h-5 w-5" /> : step.number}
                </div>
                <span
                  className={`
                    mt-2 text-sm font-medium
                    ${
                      isCurrent
                        ? "text-primary-700 dark:text-primary-300"
                        : isCompleted
                        ? "text-success-700 dark:text-success-300"
                        : "text-gray-400 dark:text-gray-500"
                    }
                  `}
                >
                  {step.label}
                </span>
              </div>

              {/* 接続線 */}
              {index < steps.length - 1 && (
                <div
                  className={`
                    flex-1 h-0.5 mx-4
                    transition-all
                    ${
                      index < currentIndex
                        ? "bg-success-500"
                        : "bg-gray-200 dark:bg-gray-700"
                    }
                  `}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StepIndicator;
