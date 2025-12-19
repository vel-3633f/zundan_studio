import { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import { useManagementStore } from "@/stores/managementStore";

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
    }
  };

  const handleDeleteFood = (foodId: number) => {
    if (confirm("この食べ物を削除しますか？")) {
      // TODO: APIを呼び出す
      removeFood(foodId);
    }
  };

  return (
    <div className="space-y-6">
      <Card title="⚙️ 管理">
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          背景画像、アイテム画像、食べ物データを管理します
        </p>

        {/* タブ */}
        <div className="flex space-x-2 mb-6 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab("backgrounds")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "backgrounds"
                ? "text-primary-600 border-b-2 border-primary-600"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            }`}
          >
            🖼️ 背景画像
          </button>
          <button
            onClick={() => setActiveTab("items")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "items"
                ? "text-primary-600 border-b-2 border-primary-600"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            }`}
          >
            🎨 アイテム画像
          </button>
          <button
            onClick={() => setActiveTab("foods")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "foods"
                ? "text-primary-600 border-b-2 border-primary-600"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            }`}
          >
            🍔 食べ物管理
          </button>
        </div>

        {/* 背景画像タブ */}
        {activeTab === "backgrounds" && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              背景画像管理
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              背景画像のアップロード機能は実装中です
            </p>
          </div>
        )}

        {/* アイテム画像タブ */}
        {activeTab === "items" && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              アイテム画像管理
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              アイテム画像のアップロード機能は実装中です
            </p>
          </div>
        )}

        {/* 食べ物管理タブ */}
        {activeTab === "foods" && (
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              食べ物管理
            </h3>

            {/* 追加フォーム */}
            <div className="flex space-x-2 mb-6">
              <Input
                value={newFoodName}
                onChange={(e) => setNewFoodName(e.target.value)}
                placeholder="食べ物名を入力"
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleAddFood();
                  }
                }}
              />
              <Button onClick={handleAddFood} disabled={!newFoodName.trim()}>
                追加
              </Button>
            </div>

            {/* 食べ物リスト */}
            {foods.length === 0 ? (
              <p className="text-gray-600 dark:text-gray-400 text-center py-8">
                登録されている食べ物はありません
              </p>
            ) : (
              <div className="space-y-2">
                {foods.map((food) => (
                  <div
                    key={food.id}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {food.name}
                      </span>
                      {food.created_at && (
                        <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                          ({new Date(food.created_at).toLocaleDateString()})
                        </span>
                      )}
                    </div>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteFood(food.id)}
                    >
                      削除
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default ManagementPage;
