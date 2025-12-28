import { useRef } from "react";
import { Upload } from "lucide-react";
import Button from "@/components/Button";
import Select from "@/components/Select";

interface JsonLoaderProps {
  jsonFiles: Array<{ filename: string; path: string }>;
  selectedJsonFile: string;
  isLoadingJsonFiles: boolean;
  onSelectedFileChange: (filename: string) => void;
  onLoadSelected: () => void;
  onLoadFromFile: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export const JsonLoader = ({
  jsonFiles,
  selectedJsonFile,
  isLoadingJsonFiles,
  onSelectedFileChange,
  onLoadSelected,
  onLoadFromFile,
}: JsonLoaderProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleJsonLoadClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2 items-end">
        <div className="flex-1">
          <Select
            label="JSONファイルを選択"
            value={selectedJsonFile}
            onChange={(e) => onSelectedFileChange(e.target.value)}
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
          onClick={onLoadSelected}
          variant="outline"
          disabled={!selectedJsonFile || isLoadingJsonFiles}
          leftIcon={<Upload className="h-5 w-5" />}
        >
          読み込む
        </Button>
      </div>
      <div className="text-sm text-gray-500 dark:text-gray-400">または</div>
      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={onLoadFromFile}
          className="hidden"
        />
        <Button
          onClick={handleJsonLoadClick}
          variant="outline"
          leftIcon={<Upload className="h-5 w-5" />}
        >
          ファイルから読み込む
        </Button>
      </div>
    </div>
  );
};

