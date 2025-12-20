import { create } from "zustand";
import type {
  ScriptMode,
  FoodTitle,
  FoodOutline,
  FoodScript,
  ComedyTitle,
  ComedyOutline,
  ComedyScript,
} from "@/types";

// ステップ定義
export type ScriptStep = "input" | "title" | "outline" | "script";

interface ScriptState {
  // === モードとステップ ===
  mode: ScriptMode;
  currentStep: ScriptStep;

  // === 入力データ ===
  inputText: string; // 食べ物名 or テーマ
  model: string;
  temperature: number;

  // === 生成データ ===
  generatedTitle: FoodTitle | ComedyTitle | null;
  generatedOutline: FoodOutline | ComedyOutline | null;
  generatedScript: FoodScript | ComedyScript | null;

  // === 参照情報（食べ物モードのみ） ===
  referenceInfo: string;
  searchResults: Record<string, any>;

  // === 生成状態 ===
  isGenerating: boolean;
  progress: number;
  statusMessage: string;
  error: string | null;

  // === アクション ===
  setMode: (mode: ScriptMode) => void;
  setCurrentStep: (step: ScriptStep) => void;
  setInputText: (text: string) => void;
  setModel: (model: string) => void;
  setTemperature: (temp: number) => void;

  setGeneratedTitle: (title: FoodTitle | ComedyTitle | null) => void;
  setGeneratedOutline: (outline: FoodOutline | ComedyOutline | null) => void;
  setGeneratedScript: (script: FoodScript | ComedyScript | null) => void;

  setReferenceInfo: (info: string) => void;
  setSearchResults: (results: Record<string, any>) => void;

  setGenerating: (generating: boolean) => void;
  setProgress: (progress: number) => void;
  setStatusMessage: (message: string) => void;
  setError: (error: string | null) => void;

  reset: () => void;
  resetToInput: () => void;
}

export const useScriptStore = create<ScriptState>((set) => ({
  // === 初期状態 ===
  mode: "food",
  currentStep: "input",

  inputText: "",
  model: "claude-3-5-sonnet",
  temperature: 0.7,

  generatedTitle: null,
  generatedOutline: null,
  generatedScript: null,

  referenceInfo: "",
  searchResults: {},

  isGenerating: false,
  progress: 0,
  statusMessage: "",
  error: null,

  // === アクション ===
  setMode: (mode) => set({ mode, currentStep: "input" }),

  setCurrentStep: (step) => set({ currentStep: step }),

  setInputText: (text) => set({ inputText: text }),

  setModel: (model) => set({ model }),

  setTemperature: (temp) => set({ temperature: temp }),

  setGeneratedTitle: (title) => set({ generatedTitle: title }),

  setGeneratedOutline: (outline) => set({ generatedOutline: outline }),

  setGeneratedScript: (script) => set({ generatedScript: script }),

  setReferenceInfo: (info) => set({ referenceInfo: info }),

  setSearchResults: (results) => set({ searchResults: results }),

  setGenerating: (generating) => set({ isGenerating: generating }),

  setProgress: (progress) => set({ progress }),

  setStatusMessage: (message) => set({ statusMessage: message }),

  setError: (error) => set({ error }),

  reset: () =>
    set({
      currentStep: "input",
      inputText: "",
      generatedTitle: null,
      generatedOutline: null,
      generatedScript: null,
      referenceInfo: "",
      searchResults: {},
      isGenerating: false,
      progress: 0,
      statusMessage: "",
      error: null,
    }),

  resetToInput: () =>
    set({
      currentStep: "input",
      generatedTitle: null,
      generatedOutline: null,
      generatedScript: null,
      isGenerating: false,
      progress: 0,
      statusMessage: "",
      error: null,
    }),
}));
