import { CheckCircle, Save } from "lucide-react";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import type { ComedyScript, ScriptMode } from "@/types";
import { ScriptSectionInfo } from "./ScriptSectionInfo";
import { ScriptSectionActions } from "./ScriptSectionActions";

interface ScriptSectionProps {
  mode: ScriptMode;
  script: ComedyScript;
  savedFilePath?: string | null;
  isAutoMode?: boolean;
}

const ScriptSection = ({ mode, script, savedFilePath, isAutoMode }: ScriptSectionProps) => {

  return (
    <Card
      icon={<CheckCircle className="h-6 w-6" />}
      title="台本生成完了！"
      headerAction={<Badge variant="success">完了</Badge>}
      className="animate-fade-in"
    >
      <div className="space-y-6">
        {/* 自動保存バナー */}
        {isAutoMode && savedFilePath && (
          <div className="p-4 bg-success-50 dark:bg-success-900/20 rounded-lg border border-success-200 dark:border-success-800">
            <div className="flex items-start gap-3">
              <Save className="h-5 w-5 text-success-600 dark:text-success-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="text-sm font-medium text-success-900 dark:text-success-100 mb-1">
                  自動保存しました
                </div>
                <div className="text-xs text-success-700 dark:text-success-300 font-mono break-all">
                  {savedFilePath}
                </div>
              </div>
            </div>
          </div>
        )}

        <ScriptSectionInfo script={script} />
        <ScriptSectionActions mode={mode} script={script} />
      </div>
    </Card>
  );
};

export default ScriptSection;
