import { useEffect, useRef, useState } from "react";

interface SSEProgressData {
  task_id: string;
  status: "pending" | "processing" | "completed" | "failed" | "error";
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

interface UseSSEProgressOptions {
  taskId: string | null;
  onProgress: (progress: number, message: string) => void;
  onComplete: (result: any) => void;
  onError: (error: string) => void;
  enabled?: boolean;
  maxRetries?: number;
  retryDelay?: number;
}

/**
 * SSEで進捗を受信するカスタムフック
 * 
 * 自動再接続機能付き：
 * - ネットワークエラー時に自動的に再接続を試みる
 * - 最大再試行回数に達したらエラーコールバックを呼び出す
 */
export const useSSEProgress = ({
  taskId,
  onProgress,
  onComplete,
  onError,
  enabled = true,
  maxRetries = 3,
  retryDelay = 2000,
}: UseSSEProgressOptions) => {
  const eventSourceRef = useRef<EventSource | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isClosedRef = useRef(false);

  useEffect(() => {
    if (!taskId || !enabled) return;

    isClosedRef.current = false;

    const connect = () => {
      // 既に閉じられている場合は接続しない
      if (isClosedRef.current) return;

      try {
        // EventSourceを作成
        const eventSource = new EventSource(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/scripts/stream/${taskId}`
        );
        eventSourceRef.current = eventSource;

        // メッセージ受信時の処理
        eventSource.onmessage = (event) => {
          try {
            const data: SSEProgressData = JSON.parse(event.data);

            // 接続成功したのでリトライカウントをリセット
            setRetryCount(0);

            if (data.status === "processing" || data.status === "pending") {
              onProgress(data.progress, data.message);
            } else if (data.status === "completed") {
              onComplete(data.result);
              isClosedRef.current = true;
              eventSource.close();
            } else if (data.status === "failed" || data.status === "error") {
              onError(data.error || data.message || "タスクが失敗しました");
              isClosedRef.current = true;
              eventSource.close();
            }
          } catch (err) {
            console.error("SSE message parse error:", err);
            onError("進捗データの解析に失敗しました");
            isClosedRef.current = true;
            eventSource.close();
          }
        };

        // エラー時の処理（再接続ロジック付き）
        eventSource.onerror = (error) => {
          console.error("SSE connection error:", error);
          eventSource.close();

          // 既に閉じられている場合は再接続しない
          if (isClosedRef.current) return;

          // 最大再試行回数に達していない場合は再接続を試みる
          if (retryCount < maxRetries) {
            console.log(`SSE再接続を試みます... (${retryCount + 1}/${maxRetries})`);
            setRetryCount((prev) => prev + 1);
            
            retryTimeoutRef.current = setTimeout(() => {
              connect();
            }, retryDelay);
          } else {
            console.error("SSE最大再試行回数に達しました");
            onError("接続エラー: 最大再試行回数に達しました");
            isClosedRef.current = true;
          }
        };

        // 接続開始時のログ
        eventSource.onopen = () => {
          console.log("SSE接続が確立されました");
        };
      } catch (err) {
        console.error("SSE接続の作成に失敗しました:", err);
        onError("SSE接続の初期化に失敗しました");
        isClosedRef.current = true;
      }
    };

    // 初回接続
    connect();

    // クリーンアップ
    return () => {
      isClosedRef.current = true;
      
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
        retryTimeoutRef.current = null;
      }
      
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [taskId, enabled, onProgress, onComplete, onError, maxRetries, retryDelay, retryCount]);

  // 手動でクローズする関数
  const close = () => {
    isClosedRef.current = true;
    
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };

  return { close, retryCount };
};
