import { Image } from "lucide-react";
import Card from "@/components/Card";

export const BackgroundManagementTab = () => {
  return (
    <Card icon={<Image className="h-6 w-6" />} title="背景画像管理">
      <div className="text-center py-12">
        <Image className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
        <p className="text-gray-600 dark:text-gray-400 mb-2">
          背景画像のアップロード機能は実装中です
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-500">
          近日公開予定
        </p>
      </div>
    </Card>
  );
};

