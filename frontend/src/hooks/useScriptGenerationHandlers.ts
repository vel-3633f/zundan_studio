import { useState } from "react";
import toast from "react-hot-toast";
import { scriptApi } from "@/api/scripts";
import { extractErrorMessage } from "@/utils/errorHandler";
import { playNotificationSound } from "@/utils/notificationSound";
import { useSSEProgress } from "./useSSEProgress";
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
  const [scriptTaskId, setScriptTaskId] = useState<string | null>(null);

  // SSE進捗監視（台本生成用）
  useSSEProgress({
    taskId: scriptTaskId,
    onProgress: (progress, message) => {
      setProgress(progress);
      setStatusMessage(message);
    },
    onComplete: async (result) => {
      try {
        setGeneratedScript(result.script);
        
        if (isAutoMode) {
          // 自動モード：保存まで自動実行
          setProgress(0.95);
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
        toast.error(errorMsg || "結果の処理に失敗しました");
        setError(errorMsg);
        console.error("Result processing error:", err);
      } finally {
        setGenerating(false);
        setGeneratingAction(null);
        setScriptTaskId(null);
      }
    },
    onError: (error) => {
      toast.error(error || "台本生成に失敗しました");
      setError(error);
      setGenerating(false);
      setGeneratingAction(null);
      setScriptTaskId(null);
    },
    enabled: !!scriptTaskId,
  });

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
        // 自動モード：台本→保存を自動実行（SSE経由）
        setStatusMessage("台本を生成中...");
        setProgress(0.5);
        
        // 2. 台本生成（SSE経由）
        const { task_id } = await scriptApi.generateScriptStream({
          mode,
          outline_data: result.outline,
          reference_info: referenceInfo,
          model,
          temperature,
        });

        setScriptTaskId(task_id);
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
      // SSE経由で台本生成を開始
      const { task_id } = await scriptApi.generateScriptStream({
        mode,
        outline_data: generatedOutline,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setScriptTaskId(task_id);
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "台本生成の開始に失敗しました");
      setError(errorMsg);
      console.error("Script generation start error:", err);
      setGenerating(false);
      setGeneratingAction(null);
    }
  };

  return {
    handleGenerateOutline,
    handleGenerateScript,
  };
};

