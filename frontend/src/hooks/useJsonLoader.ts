import { useState, useEffect, useRef } from "react";
import toast from "react-hot-toast";
import { videoApi } from "@/api/videos";
import { useVideoStore } from "@/stores/videoStore";
import {
  processJsonData,
  extractBackgroundNames,
} from "@/utils/jsonProcessor";
import { managementApi } from "@/api/management";
import type { BackgroundCheckResponse, JsonFileInfo } from "@/types";

export const useJsonLoader = () => {
  const { setConversations, setSections, setJsonScriptData } = useVideoStore();

  const processJson = async (jsonData: any) => {
    const success = processJsonData(
      jsonData,
      setConversations,
      setSections,
      setJsonScriptData
    );

    if (success) {
      const backgroundNames = extractBackgroundNames(jsonData);
      if (backgroundNames.length > 0) {
        await checkBackgrounds(backgroundNames);
      } else {
        setBackgroundCheckResult(null);
      }
    } else {
      setBackgroundCheckResult(null);
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

  const [jsonFiles, setJsonFiles] = useState<JsonFileInfo[]>([]);
  const [selectedJsonFile, setSelectedJsonFile] = useState<string>("");
  const [isLoadingJsonFiles, setIsLoadingJsonFiles] = useState(false);
  const [backgroundCheckResult, setBackgroundCheckResult] =
    useState<BackgroundCheckResponse | null>(null);
  const [isCheckingBackgrounds, setIsCheckingBackgrounds] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadJsonFiles = async () => {
      try {
        setIsLoadingJsonFiles(true);
        const files = await videoApi.listJsonFiles();
        // 生成済みのファイルを除外
        const ungeneratedFiles = files.filter((file) => !file.is_generated);
        setJsonFiles(ungeneratedFiles);
        if (ungeneratedFiles.length > 0 && !selectedJsonFile) {
          setSelectedJsonFile(ungeneratedFiles[0].filename);
        }
      } catch (error) {
        console.error("JSONファイル一覧取得エラー:", error);
        toast.error("JSONファイル一覧の取得に失敗しました");
      } finally {
        setIsLoadingJsonFiles(false);
      }
    };

    loadJsonFiles();
  }, []);

  const handleLoadSelectedJson = async () => {
    if (!selectedJsonFile) {
      toast.error("JSONファイルを選択してください");
      return;
    }

    try {
      const jsonData = await videoApi.getJsonFile(selectedJsonFile);
      await processJson(jsonData);
    } catch (error: any) {
      console.error("JSON読み込みエラー:", error);
      if (error.response?.status === 404) {
        toast.error("ファイルが見つかりませんでした。");
      } else {
        toast.error("ファイルの読み込みに失敗しました。");
      }
    }
  };

  const handleLoadJson = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    if (!file.name.endsWith(".json")) {
      toast.error("JSONファイルを選択してください");
      return;
    }

    try {
      const fileContent = await file.text();
      const jsonData = JSON.parse(fileContent);
      await processJson(jsonData);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("JSON読み込みエラー:", error);
      if (error instanceof SyntaxError) {
        toast.error("JSONファイルの形式が正しくありません。");
      } else {
        toast.error("ファイルの読み込みに失敗しました。");
      }
    }
  };

  return {
    jsonFiles,
    selectedJsonFile,
    isLoadingJsonFiles,
    fileInputRef,
    setSelectedJsonFile,
    handleLoadSelectedJson,
    handleLoadJson,
    backgroundCheckResult,
    isCheckingBackgrounds,
  };
};

