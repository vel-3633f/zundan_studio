import apiClient from "./client";
import type { Background, Item, Food, FoodCreateRequest } from "@/types";

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

  // Food Management
  foods: {
    list: async (): Promise<Food[]> => {
      const response = await apiClient.get<Food[]>("/management/foods");
      return response.data;
    },

    create: async (data: FoodCreateRequest): Promise<Food> => {
      const response = await apiClient.post<Food>("/management/foods", data);
      return response.data;
    },

    delete: async (foodId: number): Promise<void> => {
      await apiClient.delete(`/management/foods/${foodId}`);
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
