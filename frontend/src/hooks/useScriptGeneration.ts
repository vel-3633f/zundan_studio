import { useState } from "react";
import toast from "react-hot-toast";
import { useScriptStore } from "@/stores/scriptStore";
import { useScriptTitleHandlers } from "./useScriptTitleHandlers";
import { useScriptGenerationHandlers } from "./useScriptGenerationHandlers";
import { useScriptRegenerateHandlers } from "./useScriptRegenerateHandlers";
import { useScriptTestData } from "./useScriptTestData";
import { useAutoScriptGeneration } from "./useAutoScriptGeneration";
import { useAutoFromTitleGeneration } from "./useAutoFromTitleGeneration";
import { createScriptGenerationReturn } from "./useScriptGenerationReturn";
import type { ComedyTitleBatch } from "@/types";

export const useScriptGeneration = () => {
  const [titleCandidates, setTitleCandidates] =
    useState<ComedyTitleBatch | null>(null);
  const [singleTitleCandidate, setSingleTitleCandidate] = useState<{
    title: any;
    referenceInfo: string;
    searchResults: Record<string, any>;
  } | null>(null);
  const [generatingAction, setGeneratingAction] = useState<
    "approve" | "regenerate" | null
  >(null);
  const [themes, setThemes] = useState<string[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<string | null>(null);

  const {
    mode,
    currentStep,
    inputText,
    model,
    temperature,
    generatedTitle,
    generatedOutline,
    generatedScript,
    youtubeMetadata,
    referenceInfo,
    isAutoMode,
    savedFilePath,
    isGenerating,
    progress,
    statusMessage,
    setCurrentStep,
    setInputText,
    setModel,
    setTemperature,
    setGeneratedTitle,
    setGeneratedOutline,
    setGeneratedScript,
    setYoutubeMetadata,
    setReferenceInfo,
    setSearchResults,
    setAutoMode,
    setSavedFilePath,
    setGenerating,
    setProgress,
    setStatusMessage,
    setError,
    resetToInput,
  } = useScriptStore();

  const titleHandlers = useScriptTitleHandlers(
    setGenerating,
    setError,
    setTitleCandidates,
    setSingleTitleCandidate,
    setGeneratedTitle,
    setReferenceInfo,
    setSearchResults,
    setCurrentStep,
    setInputText,
    setStatusMessage,
    mode,
    inputText,
    model,
    temperature,
    titleCandidates,
    singleTitleCandidate
  );

  const generationHandlers = useScriptGenerationHandlers(
    setGenerating,
    setError,
    setStatusMessage,
    setProgress,
    setGeneratedOutline,
    setGeneratedScript,
    setCurrentStep,
    setGeneratingAction,
    setYoutubeMetadata,
    setSavedFilePath,
    mode,
    generatedTitle,
    generatedOutline,
    referenceInfo,
    model,
    temperature,
    isAutoMode
  );

  const { handleRegenerateTitle, handleRegenerateOutline } =
    useScriptRegenerateHandlers(
      setGeneratedTitle,
      setSingleTitleCandidate,
      setGeneratedOutline,
      setYoutubeMetadata,
      setCurrentStep,
      setGeneratingAction,
      titleHandlers,
      generationHandlers
    );

  const { handleAutoGenerateScript } = useAutoScriptGeneration(
    setGenerating,
    setError,
    setStatusMessage,
    setProgress,
    setGeneratedTitle,
    setGeneratedOutline,
    setGeneratedScript,
    setYoutubeMetadata,
    setSavedFilePath,
    setCurrentStep,
    mode,
    inputText,
    model,
    temperature
  );

  const { handleAutoGenerateFromTitle } = useAutoFromTitleGeneration(
    setGenerating,
    setError,
    setStatusMessage,
    setProgress,
    setGeneratedOutline,
    setGeneratedScript,
    setYoutubeMetadata,
    setSavedFilePath,
    setCurrentStep,
    mode,
    model,
    temperature
  );

  const handleResetToInput = () => {
    setTitleCandidates(null);
    setSingleTitleCandidate(null);
    setThemes([]);
    setSelectedTheme(null);
    setSavedFilePath(null);
    resetToInput();
  };

  // タイトル選択時の処理（常に手動）
  const handleSelectTitleCandidateWithAuto = async (candidateId: number) => {
    if (!titleCandidates) return;

    const selected = titleCandidates.titles.find((t) => t.id === candidateId);
    if (!selected) return;

    const comedyTitle = {
      title: selected.title,
      mode: "comedy" as const,
      theme: selected.situation,
      clickbait_elements: [
        selected.hook_pattern,
        selected.chaos_element,
        selected.expected_conflict,
      ],
    };

    setGeneratedTitle(comedyTitle);
    setInputText(selected.situation);
    setTitleCandidates(null);

    // タイトル選択は常に手動で、タイトル確認画面へ遷移
    setCurrentStep("title");
    toast.success("タイトルを選択しました！");
  };

  // 自由入力からのタイトル選択時の処理（常に手動）
  const handleSelectSingleTitleWithAuto = () => {
    if (!singleTitleCandidate) return;

    setGeneratedTitle(singleTitleCandidate.title);
    setReferenceInfo(singleTitleCandidate.referenceInfo);
    setSearchResults(singleTitleCandidate.searchResults);
    setSingleTitleCandidate(null);

    // タイトル選択は常に手動で、タイトル確認画面へ遷移
    setCurrentStep("title");
    toast.success("タイトルを選択しました！");
  };

  const handleGenerateThemes = async () => {
    const generatedThemes = await titleHandlers.handleGenerateThemes();
    if (generatedThemes.length > 0) {
      setThemes(generatedThemes);
    }
  };

  const handleThemeSelect = async (theme: string) => {
    setSelectedTheme(theme);
    setInputText(theme);
    // テーマ選択モードでは常にタイトル候補を表示
    setStatusMessage("タイトルを生成しています。");
    await titleHandlers.handleGenerateTitlesFromTheme(theme);
  };

  const handleCustomThemeSubmit = async (theme: string) => {
    setSelectedTheme(theme);
    setInputText(theme);
    // テーマ選択モードでは常にタイトル候補を表示
    setStatusMessage("タイトルを生成しています。");
    await titleHandlers.handleGenerateTitlesFromTheme(theme);
  };

  const { handleLoadTestData } = useScriptTestData(
    setGeneratedTitle,
    setGeneratedOutline,
    setGeneratedScript,
    setReferenceInfo,
    setSearchResults,
    setCurrentStep
  );

  return {
    ...createScriptGenerationReturn(
      titleCandidates,
      singleTitleCandidate,
      generatingAction,
      mode,
      currentStep,
      inputText,
      model,
      temperature,
      generatedTitle,
      generatedOutline,
      generatedScript,
      youtubeMetadata,
      isGenerating,
      progress,
      statusMessage,
      setInputText,
      setModel,
      setTemperature,
      setTitleCandidates,
      setSingleTitleCandidate,
      titleHandlers,
      generationHandlers,
      handleRegenerateTitle,
      handleRegenerateOutline,
      handleResetToInput,
      handleLoadTestData
    ),
    themes,
    selectedTheme,
    handleGenerateThemes,
    handleThemeSelect,
    handleCustomThemeSubmit,
    isAutoMode,
    savedFilePath,
    setAutoMode,
    handleAutoGenerateScript,
    handleSelectTitleCandidate: handleSelectTitleCandidateWithAuto,
    handleSelectSingleTitle: handleSelectSingleTitleWithAuto,
  };
};
