import {
  Sparkles,
  Settings as SettingsIcon,
  ChevronDown,
  ChevronUp,
  Shuffle,
} from "lucide-react";
import { useState } from "react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Select from "@/components/Select";
import ThemeSelectionSection from "./ThemeSelectionSection";
import type { ScriptMode } from "@/types";
import { useScriptStore } from "@/stores/scriptStore";

interface InputSectionProps {
  mode: ScriptMode;
  inputText: string;
  model: string;
  temperature: number;
  isGenerating: boolean;
  onInputTextChange: (text: string) => void;
  onModelChange: (model: string) => void;
  onTemperatureChange: (temp: number) => void;
  onSubmit: () => void;
  onRandomGenerate?: () => void; // お笑いモード専用
  // テーマ選択関連（お笑いモード専用）
  themes?: string[];
  selectedTheme?: string | null;
  onGenerateThemes?: () => void;
  onThemeSelect?: (theme: string) => void;
  onCustomThemeSubmit?: (theme: string) => void;
}

const InputSection = ({
  mode,
  inputText,
  model,
  temperature,
  isGenerating,
  onInputTextChange,
  onModelChange,
  onTemperatureChange,
  onSubmit,
  onRandomGenerate,
  themes = [],
  selectedTheme = null,
  onGenerateThemes,
  onThemeSelect,
  onCustomThemeSubmit,
}: InputSectionProps) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { availableModels } = useScriptStore();

  // お笑いモードでテーマ選択機能が有効な場合
  if (mode === "comedy" && onGenerateThemes && onThemeSelect) {
    return (
      <ThemeSelectionSection
        themes={themes}
        selectedTheme={selectedTheme}
        isGenerating={isGenerating}
        onThemeSelect={onThemeSelect}
        onGenerateThemes={onGenerateThemes}
        onCustomThemeSubmit={onCustomThemeSubmit}
      />
    );
  }

  return (
    <Card icon={<Sparkles className="h-6 w-6" />} title="漫談タイトル生成">
      <div className="space-y-6">
        {/* テーマ入力（ランダム生成がない場合のみ表示） */}
        {!onRandomGenerate && (
          <div>
            <Input
              label="テーマ"
              value={inputText}
              onChange={(e) => onInputTextChange(e.target.value)}
              placeholder="例: コンビニの店員、面接官、上司"
              disabled={isGenerating}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              テーマを入力すると、そのテーマに関連したタイトル候補を20個生成します
            </p>
          </div>
        )}

        {/* 説明文（ランダム生成がある場合のみ表示） */}
        {onRandomGenerate && (
          <div className="p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-700">
            <p className="text-sm text-primary-900 dark:text-primary-100">
              🎲 AIがランダムにバカバカしいタイトルを20-30個生成します。
              <br />
              5つのお笑いフックパターン別に表示されるので、気に入ったタイトルを選んで漫談台本を作成しましょう！
            </p>
          </div>
        )}

        {/* 詳細設定 */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
          >
            <div className="flex items-center gap-2">
              <SettingsIcon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                詳細設定
              </span>
            </div>
            {showAdvanced ? (
              <ChevronUp className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-600 dark:text-gray-400" />
            )}
          </button>

          {showAdvanced && (
            <div className="p-4 space-y-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 animate-fade-in">
              <Select
                label="AIモデル"
                value={model}
                onChange={(e) => onModelChange(e.target.value)}
              >
                {availableModels.length > 0 ? (
                  availableModels.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} {m.recommended ? "(推奨)" : ""}
                    </option>
                  ))
                ) : (
                  <option value="">読み込み中...</option>
                )}
              </Select>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  創造性レベル: {temperature.toFixed(1)}
                  {temperature < 0.8 && (
                    <span className="ml-2 text-xs text-warning-600 dark:text-warning-400">
                      （0.8以上推奨）
                    </span>
                  )}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={temperature}
                  onChange={(e) =>
                    onTemperatureChange(parseFloat(e.target.value))
                  }
                  className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  高いほどバカバカしく予測不可能な展開になります
                </p>
              </div>
            </div>
          )}
        </div>

        {/* 生成ボタン */}
        {onRandomGenerate ? (
          <Button
            onClick={onRandomGenerate}
            disabled={isGenerating}
            isLoading={isGenerating}
            className="w-full"
            leftIcon={<Shuffle className="h-5 w-5" />}
          >
            🎲 ランダムタイトルを生成
          </Button>
        ) : (
          <Button
            onClick={onSubmit}
            disabled={!inputText.trim() || isGenerating}
            isLoading={isGenerating}
            className="w-full"
            leftIcon={<Sparkles className="h-5 w-5" />}
          >
            タイトルを生成
          </Button>
        )}
      </div>
    </Card>
  );
};

export default InputSection;
