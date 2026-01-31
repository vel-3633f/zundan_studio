import { cn } from "@/lib/utils";

interface ProgressBarProps {
  progress: number; // 0-100
  message?: string;
  showPercentage?: boolean;
  className?: string;
  variant?: "default" | "success" | "warning" | "error";
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  message,
  showPercentage = true,
  className,
  variant = "default",
}) => {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  const variantClasses = {
    default: "bg-gradient-to-r from-primary-500 to-primary-600",
    success: "bg-gradient-to-r from-success-500 to-success-600",
    warning: "bg-gradient-to-r from-warning-500 to-warning-600",
    error: "bg-gradient-to-r from-error-500 to-error-600",
  };

  return (
    <div className={cn("w-full", className)}>
      {message && (
        <div className="mb-3 flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {message}
          </span>
          {showPercentage && (
            <span className="text-sm font-semibold text-primary-600 dark:text-primary-400">
              {Math.round(clampedProgress)}%
            </span>
          )}
        </div>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden shadow-inner">
        <div
          className={cn(
            "h-full transition-all duration-500 ease-out flex items-center justify-center relative",
            variantClasses[variant]
          )}
          style={{ width: `${clampedProgress}%` }}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </div>
      </div>
      {!message && showPercentage && (
        <div className="mt-2 text-xs text-gray-600 dark:text-gray-400 text-right font-medium">
          {Math.round(clampedProgress)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
