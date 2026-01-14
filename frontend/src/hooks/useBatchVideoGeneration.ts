import { useRef } from "react";
import toast from "react-hot-toast";
import { useVideoStore } from "@/stores/videoStore";
import { videoApi } from "@/api/videos";
import type { JsonFileInfo } from "@/types";
import type { WebSocketClient } from "@/api/websocket";
import { createWebSocketHandler } from "./useWebSocketHandler";
import { playNotificationSound } from "@/utils/notificationSound";

export const useBatchVideoGeneration = () => {
  const wsClientRef = useRef<WebSocketClient | null>(null);
  const isCancelledRef = useRef(false);

  const {
    batchGeneration,
    setBatchGenerating,
    setBatchSelectedFiles,
    setBatchCurrentFileIndex,
    setBatchCurrentProgress,
    setBatchCurrentMessage,
    addBatchCompletedFile,
    addBatchFailedFile,
    resetBatchGeneration,
  } = useVideoStore();

  const handleStartBatchGeneration = async (selectedFiles: JsonFileInfo[]) => {
    if (selectedFiles.length === 0) {
      toast.error("ファイルを選択してください");
      return;
    }

    // 初期化
    resetBatchGeneration();
    setBatchSelectedFiles(selectedFiles);
    setBatchGenerating(true);
    isCancelledRef.current = false;

    toast.success(`バッチ生成を開始します（${selectedFiles.length}件）`, {
      duration: 3000,
    });

    // 順次処理
    for (let i = 0; i < selectedFiles.length; i++) {
      // キャンセルチェック
      if (isCancelledRef.current) {
        toast("バッチ生成をキャンセルしました", {
          icon: "ℹ️",
          duration: 3000,
        });
        break;
      }

      const file = selectedFiles[i];
      setBatchCurrentFileIndex(i);
      setBatchCurrentProgress(0);
      setBatchCurrentMessage(`${file.filename} を処理中...`);

      try {
        // 1. JSONファイルを読み込む
        const jsonData = await videoApi.getJsonFile(file.filename);

        if (!jsonData.sections || jsonData.sections.length === 0) {
          throw new Error("セクション情報が見つかりません");
        }

        // 2. 会話データを抽出
        const conversations = jsonData.sections.flatMap((section: any) =>
          section.segments.map((segment: any) => ({
            speaker: segment.speaker,
            text: segment.text,
            text_for_voicevox: segment.text_for_voicevox || segment.text,
            expression: segment.expression || "normal",
            background: section.scene_background || "default",
            visible_characters: segment.visible_characters || [segment.speaker],
            character_expressions: segment.character_expressions || {},
          }))
        );

        // 3. 動画生成リクエスト
        setBatchCurrentMessage(`${file.filename} の動画を生成中...`);
        const response = await videoApi.generate({
          conversations,
          enable_subtitles: true,
          conversation_mode: "duo",
          sections: jsonData.sections,
          title: jsonData.title,
        });

        // 4. WebSocketで進捗を監視
        await new Promise<void>((resolve, reject) => {
          const wsClient = createWebSocketHandler(
            response.task_id,
            (progress) => setBatchCurrentProgress(progress),
            (message) => setBatchCurrentMessage(message),
            (isGenerating) => {
              if (!isGenerating) {
                // 生成完了
                wsClient.disconnect();
                resolve();
              }
            },
            () => {
              // 動画パスは個別には保存しない（バッチ処理なので）
            }
          );

          wsClientRef.current = wsClient;

          // WebSocket接続
          wsClient.connect();

          // エラーハンドリング用のタイムアウト（10分）
          setTimeout(() => {
            if (wsClientRef.current === wsClient) {
              wsClient.disconnect();
              reject(new Error("タイムアウト: 動画生成に時間がかかりすぎています"));
            }
          }, 10 * 60 * 1000);
        });

        // 5. is_generatedフラグを更新
        await videoApi.updateJsonFileStatus(file.filename, {
          is_generated: true,
        });

        // 6. 成功として記録
        addBatchCompletedFile(file.filename);
        toast.success(`${file.filename} の動画生成が完了しました`);
        playNotificationSound();
      } catch (error: any) {
        console.error(`動画生成エラー (${file.filename}):`, error);
        const errorMsg =
          error.response?.data?.detail ||
          error.message ||
          "動画生成に失敗しました";

        // 失敗として記録
        addBatchFailedFile(file.filename, errorMsg);
        toast.error(`${file.filename}: ${errorMsg}`);

        // WebSocket接続をクリーンアップ
        if (wsClientRef.current) {
          wsClientRef.current.disconnect();
          wsClientRef.current = null;
        }

        // エラーが発生しても次のファイルに進む
        continue;
      }
    }

    // 完了
    setBatchGenerating(false);
    setBatchCurrentMessage("バッチ生成が完了しました");

    // 結果サマリーを表示
    const completed = useVideoStore.getState().batchGeneration.completedFiles.length;
    const failed = useVideoStore.getState().batchGeneration.failedFiles.length;

    if (failed === 0) {
      toast.success(`すべての動画生成が完了しました（${completed}件）`);
      playNotificationSound();
    } else {
      toast.error(
        `バッチ生成完了: 成功 ${completed}件、失敗 ${failed}件`
      );
    }
  };

  const handleCancelBatchGeneration = () => {
    isCancelledRef.current = true;
    if (wsClientRef.current) {
      wsClientRef.current.disconnect();
      wsClientRef.current = null;
    }
    setBatchGenerating(false);
    toast("バッチ生成をキャンセルしています...", {
      icon: "ℹ️",
      duration: 3000,
    });
  };

  return {
    batchGeneration,
    handleStartBatchGeneration,
    handleCancelBatchGeneration,
  };
};
