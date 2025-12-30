import { Sparkles, Shuffle, Edit3 } from "lucide-react";
import { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Textarea from "@/components/Textarea";

interface ThemeSelectionSectionProps {
  themes: string[];
  selectedTheme: string | null;
  isGenerating: boolean;
  onThemeSelect: (theme: string) => void;
  onGenerateThemes: () => void;
  onCustomThemeSubmit?: (theme: string) => void;
}

const ThemeSelectionSection = ({
  themes,
  selectedTheme,
  isGenerating,
  onThemeSelect,
  onGenerateThemes,
  onCustomThemeSubmit,
}: ThemeSelectionSectionProps) => {
  const [activeTab, setActiveTab] = useState<"auto" | "custom">("auto");
  const [customTheme, setCustomTheme] = useState("");

  const handleCustomSubmit = () => {
    if (customTheme.trim() && onCustomThemeSubmit) {
      onCustomThemeSubmit(customTheme.trim());
    }
  };

  return (
    <Card
      icon={<Sparkles className="h-6 w-6" />}
      title="テーマを選択"
    >
      <div className="space-y-4">
        {/* タブ切り替え */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab("auto")}
            disabled={isGenerating}
            className={`
              px-4 py-2 font-medium text-sm transition-colors
              border-b-2 -mb-px
              ${
                activeTab === "auto"
                  ? "border-primary-600 text-primary-600 dark:text-primary-400"
                  : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              }
              ${isGenerating ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
            `}
          >
            <div className="flex items-center gap-2">
              <Shuffle className="h-4 w-4" />
              自動生成
            </div>
          </button>
          <button
            onClick={() => setActiveTab("custom")}
            disabled={isGenerating}
            className={`
              px-4 py-2 font-medium text-sm transition-colors
              border-b-2 -mb-px
              ${
                activeTab === "custom"
                  ? "border-primary-600 text-primary-600 dark:text-primary-400"
                  : "border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              }
              ${isGenerating ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
            `}
          >
            <div className="flex items-center gap-2">
              <Edit3 className="h-4 w-4" />
              自由入力
            </div>
          </button>
        </div>

        {/* 自動生成タブ */}
        {activeTab === "auto" && (
          <div className="space-y-4 pt-2">
            <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-700">
              <p className="text-sm text-primary-900 dark:text-primary-100">
                🎯 テーマを選択すると、そのテーマに基づいたタイトルが生成されます。
                <br />
                気に入ったテーマをクリックしてください！
              </p>
            </div>

            <Button
              onClick={onGenerateThemes}
              disabled={isGenerating}
              isLoading={isGenerating}
              className="w-full"
              leftIcon={<Shuffle className="h-5 w-5" />}
            >
              🎲 テーマを自動生成
            </Button>

            {themes.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  テーマ候補 ({themes.length}個)
                </p>
                <div className="flex flex-wrap gap-2">
                  {themes.map((theme, index) => (
                    <button
                      key={index}
                      onClick={() => onThemeSelect(theme)}
                      disabled={isGenerating}
                      className={`
                        px-4 py-2 rounded-lg font-medium transition-all
                        ${
                          selectedTheme === theme
                            ? "bg-primary-600 text-white shadow-md scale-105"
                            : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-primary-100 dark:hover:bg-primary-900/30 hover:scale-105"
                        }
                        ${isGenerating ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
                      `}
                    >
                      {theme}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 自由入力タブ */}
        {activeTab === "custom" && (
          <div className="space-y-4 pt-2">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
              <p className="text-sm text-blue-900 dark:text-blue-100">
                ✍️ お好みのテーマを自由に入力してください。
                <br />
                例：「調味料の取り違え」「電車でのマナー」「早起きのコツ」など
              </p>
            </div>

            <Textarea
              label="テーマを入力"
              placeholder="テーマを入力してください（例：調味料の取り違え）"
              value={customTheme}
              onChange={(e) => setCustomTheme(e.target.value)}
              disabled={isGenerating}
              helperText="1語程度の短い単語やフレーズを入力してください"
              className="min-h-[100px]"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  handleCustomSubmit();
                }
              }}
            />

            <Button
              onClick={handleCustomSubmit}
              disabled={isGenerating || !customTheme.trim()}
              isLoading={isGenerating}
              className="w-full"
              leftIcon={<Edit3 className="h-5 w-5" />}
            >
              このテーマでタイトルを生成
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ThemeSelectionSection;

