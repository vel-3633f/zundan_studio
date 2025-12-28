import { useState } from "react";
import { Download, Save, Eye, EyeOff } from "lucide-react";
import toast from "react-hot-toast";
import Button from "@/components/Button";
import { scriptApi } from "@/api/scripts";
import type { ComedyScript, ScriptMode } from "@/types";

interface ScriptSectionActionsProps {
  mode: ScriptMode;
  script: ComedyScript;
}

export const ScriptSectionActions = ({
  mode,
  script,
}: ScriptSectionActionsProps) => {
  const [isSaving, setIsSaving] = useState(false);
  const [savedFilePath, setSavedFilePath] = useState<string | null>(null);
  const [showJson, setShowJson] = useState(false);

  const handleDownload = () => {
    const dataStr = JSON.stringify(script, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `script_${mode}_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleSaveToServer = async () => {
    setIsSaving(true);
    try {
      const result = await scriptApi.saveScript({
        script: script,
      });
      setSavedFilePath(result.file_path);
      toast.success(`台本を保存しました: ${result.filename}`);
    } catch (error: any) {
      console.error("Save error:", error);
      toast.error(error.response?.data?.detail || "保存に失敗しました");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <div className="space-y-3">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Button
            variant="primary"
            className="w-full"
            leftIcon={<Save className="h-5 w-5" />}
            onClick={handleSaveToServer}
            disabled={isSaving}
          >
            {isSaving ? "保存中..." : "サーバーに保存"}
          </Button>
          <Button
            variant="outline"
            className="w-full"
            leftIcon={<Download className="h-5 w-5" />}
            onClick={handleDownload}
          >
            JSONをダウンロード
          </Button>
        </div>

        {savedFilePath && (
          <div className="p-3 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
            <p className="text-sm text-success-700 dark:text-success-400">
              ✓ 保存済み: <span className="font-mono text-xs">{savedFilePath}</span>
            </p>
          </div>
        )}

        <Button
          variant="ghost"
          className="w-full"
          leftIcon={showJson ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          onClick={() => setShowJson(!showJson)}
        >
          {showJson ? "JSONを隠す" : "JSONを表示"}
        </Button>
      </div>

      {showJson && (
        <div className="mt-4">
          <div className="bg-gray-900 dark:bg-gray-950 rounded-lg p-4 overflow-auto max-h-96">
            <pre className="text-xs text-gray-100 font-mono">
              {JSON.stringify(script, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </>
  );
};

