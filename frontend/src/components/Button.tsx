import { ButtonHTMLAttributes, forwardRef, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      isLoading,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseClasses =
      "inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none";

    const variantClasses = {
      primary:
        "bg-primary-600 text-white hover:bg-primary-700 hover:shadow-md active:scale-[0.98] focus:ring-primary-500 dark:bg-primary-500 dark:hover:bg-primary-600",
      secondary:
        "bg-gray-100 text-gray-900 hover:bg-gray-200 hover:shadow-sm active:scale-[0.98] focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600",
      danger:
        "bg-error-600 text-white hover:bg-error-700 hover:shadow-md active:scale-[0.98] focus:ring-error-500 dark:bg-error-500 dark:hover:bg-error-600",
      ghost:
        "bg-transparent hover:bg-gray-100 text-gray-700 active:scale-[0.98] focus:ring-gray-500 dark:hover:bg-gray-800 dark:text-gray-300",
      outline:
        "border-2 border-primary-600 text-primary-600 hover:bg-primary-50 active:scale-[0.98] focus:ring-primary-500 dark:border-primary-400 dark:text-primary-400 dark:hover:bg-primary-950",
    };

    const sizeClasses = {
      sm: "px-3 py-1.5 text-sm h-8",
      md: "px-4 py-2 text-base h-10",
      lg: "px-6 py-3 text-lg h-12",
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          leftIcon && <span className="flex-shrink-0">{leftIcon}</span>
        )}
        {children}
        {!isLoading && rightIcon && (
          <span className="flex-shrink-0">{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
