import { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  icon?: ReactNode;
  headerAction?: ReactNode;
  children: React.ReactNode;
  hover?: boolean;
}

const Card: React.FC<CardProps> = ({
  title,
  icon,
  headerAction,
  children,
  className,
  hover = false,
  ...props
}) => {
  return (
    <div
      className={cn(
        "bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-100 dark:border-gray-700 p-6 transition-all duration-200",
        hover && "hover:shadow-lg hover:-translate-y-0.5",
        className
      )}
      {...props}
    >
      {(title || icon || headerAction) && (
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="flex-shrink-0 text-primary-600 dark:text-primary-400">
                {icon}
              </div>
            )}
            {title && (
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
            )}
          </div>
          {headerAction && <div className="flex-shrink-0">{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
