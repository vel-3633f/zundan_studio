import toast from "react-hot-toast";
import { scriptApi } from "@/api/scripts";
import { extractErrorMessage } from "@/utils/errorHandler";
import { playNotificationSound } from "@/utils/notificationSound";
import type { ComedyTitle, ComedyOutline, ComedyScript, YouTubeMetadata } from "@/types";

export const useAutoFromTitleGeneration = (
  setGenerating: (value: boolean) => void,
  setError: (error: string | null) => void,
  setStatusMessage: (message: string) => void,
  setProgress: (progress: number) => void,
  setGeneratedOutline: (outline: ComedyOutline | null) => void,
  setGeneratedScript: (script: ComedyScript | null) => void,
  setYoutubeMetadata: (metadata: YouTubeMetadata | null) => void,
  setSavedFilePath: (path: string | null) => void,
  setCurrentStep: (step: "input" | "title" | "outline" | "script") => void,
  mode: "comedy",
  model: string,
  temperature: number
) => {
  const handleAutoGenerateFromTitle = async (title: ComedyTitle, referenceInfo: string = "") => {
    setGenerating(true);
    setError(null);
    setProgress(0);
    setStatusMessage("アウトラインを生成中...");
    setSavedFilePath(null);

    try {
      // 1. アウトライン生成
      setProgress(0.2);
      const outlineResult = await scriptApi.generateOutline({
        mode,
        title_data: title,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedOutline(outlineResult.outline);
      setYoutubeMetadata(outlineResult.youtube_metadata || null);
      setProgress(0.5);
      setStatusMessage("台本を生成中...");

      // 2. 台本生成
      const scriptResult = await scriptApi.generateScript({
        mode,
        outline_data: outlineResult.outline,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedScript(scriptResult.script);
      setProgress(0.8);
      setStatusMessage("台本を保存中...");

      // 3. 自動でJSON保存
      try {
        const saveResult = await scriptApi.saveScript({
          script: scriptResult.script,
        });

        setSavedFilePath(saveResult.file_path);
        setProgress(1.0);
        setStatusMessage("完了！");
        setCurrentStep("script");

        toast.success(
          `台本を生成し、自動保存しました！\n${saveResult.filename}`,
          { duration: 5000 }
        );
        playNotificationSound();
      } catch (saveErr: any) {
        // 保存失敗しても台本生成は成功しているので、警告のみ
        const saveErrorMsg = extractErrorMessage(saveErr);
        console.error("Script save error:", saveErr);
        toast.error(`台本は生成されましたが、保存に失敗しました: ${saveErrorMsg}`, {
          duration: 5000,
        });

        setProgress(1.0);
        setStatusMessage("台本生成完了（保存失敗）");
        setCurrentStep("script");
        playNotificationSound();
      }
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "自動生成に失敗しました");
      setError(errorMsg);
      console.error("Auto generation from title error:", err);
    } finally {
      setGenerating(false);
    }
  };

  return {
    handleAutoGenerateFromTitle,
  };
};
