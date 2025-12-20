import apiClient from "./client";
import type {
  TitleRequest,
  TitleResponse,
  UnifiedOutlineRequest,
  UnifiedOutlineResponse,
  ScriptRequest,
  ScriptResponse,
  FullScriptRequest,
  FullScriptResponse,
  // 旧型定義（後方互換性）
  OutlineRequest,
  OutlineResponse,
  SectionRequest,
  FoodOverconsumptionScript,
} from "@/types";

export const scriptApi = {
  /**
   * タイトルを生成（統合API）
   */
  generateTitle: async (data: TitleRequest): Promise<TitleResponse> => {
    const response = await apiClient.post<TitleResponse>(
      "/scripts/title",
      data
    );
    return response.data;
  },

  /**
   * アウトラインを生成（統合API）
   */
  generateOutline: async (
    data: UnifiedOutlineRequest
  ): Promise<UnifiedOutlineResponse> => {
    const response = await apiClient.post<UnifiedOutlineResponse>(
      "/scripts/outline",
      data
    );
    return response.data;
  },

  /**
   * 台本を生成（統合API）
   */
  generateScript: async (data: ScriptRequest): Promise<ScriptResponse> => {
    const response = await apiClient.post<ScriptResponse>(
      "/scripts/script",
      data
    );
    return response.data;
  },

  /**
   * 完全台本を生成（3段階一括）
   */
  generateFullScript: async (
    data: FullScriptRequest
  ): Promise<FullScriptResponse> => {
    const response = await apiClient.post<FullScriptResponse>(
      "/scripts/full",
      data
    );
    return response.data;
  },

  /**
   * ヘルスチェック
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await apiClient.get("/scripts/health");
    return response.data;
  },

  // === 旧API（後方互換性のため保持） ===
  /**
   * アウトラインを生成（旧API）
   * @deprecated 新しいgenerateOutlineを使用してください
   */
  generateOutlineOld: async (
    data: OutlineRequest
  ): Promise<OutlineResponse> => {
    const response = await apiClient.post<OutlineResponse>(
      "/scripts/outline",
      data
    );
    return response.data;
  },

  /**
   * セクションを生成（旧API）
   * @deprecated 新しいgenerateScriptを使用してください
   */
  generateSections: async (
    data: SectionRequest
  ): Promise<FoodOverconsumptionScript> => {
    const response = await apiClient.post<FoodOverconsumptionScript>(
      "/scripts/sections",
      data
    );
    return response.data;
  },
};
