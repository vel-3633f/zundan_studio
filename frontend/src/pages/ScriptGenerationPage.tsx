import ProgressBar from "@/components/ProgressBar";
import ModeSelector from "@/components/script/ModeSelector";
import StepIndicator from "@/components/script/StepIndicator";
import InputSection from "@/components/script/InputSection";
import TitleSection from "@/components/script/TitleSection";
import TitleCandidatesSection from "@/components/script/TitleCandidatesSection";
import SingleTitleCandidateSection from "@/components/script/SingleTitleCandidateSection";
import OutlineSection from "@/components/script/OutlineSection";
import ScriptSection from "@/components/script/ScriptSection";
import ProcessHistorySection from "@/components/script/ProcessHistorySection";
import AutoModeToggle from "@/components/script/AutoModeToggle";
import TestModeButton from "@/components/script/TestModeButton";
import { useScriptGeneration } from "@/hooks/useScriptGeneration";
import { useScriptStore } from "@/stores/scriptStore";
import Select from "@/components/Select";

const ScriptGenerationPage = () => {
  const { setMode } = useScriptStore();
  const {
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
    handleGenerateRandomTitles,
    handleSelectTitleCandidate,
    handleGenerateTitle,
    handleSelectSingleTitle,
    handleGenerateOutline,
    handleGenerateScript,
    handleRegenerateTitle,
    handleRegenerateOutline,
    handleResetToInput,
    handleLoadTestData,
    themes,
    selectedTheme,
    handleGenerateThemes,
    handleThemeSelect,
    handleCustomThemeSubmit,
    isAutoMode,
    savedFilePath,
    setAutoMode,
    handleAutoGenerateScript,
  } = useScriptGeneration();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              長尺動画台本生成
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {mode === "comedy"
                ? "ずんだもん・めたん・つむぎの3人が、バカバカしい漫談を繰り広げる動画脚本を作成します"
                : mode === "thought_experiment"
                ? "ずんだもん・めたん・つむぎの3人が、「もしも系」思考実験バラエティ動画の脚本を作成します"
                : "ずんだもん・めたん・つむぎの3人が、動画脚本を作成します"}
            </p>
            {currentStep === "input" && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  生成モード
                </label>
                <Select
                  value={mode}
                  onChange={(e) => setMode(e.target.value as "comedy" | "thought_experiment")}
                  disabled={isGenerating}
                  options={[
                    { value: "comedy", label: "お笑いモード" },
                    { value: "thought_experiment", label: "思考実験モード" },
                  ]}
                />
              </div>
            )}
          </div>
          <TestModeButton
            mode={mode}
            currentStep={currentStep}
            disabled={isGenerating}
            onLoadTestData={handleLoadTestData}
          />
        </div>
      </div>

      <StepIndicator currentStep={currentStep} />

      {/* 自動モード切り替え - 常に表示 */}
      {currentStep === "input" && (
        <AutoModeToggle
          isAutoMode={isAutoMode}
          onToggle={setAutoMode}
          disabled={isGenerating}
        />
      )}

      {currentStep === "input" && !titleCandidates && !singleTitleCandidate && (
        <InputSection
          mode={mode}
          inputText={inputText}
          model={model}
          temperature={temperature}
          isGenerating={isGenerating}
          isAutoMode={isAutoMode}
          onInputTextChange={setInputText}
          onModelChange={setModel}
          onTemperatureChange={setTemperature}
          onSubmit={handleGenerateTitle}
          onAutoSubmit={handleAutoGenerateScript}
          onAutoModeToggle={setAutoMode}
          onRandomGenerate={
            mode === "comedy" ? handleGenerateRandomTitles : undefined
          }
          themes={themes}
          selectedTheme={selectedTheme}
          onGenerateThemes={handleGenerateThemes}
          onThemeSelect={handleThemeSelect}
          onCustomThemeSubmit={handleCustomThemeSubmit}
        />
      )}

      {currentStep === "input" && titleCandidates && (
        <TitleCandidatesSection
          titleBatch={titleCandidates}
          isGenerating={isGenerating}
          onSelectTitle={handleSelectTitleCandidate}
          onRegenerate={handleGenerateRandomTitles}
          onBack={() => setTitleCandidates(null)}
        />
      )}

      {currentStep === "input" && singleTitleCandidate && (
        <SingleTitleCandidateSection
          title={singleTitleCandidate.title}
          isGenerating={isGenerating}
          onSelectTitle={handleSelectSingleTitle}
          onRegenerate={handleRegenerateTitle}
          onBack={() => setSingleTitleCandidate(null)}
        />
      )}

      {currentStep === "title" && generatedTitle && (
        <TitleSection
          title={generatedTitle}
          isGenerating={isGenerating}
          isApprovingLoading={isGenerating && generatingAction === "approve"}
          isRegeneratingLoading={
            isGenerating && generatingAction === "regenerate"
          }
          onApprove={handleGenerateOutline}
          onRegenerate={handleRegenerateTitle}
        />
      )}

      {currentStep === "outline" && generatedOutline && (
        <OutlineSection
          outline={generatedOutline}
          youtubeMetadata={youtubeMetadata}
          isGenerating={isGenerating}
          isApprovingLoading={isGenerating && generatingAction === "approve"}
          isRegeneratingLoading={
            isGenerating && generatingAction === "regenerate"
          }
          onApprove={handleGenerateScript}
          onRegenerate={handleRegenerateOutline}
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
        <>
          {/* 自動モード時は過程を表示 */}
          {isAutoMode && (
            <ProcessHistorySection
              title={generatedTitle}
              outline={generatedOutline}
              youtubeMetadata={youtubeMetadata}
            />
          )}
          
          <ScriptSection
            mode={mode}
            script={generatedScript}
            savedFilePath={savedFilePath}
            isAutoMode={isAutoMode}
          />
        </>
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

export default ScriptGenerationPage;
