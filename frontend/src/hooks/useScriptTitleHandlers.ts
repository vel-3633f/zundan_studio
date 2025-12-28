import toast from "react-hot-toast";
import { scriptApi } from "@/api/scripts";
import { extractErrorMessage } from "@/utils/errorHandler";
import type { ComedyTitleBatch, ComedyTitle } from "@/types";

export const useScriptTitleHandlers = (
  setGenerating: (value: boolean) => void,
  setError: (error: string | null) => void,
  setTitleCandidates: (value: ComedyTitleBatch | null) => void,
  setSingleTitleCandidate: (value: {
    title: any;
    referenceInfo: string;
    searchResults: Record<string, any>;
  } | null) => void,
  setGeneratedTitle: (title: ComedyTitle | null) => void,
  setReferenceInfo: (info: string) => void,
  setSearchResults: (results: Record<string, any>) => void,
  setCurrentStep: (step: "input" | "title" | "outline" | "script") => void,
  setInputText: (text: string) => void,
  setStatusMessage: (message: string) => void,
  mode: "comedy",
  inputText: string,
  model: string,
  temperature: number,
  titleCandidates: ComedyTitleBatch | null,
  singleTitleCandidate: {
    title: any;
    referenceInfo: string;
    searchResults: Record<string, any>;
  } | null
) => {
  const handleGenerateRandomTitles = async () => {
    setGenerating(true);
    setError(null);

    try {
      const result = await scriptApi.generateComedyTitlesBatch();
      setTitleCandidates(result);
      toast.success(`${result.titles.length}個のタイトルを生成しました！`);
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "タイトル量産に失敗しました");
      setError(errorMsg);
      console.error("Random titles generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectTitleCandidate = (candidateId: number) => {
    if (!titleCandidates) return;

    const selected = titleCandidates.titles.find((t) => t.id === candidateId);
    if (!selected) return;

    const comedyTitle: ComedyTitle = {
      title: selected.title,
      mode: "comedy",
      theme: selected.situation,
      clickbait_elements: [
        selected.hook_pattern,
        selected.chaos_element,
        selected.expected_conflict,
      ],
    };

    setGeneratedTitle(comedyTitle);
    setInputText(selected.situation);
    setCurrentStep("title");
    setTitleCandidates(null);
    toast.success("タイトルを選択しました！");
  };

  const handleGenerateTitle = async () => {
    if (!inputText.trim()) {
      toast.error("漫談のテーマを入力してください");
      return;
    }

    setGenerating(true);
    setError(null);
    setStatusMessage("タイトルを生成中...");

    try {
      const result = await scriptApi.generateTitle({
        mode,
        input_text: inputText,
        model,
        temperature,
      });

      setSingleTitleCandidate({
        title: result.title,
        referenceInfo: result.reference_info,
        searchResults: result.search_results,
      });

      toast.success("タイトルを生成しました！選択して次へ進んでください");
    } catch (err: any) {
      const errorMsg = extractErrorMessage(err);
      toast.error(errorMsg || "タイトル生成に失敗しました");
      setError(errorMsg);
      console.error("Title generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectSingleTitle = () => {
    if (!singleTitleCandidate) return;

    setGeneratedTitle(singleTitleCandidate.title);
    setReferenceInfo(singleTitleCandidate.referenceInfo);
    setSearchResults(singleTitleCandidate.searchResults);
    setCurrentStep("title");
    setSingleTitleCandidate(null);
    toast.success("タイトルを選択しました！");
  };

  return {
    handleGenerateRandomTitles,
    handleSelectTitleCandidate,
    handleGenerateTitle,
    handleSelectSingleTitle,
  };
};

