import { useState, useEffect } from "react";
import { Wand2, FileJson } from "lucide-react";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Select from "@/components/Select";
import toast from "react-hot-toast";
import { videoApi } from "@/api/videos";
import { managementApi } from "@/api/management";
import type { JsonFileInfo } from "@/types";

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
  const [jsonFiles, setJsonFiles] = useState<JsonFileInfo[]>([]);
  const [selectedJsonFile, setSelectedJsonFile] = useState<string>("");
  const [isLoadingJsonFiles, setIsLoadingJsonFiles] = useState(false);
  const [isGeneratingFromJson, setIsGeneratingFromJson] = useState(false);

  useEffect(() => {
    const loadJsonFiles = async () => {
      try {
        setIsLoadingJsonFiles(true);
        const files = await videoApi.listJsonFiles();
        // 生成済みのファイルを除外
        const ungeneratedFiles = files.filter((file) => !file.is_generated);
        setJsonFiles(ungeneratedFiles);
        if (ungeneratedFiles.length > 0 && !selectedJsonFile) {
          setSelectedJsonFile(ungeneratedFiles[0].filename);
        }
      } catch (error) {
        console.error("JSONファイル一覧取得エラー:", error);
        toast.error("JSONファイル一覧の取得に失敗しました");
      } finally {
        setIsLoadingJsonFiles(false);
      }
    };

    loadJsonFiles();
  }, []);

  const handleGenerateFromJson = async () => {
    if (!selectedJsonFile || isGeneratingFromJson) {
      return;
    }

    setIsGeneratingFromJson(true);
    try {
      const result = await managementApi.backgrounds.generateFromJson(
        selectedJsonFile
      );
      if (result.success) {
        if (result.generated_count > 0) {
          toast.success(`${result.message} 完了です。`);
        } else {
          toast.success(result.message);
        }
      } else {
        toast.error(result.message || "背景画像の生成に失敗しました");
      }
    } catch (error: any) {
      console.error("背景画像生成エラー:", error);
      const errorMessage =
        error?.response?.data?.detail ||
        error?.message ||
        "背景画像の生成に失敗しました";
      toast.error(errorMessage);
    } finally {
      setIsGeneratingFromJson(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card icon={<Wand2 className="h-6 w-6" />} title="単一背景生成">
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
                if (
                  e.key === "Enter" &&
                  backgroundName.trim() &&
                  !isGenerating
                ) {
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
      </Card>

      <Card icon={<FileJson className="h-6 w-6" />} title="JSONから一括生成">
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              JSONファイルを読み込んで、不足している背景画像を一括生成します。
            </p>
          </div>
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <Select
                label="JSONファイルを選択"
                value={selectedJsonFile}
                onChange={(e) => setSelectedJsonFile(e.target.value)}
                disabled={isLoadingJsonFiles || jsonFiles.length === 0}
              >
                <option value="">
                  {isLoadingJsonFiles
                    ? "読み込み中..."
                    : jsonFiles.length === 0
                    ? "JSONファイルが見つかりません"
                    : "ファイルを選択してください"}
                </option>
                {jsonFiles.map((file) => (
                  <option key={file.filename} value={file.filename}>
                    {file.filename}
                  </option>
                ))}
              </Select>
            </div>
            <Button
              onClick={handleGenerateFromJson}
              disabled={!selectedJsonFile || isGeneratingFromJson}
              isLoading={isGeneratingFromJson}
              leftIcon={<FileJson className="h-5 w-5" />}
            >
              生成
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

