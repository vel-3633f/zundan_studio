import toast from "react-hot-toast";
import {
  mockComedyTitle,
  mockComedyOutline,
  mockComedyScript,
  mockReferenceInfo,
  mockSearchResults,
} from "@/utils/mockData";

export const useScriptTestData = (
  setGeneratedTitle: (title: any) => void,
  setGeneratedOutline: (outline: any) => void,
  setGeneratedScript: (script: any) => void,
  setReferenceInfo: (info: string) => void,
  setSearchResults: (results: Record<string, any>) => void,
  setCurrentStep: (step: "input" | "title" | "outline" | "script") => void
) => {
  const handleLoadTestData = (step: "title" | "outline" | "script") => {
    try {
      if (step === "title") {
        setGeneratedTitle(mockComedyTitle);
        setReferenceInfo(mockReferenceInfo);
        setSearchResults(mockSearchResults);
        setCurrentStep("title");
        toast.success("テストデータ（タイトル）を読み込みました");
      } else if (step === "outline") {
        setGeneratedTitle(mockComedyTitle);
        setGeneratedOutline(mockComedyOutline);
        setReferenceInfo(mockReferenceInfo);
        setSearchResults(mockSearchResults);
        setCurrentStep("outline");
        toast.success("テストデータ（アウトライン）を読み込みました");
      } else if (step === "script") {
        setGeneratedTitle(mockComedyTitle);
        setGeneratedOutline(mockComedyOutline);
        setGeneratedScript(mockComedyScript);
        setReferenceInfo(mockReferenceInfo);
        setSearchResults(mockSearchResults);
        setCurrentStep("script");
        toast.success("テストデータ（完成台本）を読み込みました");
      }
    } catch (error) {
      console.error("Test data load error:", error);
      toast.error("テストデータの読み込みに失敗しました");
    }
  };

  return { handleLoadTestData };
};

