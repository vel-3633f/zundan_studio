import { create } from "zustand";
import type { Background, Item } from "@/types";

interface ManagementState {
  // データ
  backgrounds: Background[];
  items: Item[];

  // ローディング状態
  isLoadingBackgrounds: boolean;
  isLoadingItems: boolean;

  // アクション
  setBackgrounds: (backgrounds: Background[]) => void;
  setItems: (items: Item[]) => void;

  addBackground: (background: Background) => void;
  addItem: (item: Item) => void;

  setLoadingBackgrounds: (loading: boolean) => void;
  setLoadingItems: (loading: boolean) => void;
}

export const useManagementStore = create<ManagementState>((set) => ({
  // 初期状態
  backgrounds: [],
  items: [],
  isLoadingBackgrounds: false,
  isLoadingItems: false,

  // アクション
  setBackgrounds: (backgrounds) => set({ backgrounds }),

  setItems: (items) => set({ items }),

  addBackground: (background) =>
    set((state) => ({
      backgrounds: [...state.backgrounds, background],
    })),

  addItem: (item) =>
    set((state) => ({
      items: [...state.items, item],
    })),

  setLoadingBackgrounds: (loading) => set({ isLoadingBackgrounds: loading }),

  setLoadingItems: (loading) => set({ isLoadingItems: loading }),
}));
