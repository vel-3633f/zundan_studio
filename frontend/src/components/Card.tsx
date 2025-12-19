import { HTMLAttributes } from "react";
import { clsx } from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  children: React.ReactNode;
}

const Card: React.FC<CardProps> = ({
  title,
  children,
  className,
  ...props
}) => {
  return (
    <div
      className={clsx(
        "bg-white dark:bg-gray-800 rounded-lg shadow-md p-6",
        className
      )}
      {...props}
    >
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export default Card;
