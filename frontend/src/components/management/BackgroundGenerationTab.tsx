import { Wand2 } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";

interface BackgroundGenerationTabProps {
  backgroundName: string;
  isGenerating: boolean;
  onBackgroundNameChange: (value: string) => void;
  onGenerate: () => void;
}

export const BackgroundGenerationTab = ({
  backgroundName,
  isGenerating,
  onBackgroundNameChange,
  onGenerate,
}: BackgroundGenerationTabProps) => {
  return (
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
              onChange={(e) => onBackgroundNameChange(e.target.value)}
              placeholder="例: オフィス、カフェ、図書館など"
              className="flex-1"
              onKeyPress={(e) => {
                if (e.key === "Enter" && backgroundName.trim() && !isGenerating) {
                  onGenerate();
                }
              }}
            />
            <Button
              onClick={onGenerate}
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
  );
};

