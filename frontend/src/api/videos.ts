import apiClient from "./client";
import type {
  VideoGenerationRequest,
  VideoGenerationResponse,
  VideoStatusResponse,
  JsonFileInfo,
  JsonFileStatusUpdate,
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

  /**
   * JSONファイル一覧を取得
   */
  listJsonFiles: async (): Promise<JsonFileInfo[]> => {
    const response = await apiClient.get<JsonFileInfo[]>(
      "/videos/json-files"
    );
    return response.data;
  },

  /**
   * JSONファイルの内容を取得
   */
  getJsonFile: async (filename: string): Promise<any> => {
    const response = await apiClient.get(`/videos/json-files/${encodeURIComponent(filename)}`);
    return response.data;
  },

  /**
   * JSONファイルのis_generatedステータスを更新
   */
  updateJsonFileStatus: async (
    filename: string,
    statusUpdate: JsonFileStatusUpdate
  ): Promise<JsonFileInfo> => {
    const response = await apiClient.patch<JsonFileInfo>(
      `/videos/json-files/${encodeURIComponent(filename)}/status`,
      statusUpdate
    );
    return response.data;
  },

  /**
   * JSONファイルを削除
   */
  deleteJsonFile: async (filename: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.delete<{ success: boolean; message: string }>(
      `/videos/json-files/${encodeURIComponent(filename)}`
    );
    return response.data;
  },
};
