import { create } from "zustand";
import type { Background, Item, Food } from "@/types";

interface ManagementState {
  // データ
  backgrounds: Background[];
  items: Item[];
  foods: Food[];

  // ローディング状態
  isLoadingBackgrounds: boolean;
  isLoadingItems: boolean;
  isLoadingFoods: boolean;

  // アクション
  setBackgrounds: (backgrounds: Background[]) => void;
  setItems: (items: Item[]) => void;
  setFoods: (foods: Food[]) => void;

  addBackground: (background: Background) => void;
  addItem: (item: Item) => void;
  addFood: (food: Food) => void;

  removeFood: (foodId: number) => void;

  setLoadingBackgrounds: (loading: boolean) => void;
  setLoadingItems: (loading: boolean) => void;
  setLoadingFoods: (loading: boolean) => void;
}

export const useManagementStore = create<ManagementState>((set) => ({
  // 初期状態
  backgrounds: [],
  items: [],
  foods: [],
  isLoadingBackgrounds: false,
  isLoadingItems: false,
  isLoadingFoods: false,

  // アクション
  setBackgrounds: (backgrounds) => set({ backgrounds }),

  setItems: (items) => set({ items }),

  setFoods: (foods) => set({ foods }),

  addBackground: (background) =>
    set((state) => ({
      backgrounds: [...state.backgrounds, background],
    })),

  addItem: (item) =>
    set((state) => ({
      items: [...state.items, item],
    })),

  addFood: (food) =>
    set((state) => ({
      foods: [...state.foods, food],
    })),

  removeFood: (foodId) =>
    set((state) => ({
      foods: state.foods.filter((f) => f.id !== foodId),
    })),

  setLoadingBackgrounds: (loading) => set({ isLoadingBackgrounds: loading }),

  setLoadingItems: (loading) => set({ isLoadingItems: loading }),

  setLoadingFoods: (loading) => set({ isLoadingFoods: loading }),
}));
