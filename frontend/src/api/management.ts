import apiClient from "./client";
import type { Background, Item } from "@/types";

export const managementApi = {
  // Background Management
  backgrounds: {
    list: async (): Promise<Background[]> => {
      const response = await apiClient.get<Background[]>(
        "/management/backgrounds"
      );
      return response.data;
    },

    upload: async (file: File): Promise<Background> => {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post<Background>(
        "/management/backgrounds/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },

    generate: async (name: string): Promise<{ success: boolean; message: string; path?: string }> => {
      const response = await apiClient.post<{ success: boolean; message: string; path?: string }>(
        "/management/backgrounds/generate",
        { name }
      );
      return response.data;
    },
  },

  // Item Management
  items: {
    list: async (): Promise<Item[]> => {
      const response = await apiClient.get<Item[]>("/management/items");
      return response.data;
    },

    upload: async (file: File): Promise<Item> => {
      const formData = new FormData();
      formData.append("file", file);
      const response = await apiClient.post<Item>(
        "/management/items/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    },
  },

  /**
   * ヘルスチェック
   */
  healthCheck: async (): Promise<{ status: string; service: string }> => {
    const response = await apiClient.get("/management/health");
    return response.data;
  },
};
