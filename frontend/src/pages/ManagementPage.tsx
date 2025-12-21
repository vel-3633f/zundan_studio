import { useState } from "react";
import toast from "react-hot-toast";
import {
  Image,
  Palette,
  UtensilsCrossed,
  Plus,
  Trash2,
  Calendar,
} from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Badge from "@/components/Badge";
import IconButton from "@/components/IconButton";
import { useManagementStore } from "@/stores/managementStore";
import { cn } from "@/lib/utils";

const ManagementPage = () => {
  const [activeTab, setActiveTab] = useState<"backgrounds" | "items" | "foods">(
    "foods"
  );
  const [newFoodName, setNewFoodName] = useState("");

  const { foods, addFood, removeFood } = useManagementStore();

  const handleAddFood = () => {
    if (newFoodName.trim()) {
      // TODO: APIを呼び出す
      addFood({
        id: Date.now(),
        name: newFoodName.trim(),
        created_at: new Date().toISOString(),
      });
      setNewFoodName("");
      toast.success("食べ物を追加しました");
    }
  };

  const handleDeleteFood = (foodId: number, foodName: string) => {
    // TODO: APIを呼び出す
    removeFood(foodId);
    toast.success(`${foodName}を削除しました`);
  };

  const tabs = [
    { id: "backgrounds", label: "背景画像", icon: Image },
    { id: "items", label: "アイテム画像", icon: Palette },
    { id: "foods", label: "食べ物管理", icon: UtensilsCrossed },
  ] as const;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          管理
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          背景画像、アイテム画像、食べ物データを管理します
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

      {/* 背景画像タブ */}
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

      {/* アイテム画像タブ */}
      {activeTab === "items" && (
        <Card icon={<Palette className="h-6 w-6" />} title="アイテム画像管理">
          <div className="text-center py-12">
            <Palette className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              アイテム画像のアップロード機能は実装中です
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              近日公開予定
            </p>
          </div>
        </Card>
      )}

      {/* 食べ物管理タブ */}
      {activeTab === "foods" && (
        <Card
          icon={<UtensilsCrossed className="h-6 w-6" />}
          title="食べ物管理"
          headerAction={<Badge variant="info">{foods.length}件</Badge>}
        >
          <div className="space-y-6">
            {/* 追加フォーム */}
            <div className="flex gap-2">
              <Input
                value={newFoodName}
                onChange={(e) => setNewFoodName(e.target.value)}
                placeholder="食べ物名を入力"
                className="flex-1"
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleAddFood();
                  }
                }}
              />
              <Button
                onClick={handleAddFood}
                disabled={!newFoodName.trim()}
                leftIcon={<Plus className="h-5 w-5" />}
              >
                追加
              </Button>
            </div>

            {/* 食べ物リスト */}
            {foods.length === 0 ? (
              <div className="text-center py-12">
                <UtensilsCrossed className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400 mb-2">
                  登録されている食べ物はありません
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  上のフォームから食べ物を追加してください
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {foods.map((food) => (
                  <div
                    key={food.id}
                    className="group p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 dark:text-white truncate mb-1">
                          {food.name}
                        </p>
                        {food.created_at && (
                          <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                            <Calendar className="h-3 w-3" />
                            <span>
                              {new Date(food.created_at).toLocaleDateString(
                                "ja-JP"
                              )}
                            </span>
                          </div>
                        )}
                      </div>
                      <IconButton
                        icon={<Trash2 className="h-4 w-4" />}
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteFood(food.id, food.name)}
                        aria-label="削除"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default ManagementPage;
