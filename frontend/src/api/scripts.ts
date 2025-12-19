import apiClient from "./client";
import type {
  OutlineRequest,
  OutlineResponse,
  SectionRequest,
  FoodOverconsumptionScript,
} from "@/types";

export const scriptApi = {
  /**
   * アウトラインを生成
   */
  generateOutline: async (data: OutlineRequest): Promise<OutlineResponse> => {
    const response = await apiClient.post<OutlineResponse>(
      "/scripts/outline",
      data
    );
    return response.data;
  },

  /**
   * セクションを生成
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

  /**
   * ヘルスチェック
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await apiClient.get("/scripts/health");
    return response.data;
  },
};
