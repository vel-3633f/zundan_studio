import toast from "react-hot-toast";
import { createWebSocketClient, type WebSocketClient } from "@/api/websocket";
import { playNotificationSound } from "@/utils/notificationSound";

export const createWebSocketHandler = (
  taskId: string,
  setProgress: (progress: number) => void,
  setStatusMessage: (message: string) => void,
  setGenerating: (generating: boolean) => void,
  setGeneratedVideoPath: (path: string | null) => void
): WebSocketClient => {
  return createWebSocketClient(
    taskId,
    (data) => {
      setProgress(data.progress);
      if (data.message) {
        setStatusMessage(data.message);
      }

      if (data.status === "completed") {
        setGenerating(false);
        if (data.result?.video_path) {
          setGeneratedVideoPath(data.result.video_path);
          toast.success("動画生成が完了しました！");
          playNotificationSound();
        } else {
          toast.error("動画パスが取得できませんでした");
        }
      }

      if (data.status === "failed") {
        setGenerating(false);
        const errorMsg = data.error || "動画生成に失敗しました";
        toast.error(errorMsg);
        setStatusMessage(`エラー: ${errorMsg}`);
      }
    },
    (error) => {
      console.error("WebSocket error:", error);
      toast.error("進捗取得中にエラーが発生しました");
    },
    () => {
      console.log("WebSocket disconnected");
    }
  );
};

