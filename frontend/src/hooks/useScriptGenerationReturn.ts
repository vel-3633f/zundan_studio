import type { ComedyTitleBatch } from "@/types";

export const createScriptGenerationReturn = (
  titleCandidates: ComedyTitleBatch | null,
  singleTitleCandidate: {
    title: any;
    referenceInfo: string;
    searchResults: Record<string, any>;
  } | null,
  generatingAction: "approve" | "regenerate" | null,
  mode: "comedy",
  currentStep: "input" | "title" | "outline" | "script",
  inputText: string,
  model: string,
  temperature: number,
  generatedTitle: any,
  generatedOutline: any,
  generatedScript: any,
  isGenerating: boolean,
  progress: number,
  statusMessage: string,
  setInputText: (text: string) => void,
  setModel: (model: string) => void,
  setTemperature: (temp: number) => void,
  setTitleCandidates: (value: ComedyTitleBatch | null) => void,
  setSingleTitleCandidate: (value: {
    title: any;
    referenceInfo: string;
    searchResults: Record<string, any>;
  } | null) => void,
  titleHandlers: any,
  generationHandlers: any,
  handleRegenerateTitle: () => Promise<void>,
  handleRegenerateOutline: () => Promise<void>,
  handleResetToInput: () => void,
  handleLoadTestData: (step: "title" | "outline" | "script") => void
) => ({
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
  isGenerating,
  progress,
  statusMessage,
  setInputText,
  setModel,
  setTemperature,
  setTitleCandidates,
  setSingleTitleCandidate,
  handleGenerateRandomTitles: titleHandlers.handleGenerateRandomTitles,
  handleSelectTitleCandidate: titleHandlers.handleSelectTitleCandidate,
  handleGenerateTitle: titleHandlers.handleGenerateTitle,
  handleSelectSingleTitle: titleHandlers.handleSelectSingleTitle,
  handleGenerateOutline: generationHandlers.handleGenerateOutline,
  handleGenerateScript: generationHandlers.handleGenerateScript,
  handleRegenerateTitle,
  handleRegenerateOutline,
  handleResetToInput,
  handleLoadTestData,
});

