import { useState } from "react";
import { useScriptStore } from "@/stores/scriptStore";
import { useScriptTitleHandlers } from "./useScriptTitleHandlers";
import { useScriptGenerationHandlers } from "./useScriptGenerationHandlers";
import { useScriptRegenerateHandlers } from "./useScriptRegenerateHandlers";
import { useScriptTestData } from "./useScriptTestData";
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
    mode,
    generatedTitle,
    generatedOutline,
    referenceInfo,
    model,
    temperature
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

  const handleResetToInput = () => {
    setTitleCandidates(null);
    setSingleTitleCandidate(null);
    setThemes([]);
    setSelectedTheme(null);
    resetToInput();
  };

  const handleGenerateThemes = async () => {
    const generatedThemes = await titleHandlers.handleGenerateThemes();
    if (generatedThemes.length > 0) {
      setThemes(generatedThemes);
    }
  };

  const handleThemeSelect = async (theme: string) => {
    setSelectedTheme(theme);
    setStatusMessage("タイトルを生成しています。");
    await titleHandlers.handleGenerateTitlesFromTheme(theme);
  };

  const handleCustomThemeSubmit = async (theme: string) => {
    setSelectedTheme(theme);
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
  };
};
