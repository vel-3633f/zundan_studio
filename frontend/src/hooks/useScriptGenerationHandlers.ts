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
  setSavedFilePath: (path: string | null) => void,
  mode: "comedy" | "thought_experiment",
  generatedTitle: ComedyTitle | null,
  generatedOutline: ComedyOutline | null,
  referenceInfo: string,
  model: string,
  temperature: number,
  isAutoMode: boolean
) => {
  const handleGenerateOutline = async () => {
    if (!generatedTitle) {
      toast.error("タイトルが生成されていません");
      return;
    }

    setGenerating(true);
    setGeneratingAction("approve");
    setError(null);
    setProgress(0);
    setStatusMessage("アウトラインを生成中...");

    try {
      // 1. アウトライン生成
      setProgress(0.2);
      const result = await scriptApi.generateOutline({
        mode,
        title_data: generatedTitle,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedOutline(result.outline);
      setYoutubeMetadata(result.youtube_metadata || null);
      setProgress(0.5);

      if (isAutoMode) {
        // 自動モード：台本→保存を自動実行
        setStatusMessage("台本を生成中...");
        
        // 2. 台本生成
        const scriptResult = await scriptApi.generateScript({
          mode,
          outline_data: result.outline,
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
      } else {
        // 手動モード：アウトライン確認画面へ
        setCurrentStep("outline");
        toast.success("アウトラインを生成しました！");
        playNotificationSound();
      }
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "生成に失敗しました");
      setError(errorMsg);
      console.error("Generation error:", err);
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
      setProgress(0.8);

      if (isAutoMode) {
        // 自動モード：保存まで自動実行
        setStatusMessage("台本を保存中...");
        
        try {
          const saveResult = await scriptApi.saveScript({
            script: result.script,
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
      } else {
        // 手動モード：台本確認画面へ
        setCurrentStep("script");
        setProgress(1);
        setStatusMessage("完了！");
        toast.success("台本を生成しました！");
        playNotificationSound();
      }
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

