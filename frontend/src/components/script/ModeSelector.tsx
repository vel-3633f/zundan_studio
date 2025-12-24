import { Laugh } from "lucide-react";

const ModeSelector = () => {
  return (
    <div className="flex justify-center">
      <div className="p-6 rounded-lg border-2 border-primary-500 bg-primary-50 dark:bg-primary-900/20 max-w-md">
        <div className="flex flex-col items-center gap-3">
          <Laugh className="h-8 w-8 text-primary-600 dark:text-primary-400" />
          <div className="text-center">
            <h3 className="text-lg font-bold text-primary-900 dark:text-primary-100">
              😂 お笑い漫談モード
            </h3>
            <p className="text-sm mt-1 text-primary-700 dark:text-primary-300">
              バカバカしい漫談・教訓なし
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModeSelector;
