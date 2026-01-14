import { useRef, useEffect } from "react";
import toast from "react-hot-toast";
import { useVideoStore } from "@/stores/videoStore";
import { videoApi } from "@/api/videos";
import type { WebSocketClient } from "@/api/websocket";
import { createWebSocketHandler } from "./useWebSocketHandler";

export const useVideoGeneration = () => {
  const wsClientRef = useRef<WebSocketClient | null>(null);
  const {
    conversations,
    jsonScriptData,
    enableSubtitles,
    conversationMode,
    sections,
    isGenerating,
    progress,
    statusMessage,
    generatedVideoPath,
    setGenerating,
    setTaskId,
    setProgress,
    setStatusMessage,
    setGeneratedVideoPath,
    reset,
  } = useVideoStore();

  useEffect(() => {
    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
        wsClientRef.current = null;
      }
    };
  }, []);

  const handleGenerate = async () => {
    if (conversations.length === 0) {
      toast.error("セリフを追加してください");
      return;
    }

    try {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
        wsClientRef.current = null;
      }

      reset();
      setGenerating(true);
      setProgress(0);
      setStatusMessage("動画生成を開始しています...");

      const response = await videoApi.generate({
        conversations,
        title: jsonScriptData?.title || undefined,
        enable_subtitles: enableSubtitles,
        conversation_mode: conversationMode,
        sections: sections || undefined,
      });

      setTaskId(response.task_id);
      setStatusMessage("動画生成タスクを開始しました");

      const wsClient = createWebSocketHandler(
        response.task_id,
        setProgress,
        setStatusMessage,
        setGenerating,
        setGeneratedVideoPath
      );

      wsClientRef.current = wsClient;
      wsClient.connect();

      toast.success("動画生成を開始しました");
    } catch (error: any) {
      console.error("動画生成エラー:", error);
      setGenerating(false);
      const errorMsg =
        error.response?.data?.detail || "動画生成の開始に失敗しました";
      toast.error(errorMsg);
      setStatusMessage(`エラー: ${errorMsg}`);
    }
  };

  return {
    isGenerating,
    progress,
    statusMessage,
    generatedVideoPath,
    handleGenerate,
  };
};

