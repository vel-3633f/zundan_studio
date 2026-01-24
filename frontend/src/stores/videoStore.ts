import { create } from "zustand";
import type { ConversationLine, VideoSection, JsonScriptData, JsonFileInfo } from "@/types";

interface BatchGenerationState {
  isGenerating: boolean;
  selectedFiles: JsonFileInfo[];
  currentFileIndex: number;
  currentFileName: string;
  totalFiles: number;
  completedFiles: string[];
  failedFiles: { filename: string; error: string }[];
  currentProgress: number;
  currentMessage: string;
}

interface VideoState {
  // 会話データ
  conversations: ConversationLine[];

  // JSON全体のデータ（メタ情報を含む）
  jsonScriptData: JsonScriptData | null;

  // 生成設定
  enableSubtitles: boolean;
  conversationMode: string;
  sections: VideoSection[] | null;

  // 生成状態
  isGenerating: boolean;
  taskId: string | null;
  progress: number;
  statusMessage: string;

  // 生成結果
  generatedVideoPath: string | null;

  // バッチ生成状態
  batchGeneration: BatchGenerationState;

  // アクション
  addConversation: (conversation: ConversationLine) => void;
  updateConversation: (index: number, conversation: ConversationLine) => void;
  removeConversation: (index: number) => void;
  clearConversations: () => void;
  setConversations: (conversations: ConversationLine[]) => void;

  setEnableSubtitles: (enabled: boolean) => void;
  setConversationMode: (mode: string) => void;
  setSections: (sections: VideoSection[] | null) => void;
  setJsonScriptData: (data: JsonScriptData | null) => void;

  setGenerating: (generating: boolean) => void;
  setTaskId: (taskId: string | null) => void;
  setProgress: (progress: number) => void;
  setStatusMessage: (message: string) => void;
  setGeneratedVideoPath: (path: string | null) => void;

  // バッチ生成アクション
  setBatchGenerating: (generating: boolean) => void;
  setBatchSelectedFiles: (files: JsonFileInfo[]) => void;
  setBatchCurrentFileIndex: (index: number) => void;
  setBatchCurrentProgress: (progress: number) => void;
  setBatchCurrentMessage: (message: string) => void;
  addBatchCompletedFile: (filename: string) => void;
  addBatchFailedFile: (filename: string, error: string) => void;
  resetBatchGeneration: () => void;

  reset: () => void;
}

export const useVideoStore = create<VideoState>((set) => ({
  // 初期状態
  conversations: [],
  jsonScriptData: null,
  enableSubtitles: true,
  conversationMode: "duo",
  sections: null,
  isGenerating: false,
  taskId: null,
  progress: 0,
  statusMessage: "",
  generatedVideoPath: null,
  batchGeneration: {
    isGenerating: false,
    selectedFiles: [],
    currentFileIndex: 0,
    currentFileName: "",
    totalFiles: 0,
    completedFiles: [],
    failedFiles: [],
    currentProgress: 0,
    currentMessage: "",
  },

  // アクション
  addConversation: (conversation) =>
    set((state) => ({
      conversations: [...state.conversations, conversation],
    })),

  updateConversation: (index, conversation) =>
    set((state) => ({
      conversations: state.conversations.map((c, i) =>
        i === index ? conversation : c
      ),
    })),

  removeConversation: (index) =>
    set((state) => ({
      conversations: state.conversations.filter((_, i) => i !== index),
    })),

  clearConversations: () => set({ conversations: [] }),

  setConversations: (conversations) => set({ conversations }),

  setEnableSubtitles: (enabled) => set({ enableSubtitles: enabled }),

  setConversationMode: (mode) => set({ conversationMode: mode }),

  setSections: (sections) => set({ sections }),
  setJsonScriptData: (data) => set({ jsonScriptData: data }),

  setGenerating: (generating) => set({ isGenerating: generating }),

  setTaskId: (taskId) => set({ taskId }),

  setProgress: (progress) => set({ progress }),

  setStatusMessage: (message) => set({ statusMessage: message }),

  setGeneratedVideoPath: (path) => set({ generatedVideoPath: path }),

  // バッチ生成アクション
  setBatchGenerating: (generating) =>
    set((state) => ({
      batchGeneration: { ...state.batchGeneration, isGenerating: generating },
    })),

  setBatchSelectedFiles: (files) =>
    set((state) => ({
      batchGeneration: {
        ...state.batchGeneration,
        selectedFiles: files,
        totalFiles: files.length,
      },
    })),

  setBatchCurrentFileIndex: (index) =>
    set((state) => ({
      batchGeneration: { 
        ...state.batchGeneration, 
        currentFileIndex: index,
        currentFileName: state.batchGeneration.selectedFiles[index]?.filename || "",
      },
    })),

  setBatchCurrentProgress: (progress) =>
    set((state) => ({
      batchGeneration: { ...state.batchGeneration, currentProgress: progress },
    })),

  setBatchCurrentMessage: (message) =>
    set((state) => ({
      batchGeneration: { ...state.batchGeneration, currentMessage: message },
    })),

  addBatchCompletedFile: (filename) =>
    set((state) => ({
      batchGeneration: {
        ...state.batchGeneration,
        completedFiles: [...state.batchGeneration.completedFiles, filename],
      },
    })),

  addBatchFailedFile: (filename, error) =>
    set((state) => ({
      batchGeneration: {
        ...state.batchGeneration,
        failedFiles: [
          ...state.batchGeneration.failedFiles,
          { filename, error },
        ],
      },
    })),

  resetBatchGeneration: () =>
    set({
      batchGeneration: {
        isGenerating: false,
        selectedFiles: [],
        currentFileIndex: 0,
        currentFileName: "",
        totalFiles: 0,
        completedFiles: [],
        failedFiles: [],
        currentProgress: 0,
        currentMessage: "",
      },
    }),

  reset: () =>
    set({
      isGenerating: false,
      taskId: null,
      progress: 0,
      statusMessage: "",
      generatedVideoPath: null,
    }),
}));
