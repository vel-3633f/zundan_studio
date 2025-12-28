import { CheckCircle } from "lucide-react";
import Card from "@/components/Card";
import Badge from "@/components/Badge";
import type { ComedyScript, ScriptMode } from "@/types";
import { ScriptSectionInfo } from "./ScriptSectionInfo";
import { ScriptSectionActions } from "./ScriptSectionActions";

interface ScriptSectionProps {
  mode: ScriptMode;
  script: ComedyScript;
}

const ScriptSection = ({ mode, script }: ScriptSectionProps) => {

  return (
    <Card
      icon={<CheckCircle className="h-6 w-6" />}
      title="台本生成完了！"
      headerAction={<Badge variant="success">完了</Badge>}
      className="animate-fade-in"
    >
      <div className="space-y-6">
        <ScriptSectionInfo script={script} />
        <ScriptSectionActions mode={mode} script={script} />
      </div>
    </Card>
  );
};

export default ScriptSection;
