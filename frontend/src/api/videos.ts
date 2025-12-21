import apiClient from "./client";
import type {
  VideoGenerationRequest,
  VideoGenerationResponse,
  VideoStatusResponse,
} from "@/types";

export const videoApi = {
  /**
   * 動画生成リクエストを送信
   */
  generate: async (
    data: VideoGenerationRequest
  ): Promise<VideoGenerationResponse> => {
    const response = await apiClient.post<VideoGenerationResponse>(
      "/videos/generate",
      data
    );
    return response.data;
  },

  /**
   * 動画生成のステータスを取得
   */
  getStatus: async (taskId: string): Promise<VideoStatusResponse> => {
    const response = await apiClient.get<VideoStatusResponse>(
      `/videos/status/${taskId}`
    );
    return response.data;
  },

  /**
   * ヘルスチェック
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await apiClient.get("/videos/health");
    return response.data;
  },
};
