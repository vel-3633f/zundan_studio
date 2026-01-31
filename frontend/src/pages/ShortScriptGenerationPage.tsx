import ProgressBar from "@/components/ProgressBar";
import StepIndicator from "@/components/script/StepIndicator";
import InputSection from "@/components/script/InputSection";
import TitleCandidatesSection from "@/components/script/TitleCandidatesSection";
import TitleSection from "@/components/script/TitleSection";
import ScriptSection from "@/components/script/ScriptSection";
import { useShortScriptGeneration } from "@/hooks/useShortScriptGeneration";
import { Zap } from "lucide-react";

const ShortScriptGenerationPage = () => {
  const {
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
    setInputText,
    setModel,
    setTemperature,
    setTitleCandidates,
    handleGenerateTitles,
    handleSelectTitleCandidate,
    handleRegenerateTitles,
    handleResetToInput,
  } = useShortScriptGeneration();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <Zap className="h-8 w-8 text-yellow-500" />
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                ショート動画台本生成
              </h1>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              TikTok・YouTube Shorts向けのお笑い漫談台本を生成します
            </p>
          </div>
        </div>
      </div>

      <StepIndicator 
        currentStep={
          currentStep === "script" 
            ? "script" 
            : titleCandidates 
            ? "title" 
            : "input"
        }
        mode="short"
      />

      {currentStep === "input" && !titleCandidates && (
        <InputSection
          mode="comedy"
          inputText={inputText}
          model={model}
          temperature={temperature}
          isGenerating={isGenerating}
          onInputTextChange={setInputText}
          onModelChange={setModel}
          onTemperatureChange={setTemperature}
          onSubmit={handleGenerateTitles}
        />
      )}

      {currentStep === "input" && titleCandidates && !isGenerating && (
        <TitleCandidatesSection
          titleBatch={titleCandidates}
          isGenerating={isGenerating}
          onSelectTitle={handleSelectTitleCandidate}
          onRegenerate={handleRegenerateTitles}
          onBack={() => setTitleCandidates(null)}
        />
      )}

      {isGenerating && currentStep === "script" && (
        <div className="animate-fade-in">
          <ProgressBar
            progress={progress * 100}
            message={statusMessage}
            variant="default"
          />
        </div>
      )}

      {currentStep === "script" && generatedScript && !isGenerating && (
        <ScriptSection mode="comedy" script={generatedScript} />
      )}

      {currentStep !== "input" && !isGenerating && (
        <div className="flex justify-center pt-4">
          <button
            onClick={handleResetToInput}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
          >
            最初からやり直す
          </button>
        </div>
      )}
    </div>
  );
};

export default ShortScriptGenerationPage;
