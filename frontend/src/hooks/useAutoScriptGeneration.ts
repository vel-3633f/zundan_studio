import toast from "react-hot-toast";
import { scriptApi } from "@/api/scripts";
import { extractErrorMessage } from "@/utils/errorHandler";
import { playNotificationSound } from "@/utils/notificationSound";
import type { ComedyTitle, ComedyOutline, ComedyScript, YouTubeMetadata } from "@/types";

export const useAutoScriptGeneration = (
  setGenerating: (value: boolean) => void,
  setError: (error: string | null) => void,
  setStatusMessage: (message: string) => void,
  setProgress: (progress: number) => void,
  setGeneratedTitle: (title: ComedyTitle | null) => void,
  setGeneratedOutline: (outline: ComedyOutline | null) => void,
  setGeneratedScript: (script: ComedyScript | null) => void,
  setYoutubeMetadata: (metadata: YouTubeMetadata | null) => void,
  setSavedFilePath: (path: string | null) => void,
  setCurrentStep: (step: "input" | "title" | "outline" | "script") => void,
  mode: "comedy",
  inputText: string,
  model: string,
  temperature: number
) => {
  const handleAutoGenerateScript = async (themeOverride?: string) => {
    const theme = themeOverride || inputText;
    
    if (!theme.trim()) {
      toast.error("テーマを入力してください");
      return;
    }

    setGenerating(true);
    setError(null);
    setProgress(0);
    setStatusMessage("自動生成を開始しています...");
    setSavedFilePath(null);

    try {
      // 1. タイトル→アウトライン→台本を一括生成
      setStatusMessage("タイトルを生成中...");
      setProgress(0.1);

      const fullScriptResult = await scriptApi.generateFullScript({
        mode,
        input_text: theme,
        model,
        temperature,
      });

      // 中間データをストアに保存
      setGeneratedTitle(fullScriptResult.title);
      setProgress(0.4);
      setStatusMessage("アウトラインを生成中...");

      setGeneratedOutline(fullScriptResult.outline);
      setYoutubeMetadata(fullScriptResult.youtube_metadata || null);
      setProgress(0.7);
      setStatusMessage("台本を生成中...");

      setGeneratedScript(fullScriptResult.script);
      setProgress(0.9);
      setStatusMessage("台本を保存中...");

      // 2. 自動でJSON保存
      try {
        const saveResult = await scriptApi.saveScript({
          script: fullScriptResult.script,
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
      console.error("Auto generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  return {
    handleAutoGenerateScript,
  };
};
