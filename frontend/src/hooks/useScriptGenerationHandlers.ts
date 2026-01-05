import toast from "react-hot-toast";
import { scriptApi } from "@/api/scripts";
import { extractErrorMessage } from "@/utils/errorHandler";
import { playNotificationSound } from "@/utils/notificationSound";
import type { ComedyTitle, ComedyOutline, YouTubeMetadata } from "@/types";

export const useScriptGenerationHandlers = (
  setGenerating: (value: boolean) => void,
  setError: (error: string | null) => void,
  setStatusMessage: (message: string) => void,
  setProgress: (progress: number) => void,
  setGeneratedOutline: (outline: ComedyOutline | null) => void,
  setGeneratedScript: (script: any) => void,
  setCurrentStep: (step: "input" | "title" | "outline" | "script") => void,
  setGeneratingAction: (action: "approve" | "regenerate" | null) => void,
  setYoutubeMetadata: (metadata: YouTubeMetadata | null) => void,
  mode: "comedy",
  generatedTitle: ComedyTitle | null,
  generatedOutline: ComedyOutline | null,
  referenceInfo: string,
  model: string,
  temperature: number
) => {
  const handleGenerateOutline = async () => {
    if (!generatedTitle) {
      toast.error("タイトルが生成されていません");
      return;
    }

    setGenerating(true);
    setGeneratingAction("approve");
    setError(null);
    setStatusMessage("アウトラインを生成中...");

    try {
      const result = await scriptApi.generateOutline({
        mode,
        title_data: generatedTitle,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedOutline(result.outline);
      setYoutubeMetadata(result.youtube_metadata || null);
      setCurrentStep("outline");
      toast.success("アウトラインを生成しました！");
      playNotificationSound();
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "アウトライン生成に失敗しました");
      setError(errorMsg);
      console.error("Outline generation error:", err);
    } finally {
      setGenerating(false);
      setGeneratingAction(null);
    }
  };

  const handleGenerateScript = async () => {
    if (!generatedOutline) {
      toast.error("アウトラインが生成されていません");
      return;
    }

    setGenerating(true);
    setGeneratingAction("approve");
    setError(null);
    setProgress(0);
    setStatusMessage("台本を生成中...");

    try {
      const result = await scriptApi.generateScript({
        mode,
        outline_data: generatedOutline,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedScript(result.script);
      setCurrentStep("script");
      setProgress(1);
      setStatusMessage("完了！");
      toast.success("台本を生成しました！");
      playNotificationSound();
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "台本生成に失敗しました");
      setError(errorMsg);
      console.error("Script generation error:", err);
    } finally {
      setGenerating(false);
      setGeneratingAction(null);
    }
  };

  return {
    handleGenerateOutline,
    handleGenerateScript,
  };
};

