import { create } from "zustand";
import type { StoryOutline, FoodOverconsumptionScript } from "@/types";

interface ScriptState {
  // 入力データ
  foodName: string;
  model: string;
  temperature: number;

  // アウトライン
  outline: StoryOutline | null;
  outlineApproved: boolean;

  // 生成状態
  isGeneratingOutline: boolean;
  isGeneratingSections: boolean;
  taskId: string | null;
  progress: number;
  statusMessage: string;

  // 生成結果
  generatedScript: FoodOverconsumptionScript | null;
  referenceInfo: string;

  // アクション
  setFoodName: (name: string) => void;
  setModel: (model: string) => void;
  setTemperature: (temp: number) => void;

  setOutline: (outline: StoryOutline | null) => void;
  setOutlineApproved: (approved: boolean) => void;

  setGeneratingOutline: (generating: boolean) => void;
  setGeneratingSections: (generating: boolean) => void;
  setTaskId: (taskId: string | null) => void;
  setProgress: (progress: number) => void;
  setStatusMessage: (message: string) => void;

  setGeneratedScript: (script: FoodOverconsumptionScript | null) => void;
  setReferenceInfo: (info: string) => void;

  reset: () => void;
}

export const useScriptStore = create<ScriptState>((set) => ({
  // 初期状態
  foodName: "",
  model: "claude-3-5-sonnet",
  temperature: 0.7,
  outline: null,
  outlineApproved: false,
  isGeneratingOutline: false,
  isGeneratingSections: false,
  taskId: null,
  progress: 0,
  statusMessage: "",
  generatedScript: null,
  referenceInfo: "",

  // アクション
  setFoodName: (name) => set({ foodName: name }),

  setModel: (model) => set({ model }),

  setTemperature: (temp) => set({ temperature: temp }),

  setOutline: (outline) => set({ outline }),

  setOutlineApproved: (approved) => set({ outlineApproved: approved }),

  setGeneratingOutline: (generating) =>
    set({ isGeneratingOutline: generating }),

  setGeneratingSections: (generating) =>
    set({ isGeneratingSections: generating }),

  setTaskId: (taskId) => set({ taskId }),

  setProgress: (progress) => set({ progress }),

  setStatusMessage: (message) => set({ statusMessage: message }),

  setGeneratedScript: (script) => set({ generatedScript: script }),

  setReferenceInfo: (info) => set({ referenceInfo: info }),

  reset: () =>
    set({
      outline: null,
      outlineApproved: false,
      isGeneratingOutline: false,
      isGeneratingSections: false,
      taskId: null,
      progress: 0,
      statusMessage: "",
      generatedScript: null,
    }),
}));
