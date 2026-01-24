import { useState } from "react";
import toast from "react-hot-toast";
import { videoApi } from "@/api/videos";
import { managementApi } from "@/api/management";
import {
  processJsonData,
  extractBackgroundNames,
} from "@/utils/jsonProcessor";
import type { BackgroundCheckResponse, JsonFileInfo, JsonScriptData, ConversationLine, VideoSection } from "@/types";

interface FilePreviewData {
  filename: string;
  conversations: ConversationLine[];
  sections: VideoSection[] | null;
  jsonScriptData: JsonScriptData | null;
}

export const useBatchJsonLoader = () => {
  const [selectedFiles, setSelectedFiles] = useState<JsonFileInfo[]>([]);
  const [allFilesPreview, setAllFilesPreview] = useState<FilePreviewData[]>([]);
  const [previewData, setPreviewData] = useState<{
    conversations: ConversationLine[];
    sections: VideoSection[] | null;
    jsonScriptData: JsonScriptData | null;
  } | null>(null);
  const [backgroundCheckResult, setBackgroundCheckResult] =
    useState<BackgroundCheckResponse | null>(null);
  const [isCheckingBackgrounds, setIsCheckingBackgrounds] = useState(false);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);

  const loadPreviewForFiles = async (files: JsonFileInfo[]) => {
    if (files.length === 0) {
      setPreviewData(null);
      setAllFilesPreview([]);
      setBackgroundCheckResult(null);
      return;
    }

    setIsLoadingPreview(true);
    try {
      // 全ファイルのプレビューデータを読み込む
      const allPreviews: FilePreviewData[] = [];
      
      for (const file of files) {
        try {
          const jsonData = await videoApi.getJsonFile(file.filename);

          // 会話データとセクション情報を抽出
          let conversations: ConversationLine[] = [];
          let sections: VideoSection[] | null = null;
          let jsonScriptData: JsonScriptData | null = null;

          const tempSetConversations = (convs: ConversationLine[]) => {
            conversations = convs;
          };
          const tempSetSections = (sects: VideoSection[] | null) => {
            sections = sects;
          };
          const tempSetJsonScriptData = (data: JsonScriptData | null) => {
            jsonScriptData = data;
          };

          processJsonData(
            jsonData,
            tempSetConversations,
            tempSetSections,
            tempSetJsonScriptData
          );

          allPreviews.push({
            filename: file.filename,
            conversations,
            sections,
            jsonScriptData,
          });
        } catch (error) {
          console.error(`ファイル読み込みエラー (${file.filename}):`, error);
        }
      }

      setAllFilesPreview(allPreviews);
      
      // 最初のファイルのプレビューデータを設定
      const firstPreview = allPreviews[0];
      if (firstPreview) {
        setPreviewData({
          conversations: firstPreview.conversations,
          sections: firstPreview.sections,
          jsonScriptData: firstPreview.jsonScriptData,
        });
      }

      // 背景画像チェック（全ファイルの背景を集約）
      const allBackgroundNames = new Set<string>();
      for (const file of files) {
        try {
          const data = await videoApi.getJsonFile(file.filename);
          const bgNames = extractBackgroundNames(data);
          bgNames.forEach((name) => allBackgroundNames.add(name));
        } catch (error) {
          console.error(`背景抽出エラー (${file.filename}):`, error);
        }
      }

      if (allBackgroundNames.size > 0) {
        await checkBackgrounds(Array.from(allBackgroundNames));
      } else {
        setBackgroundCheckResult(null);
      }
    } catch (error: any) {
      console.error("プレビュー読み込みエラー:", error);
      toast.error("プレビューの読み込みに失敗しました");
      setPreviewData(null);
      setBackgroundCheckResult(null);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const checkBackgrounds = async (backgroundNames: string[]) => {
    setIsCheckingBackgrounds(true);
    setBackgroundCheckResult(null);
    try {
      const result = await managementApi.backgrounds.check(backgroundNames);
      setBackgroundCheckResult(result);
    } catch (error: any) {
      console.error("背景画像確認エラー:", error);
      setBackgroundCheckResult(null);
    } finally {
      setIsCheckingBackgrounds(false);
    }
  };

  const clearPreview = () => {
    setPreviewData(null);
    setAllFilesPreview([]);
    setBackgroundCheckResult(null);
    setSelectedFiles([]);
  };

  const getPreviewForFile = (filename: string) => {
    return allFilesPreview.find((p) => p.filename === filename) || null;
  };

  return {
    selectedFiles,
    setSelectedFiles,
    allFilesPreview,
    previewData,
    backgroundCheckResult,
    isCheckingBackgrounds,
    isLoadingPreview,
    loadPreviewForFiles,
    getPreviewForFile,
    clearPreview,
  };
};
