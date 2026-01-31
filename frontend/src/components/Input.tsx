import { InputHTMLAttributes, forwardRef, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  leftAddon?: string;
  rightAddon?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      leftIcon,
      rightIcon,
      leftAddon,
      rightAddon,
      ...props
    },
    ref
  ) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {leftAddon && (
            <span className="absolute left-0 top-0 bottom-0 px-3 flex items-center text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border border-r-0 border-gray-300 dark:border-gray-600 rounded-l-lg">
              {leftAddon}
            </span>
          )}
          {leftIcon && !leftAddon && (
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
              {leftIcon}
            </span>
          )}
          <input
            ref={ref}
            className={cn(
              "w-full px-4 py-2.5 border rounded-lg transition-all duration-200",
              "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
              "disabled:bg-gray-50 disabled:cursor-not-allowed disabled:text-gray-500 dark:disabled:bg-gray-800",
              "placeholder:text-gray-400 dark:placeholder:text-gray-500",
              error
                ? "border-error-500 focus:ring-error-500 dark:border-error-400"
                : "border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500",
              "bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              leftIcon && !leftAddon && "pl-10",
              rightIcon && !rightAddon && "pr-10",
              leftAddon && "pl-20 rounded-l-none",
              rightAddon && "pr-20 rounded-r-none",
              className
            )}
            {...props}
          />
          {rightIcon && !rightAddon && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
              {rightIcon}
            </span>
          )}
          {rightAddon && (
            <span className="absolute right-0 top-0 bottom-0 px-3 flex items-center text-sm text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border border-l-0 border-gray-300 dark:border-gray-600 rounded-r-lg">
              {rightAddon}
            </span>
          )}
        </div>
        {error && (
          <p className="mt-1.5 text-sm text-error-600 dark:text-error-400 animate-fade-in">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
