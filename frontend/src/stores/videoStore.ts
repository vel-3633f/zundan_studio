import { create } from "zustand";
import type { ConversationLine, VideoSection } from "@/types";

interface VideoState {
  // 会話データ
  conversations: ConversationLine[];

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

  // アクション
  addConversation: (conversation: ConversationLine) => void;
  updateConversation: (index: number, conversation: ConversationLine) => void;
  removeConversation: (index: number) => void;
  clearConversations: () => void;

  setEnableSubtitles: (enabled: boolean) => void;
  setConversationMode: (mode: string) => void;
  setSections: (sections: VideoSection[] | null) => void;

  setGenerating: (generating: boolean) => void;
  setTaskId: (taskId: string | null) => void;
  setProgress: (progress: number) => void;
  setStatusMessage: (message: string) => void;
  setGeneratedVideoPath: (path: string | null) => void;

  reset: () => void;
}

export const useVideoStore = create<VideoState>((set) => ({
  // 初期状態
  conversations: [],
  enableSubtitles: true,
  conversationMode: "duo",
  sections: null,
  isGenerating: false,
  taskId: null,
  progress: 0,
  statusMessage: "",
  generatedVideoPath: null,

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

  setEnableSubtitles: (enabled) => set({ enableSubtitles: enabled }),

  setConversationMode: (mode) => set({ conversationMode: mode }),

  setSections: (sections) => set({ sections }),

  setGenerating: (generating) => set({ isGenerating: generating }),

  setTaskId: (taskId) => set({ taskId }),

  setProgress: (progress) => set({ progress }),

  setStatusMessage: (message) => set({ statusMessage: message }),

  setGeneratedVideoPath: (path) => set({ generatedVideoPath: path }),

  reset: () =>
    set({
      isGenerating: false,
      taskId: null,
      progress: 0,
      statusMessage: "",
      generatedVideoPath: null,
    }),
}));
