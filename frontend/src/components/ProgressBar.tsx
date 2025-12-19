import { clsx } from "clsx";

interface ProgressBarProps {
  progress: number; // 0-100
  message?: string;
  showPercentage?: boolean;
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  message,
  showPercentage = true,
  className,
}) => {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  return (
    <div className={clsx("w-full", className)}>
      {message && (
        <div className="mb-2 text-sm text-gray-700 dark:text-gray-300">
          {message}
        </div>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 overflow-hidden">
        <div
          className="bg-primary-600 h-full transition-all duration-300 ease-out flex items-center justify-center"
          style={{ width: `${clampedProgress}%` }}
        >
          {showPercentage && clampedProgress > 10 && (
            <span className="text-xs font-medium text-white">
              {Math.round(clampedProgress)}%
            </span>
          )}
        </div>
      </div>
      {showPercentage && clampedProgress <= 10 && (
        <div className="mt-1 text-xs text-gray-600 dark:text-gray-400 text-right">
          {Math.round(clampedProgress)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
