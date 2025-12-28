import { useState, useEffect, useRef } from "react";
import toast from "react-hot-toast";
import { videoApi } from "@/api/videos";
import { useVideoStore } from "@/stores/videoStore";
import { processJsonData } from "@/utils/jsonProcessor";

export const useJsonLoader = () => {
  const { setConversations, setSections, setJsonScriptData } = useVideoStore();

  const processJson = (jsonData: any) =>
    processJsonData(jsonData, setConversations, setSections, setJsonScriptData);

  const [jsonFiles, setJsonFiles] = useState<
    Array<{ filename: string; path: string }>
  >([]);
  const [selectedJsonFile, setSelectedJsonFile] = useState<string>("");
  const [isLoadingJsonFiles, setIsLoadingJsonFiles] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadJsonFiles = async () => {
      try {
        setIsLoadingJsonFiles(true);
        const files = await videoApi.listJsonFiles();
        setJsonFiles(files);
        if (files.length > 0 && !selectedJsonFile) {
          setSelectedJsonFile(files[0].filename);
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
      processJson(jsonData);
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
      processJson(jsonData);

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
  };
};

