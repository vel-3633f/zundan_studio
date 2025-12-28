import { useState } from "react";
import {
  Image,
  Wand2,
} from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";
import { managementApi } from "@/api/management";

const ManagementPage = () => {
  const [activeTab, setActiveTab] = useState<"backgrounds" | "generation">(
    "backgrounds"
  );
  const [backgroundName, setBackgroundName] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const tabs = [
    { id: "backgrounds", label: "背景画像管理", icon: Image },
    { id: "generation", label: "背景生成", icon: Wand2 },
  ] as const;

  const handleGenerate = async () => {
    if (!backgroundName.trim() || isGenerating) return;

    setIsGenerating(true);
    try {
      const response = await managementApi.backgrounds.generate(backgroundName.trim());
      if (response.success) {
        toast.success(response.message || "背景画像を生成しました");
        setBackgroundName("");
      } else {
        toast.error("背景生成に失敗しました");
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || "背景生成に失敗しました";
      toast.error(errorMessage);
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          管理
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          背景画像の管理と生成を行います
        </p>
      </div>

      {/* タブナビゲーション */}
      <div className="flex flex-wrap gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200",
                activeTab === tab.id
                  ? "bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow-sm"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* 背景画像管理タブ */}
      {activeTab === "backgrounds" && (
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
      )}

      {/* 背景生成タブ */}
      {activeTab === "generation" && (
        <Card icon={<Wand2 className="h-6 w-6" />} title="背景生成">
          <div className="space-y-6">
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  AIを使用して背景画像を自動生成します。背景名を入力して生成ボタンをクリックしてください。
                </p>
              </div>
              <div className="flex gap-2">
                <Input
                  value={backgroundName}
                  onChange={(e) => setBackgroundName(e.target.value)}
                  placeholder="例: オフィス、カフェ、図書館など"
                  className="flex-1"
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && backgroundName.trim() && !isGenerating) {
                      handleGenerate();
                    }
                  }}
                />
                <Button
                  onClick={handleGenerate}
                  disabled={!backgroundName.trim() || isGenerating}
                  isLoading={isGenerating}
                  leftIcon={<Wand2 className="h-5 w-5" />}
                >
                  生成
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ManagementPage;
