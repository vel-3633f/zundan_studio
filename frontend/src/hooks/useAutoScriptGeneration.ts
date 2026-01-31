import { useState } from "react";
import toast from "react-hot-toast";
import { scriptApi } from "@/api/scripts";
import { extractErrorMessage } from "@/utils/errorHandler";
import { playNotificationSound } from "@/utils/notificationSound";
import { useSSEProgress } from "./useSSEProgress";
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
  mode: "comedy" | "thought_experiment" | "short_comedy",
  inputText: string,
  model: string,
  temperature: number
) => {
  const [taskId, setTaskId] = useState<string | null>(null);
  // SSE進捗監視
  useSSEProgress({
    taskId,
    onProgress: (progress, message) => {
      setProgress(progress);
      setStatusMessage(message);
    },
    onComplete: async (result) => {
      try {
        // 結果をストアに保存
        setGeneratedTitle(result.title);
        setGeneratedOutline(result.outline);
        setYoutubeMetadata(result.youtube_metadata || null);
        setGeneratedScript(result.script);
        
        setProgress(0.95);
        setStatusMessage("台本を保存中...");

        // 自動でJSON保存
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
      } catch (err: any) {
        const errorMsg = extractErrorMessage(err);
        toast.error(errorMsg || "結果の処理に失敗しました");
        setError(errorMsg);
        console.error("Result processing error:", err);
      } finally {
        setGenerating(false);
        setTaskId(null);
      }
    },
    onError: (error) => {
      toast.error(error || "自動生成に失敗しました");
      setError(error);
      setGenerating(false);
      setTaskId(null);
    },
    enabled: !!taskId,
  });

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
      // SSE経由で台本生成を開始
      const { task_id } = await scriptApi.generateFullScriptStream({
        mode,
        input_text: theme,
        model,
        temperature,
      });

      setTaskId(task_id);
      setStatusMessage("タスクを開始しました...");
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "自動生成の開始に失敗しました");
      setError(errorMsg);
      console.error("Auto generation start error:", err);
      setGenerating(false);
    }
  };

  return {
    handleAutoGenerateScript,
  };
};
