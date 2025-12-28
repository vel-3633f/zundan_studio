import { useState } from "react";
import { Image, Wand2 } from "lucide-react";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";
import { managementApi } from "@/api/management";
import { BackgroundManagementTab } from "@/components/management/BackgroundManagementTab";
import { BackgroundGenerationTab } from "@/components/management/BackgroundGenerationTab";

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
      const response = await managementApi.backgrounds.generate(
        backgroundName.trim()
      );
      if (response.success) {
        toast.success(response.message || "背景画像を生成しました");
        setBackgroundName("");
      } else {
        toast.error("背景生成に失敗しました");
      }
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        "背景生成に失敗しました";
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

      {activeTab === "backgrounds" && <BackgroundManagementTab />}

      {activeTab === "generation" && (
        <BackgroundGenerationTab
          backgroundName={backgroundName}
          isGenerating={isGenerating}
          onBackgroundNameChange={setBackgroundName}
          onGenerate={handleGenerate}
        />
      )}
    </div>
  );
};

export default ManagementPage;
