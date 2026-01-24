import { useState } from "react";
import { useScriptStore } from "@/stores/scriptStore";
import { scriptApi } from "@/api/scripts";
import type { ComedyTitle, ComedyScript, ComedyTitleBatch } from "@/types";

export const useShortScriptGeneration = () => {
  const [titleCandidates, setTitleCandidates] = useState<ComedyTitleBatch | null>(null);

  const {
    currentStep,
    inputText,
    model,
    temperature,
    generatedTitle,
    generatedScript,
    isGenerating,
    progress,
    statusMessage,
    setCurrentStep,
    setInputText,
    setModel,
    setTemperature,
    setGeneratedTitle,
    setGeneratedScript,
    setGenerating,
    setProgress,
    setStatusMessage,
    setError,
    resetToInput,
  } = useScriptStore();

  // テーマからタイトル候補を生成（20個）
  const handleGenerateTitles = async () => {
    if (!inputText.trim()) {
      setError("テーマを入力してください");
      return;
    }

    setGenerating(true);
    setError(null);
    setStatusMessage("タイトル候補を生成中...");

    try {
      const response = await scriptApi.generateShortTitles(
        inputText,
        model,
        temperature
      );

      setTitleCandidates(response);
      setStatusMessage("タイトル候補生成完了");
    } catch (error: any) {
      console.error("タイトル生成エラー:", error);
      setError(error.message || "タイトル生成に失敗しました");
    } finally {
      setGenerating(false);
    }
  };

  // タイトル候補から選択して即座に台本生成
  const handleSelectTitleCandidate = async (candidate: any) => {
    const title: ComedyTitle = {
      title: candidate.title,
      mode: "comedy",
      theme: inputText,
      clickbait_elements: [
        candidate.hook_pattern,
        candidate.situation,
        candidate.chaos_element,
      ],
    };

    setGeneratedTitle(title);
    
    // タイトル選択後、即座に台本生成を開始
    setGenerating(true);
    setError(null);
    setCurrentStep("script");
    setProgress(0);
    setStatusMessage("60秒ショート台本を生成中...");

    try {
      setProgress(0.3);
      const response = await scriptApi.generateShortScript({
        mode: "comedy",
        title_data: title,
        model,
        temperature,
      });

      setProgress(0.9);
      setGeneratedScript(response.script);
      setStatusMessage("ショート台本生成完了！");
      setProgress(1.0);
    } catch (error: any) {
      console.error("ショート台本生成エラー:", error);
      setError(error.message || "ショート台本生成に失敗しました");
      setCurrentStep("input");
      setTitleCandidates(null);
    } finally {
      setGenerating(false);
    }
  };

  // タイトルを再生成
  const handleRegenerateTitles = async () => {
    setTitleCandidates(null);
    await handleGenerateTitles();
  };


  // 最初からやり直す
  const handleResetToInput = () => {
    setTitleCandidates(null);
    resetToInput();
  };

  return {
    // State
    currentStep,
    inputText,
    model,
    temperature,
    titleCandidates,
    generatedTitle,
    generatedScript,
    isGenerating,
    progress,
    statusMessage,

    // Actions
    setInputText,
    setModel,
    setTemperature,
    setTitleCandidates,
    handleGenerateTitles,
    handleSelectTitleCandidate,
    handleRegenerateTitles,
    handleResetToInput,
  };
};
