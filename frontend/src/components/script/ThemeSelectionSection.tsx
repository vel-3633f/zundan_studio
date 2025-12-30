import { Sparkles, Shuffle } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";

interface ThemeSelectionSectionProps {
  themes: string[];
  selectedTheme: string | null;
  isGenerating: boolean;
  onThemeSelect: (theme: string) => void;
  onGenerateThemes: () => void;
}

const ThemeSelectionSection = ({
  themes,
  selectedTheme,
  isGenerating,
  onThemeSelect,
  onGenerateThemes,
}: ThemeSelectionSectionProps) => {
  return (
    <Card
      icon={<Sparkles className="h-6 w-6" />}
      title="テーマを選択"
    >
      <div className="space-y-4">
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
    </Card>
  );
};

export default ThemeSelectionSection;

