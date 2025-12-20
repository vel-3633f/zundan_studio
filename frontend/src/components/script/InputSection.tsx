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
}: InputSectionProps) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { availableModels } = useScriptStore();

  return (
    <Card
      icon={<Sparkles className="h-6 w-6" />}
      title={mode === "food" ? "食べ物設定" : "漫談テーマ設定"}
    >
      <div className="space-y-6">
        {/* 入力フィールド */}
        {mode === "food" ? (
          <Input
            label="調べたい食べ物"
            value={inputText}
            onChange={(e) => onInputTextChange(e.target.value)}
            placeholder="例: チョコレート"
            helperText="一般的な食べ物や飲み物の名前を入力してください"
            leftIcon={<Sparkles className="h-5 w-5" />}
          />
        ) : (
          <Input
            label="漫談のテーマ"
            value={inputText}
            onChange={(e) => onInputTextChange(e.target.value)}
            placeholder="例: 猫、ラーメン、月曜日"
            helperText="何でもOK！バカバカしいテーマほど面白い"
            leftIcon={<Sparkles className="h-5 w-5" />}
          />
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
                  {mode === "comedy" && temperature < 0.8 && (
                    <span className="ml-2 text-xs text-warning-600 dark:text-warning-400">
                      （お笑いモードは0.8以上推奨）
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
                  {mode === "food"
                    ? "高いほど創造的ですが、一貫性が下がる可能性があります"
                    : "高いほどバカバカしく予測不可能な展開になります"}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* お笑いモード: ランダム生成ボタン */}
        {mode === "comedy" && onRandomGenerate && (
          <Button
            onClick={onRandomGenerate}
            disabled={isGenerating}
            isLoading={isGenerating}
            className="w-full"
            variant="secondary"
            leftIcon={<Shuffle className="h-5 w-5" />}
          >
            🎲 ランダムタイトルを5-10個生成（テーマ不要）
          </Button>
        )}

        {/* 通常の生成ボタン */}
        <Button
          onClick={onSubmit}
          disabled={!inputText.trim() || isGenerating}
          isLoading={isGenerating}
          className="w-full"
          leftIcon={<Sparkles className="h-5 w-5" />}
        >
          {mode === "food" ? "タイトルを生成" : "テーマからタイトルを生成"}
        </Button>
      </div>
    </Card>
  );
};

export default InputSection;
