import { useState } from "react";
import toast from "react-hot-toast";
import ProgressBar from "@/components/ProgressBar";
import { useScriptStore } from "@/stores/scriptStore";
import { scriptApi } from "@/api/scripts";
import ModeSelector from "@/components/script/ModeSelector";
import StepIndicator from "@/components/script/StepIndicator";
import InputSection from "@/components/script/InputSection";
import TitleSection from "@/components/script/TitleSection";
import TitleCandidatesSection from "@/components/script/TitleCandidatesSection";
import OutlineSection from "@/components/script/OutlineSection";
import ScriptSection from "@/components/script/ScriptSection";
import type { ComedyTitleBatch, ComedyTitle } from "@/types";

const ScriptGenerationPage = () => {
  const [titleCandidates, setTitleCandidates] =
    useState<ComedyTitleBatch | null>(null);

  const {
    mode,
    currentStep,
    inputText,
    model,
    temperature,
    generatedTitle,
    generatedOutline,
    generatedScript,
    referenceInfo,
    isGenerating,
    progress,
    statusMessage,
    setMode,
    setCurrentStep,
    setInputText,
    setModel,
    setTemperature,
    setGeneratedTitle,
    setGeneratedOutline,
    setGeneratedScript,
    setReferenceInfo,
    setSearchResults,
    setGenerating,
    setProgress,
    setStatusMessage,
    setError,
    resetToInput,
  } = useScriptStore();

  // === ランダムタイトル量産（お笑いモード専用） ===
  const handleGenerateRandomTitles = async () => {
    setGenerating(true);
    setError(null);

    try {
      const result = await scriptApi.generateComedyTitlesBatch();
      setTitleCandidates(result);
      toast.success(`${result.titles.length}個のタイトルを生成しました！`);
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || "タイトル量産に失敗しました";
      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Random titles generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  // === タイトル候補選択 ===
  const handleSelectTitleCandidate = (candidateId: number) => {
    if (!titleCandidates) return;

    const selected = titleCandidates.titles.find((t) => t.id === candidateId);
    if (!selected) return;

    // ComedyTitleオブジェクトを作成
    const comedyTitle: ComedyTitle = {
      title: selected.title,
      mode: "comedy",
      theme: selected.situation,
      clickbait_elements: [selected.hook_pattern, selected.chaos_element],
    };

    setGeneratedTitle(comedyTitle);
    setInputText(selected.situation); // テーマを設定
    setCurrentStep("title");
    setTitleCandidates(null); // 候補リストをクリア
    toast.success("タイトルを選択しました！");
  };

  // === タイトル生成 ===
  const handleGenerateTitle = async () => {
    if (!inputText.trim()) {
      toast.error(
        mode === "food"
          ? "食べ物の名前を入力してください"
          : "漫談のテーマを入力してください"
      );
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const result = await scriptApi.generateTitle({
        mode,
        input_text: inputText,
        model,
        temperature,
      });

      setGeneratedTitle(result.title);
      setReferenceInfo(result.reference_info);
      setSearchResults(result.search_results);
      setCurrentStep("title");

      toast.success("タイトルを生成しました！");
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || "タイトル生成に失敗しました";
      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Title generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  // === アウトライン生成 ===
  const handleGenerateOutline = async () => {
    if (!generatedTitle) {
      toast.error("タイトルが生成されていません");
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const result = await scriptApi.generateOutline({
        mode,
        title_data: generatedTitle,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedOutline(result.outline);
      setCurrentStep("outline");

      toast.success("アウトラインを生成しました！");
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.detail || "アウトライン生成に失敗しました";
      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Outline generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  // === 台本生成 ===
  const handleGenerateScript = async () => {
    if (!generatedOutline) {
      toast.error("アウトラインが生成されていません");
      return;
    }

    setGenerating(true);
    setError(null);
    setProgress(0);
    setStatusMessage("台本を生成中...");

    try {
      const result = await scriptApi.generateScript({
        mode,
        outline_data: generatedOutline,
        reference_info: referenceInfo,
        model,
        temperature,
      });

      setGeneratedScript(result.script);
      setCurrentStep("script");
      setProgress(1);
      setStatusMessage("完了！");

      toast.success("台本を生成しました！");
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || "台本生成に失敗しました";
      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Script generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  // === タイトル再生成 ===
  const handleRegenerateTitle = async () => {
    setGeneratedTitle(null);
    await handleGenerateTitle();
  };

  // === アウトライン再生成 ===
  const handleRegenerateOutline = async () => {
    setGeneratedOutline(null);
    await handleGenerateOutline();
  };

  // === モード変更 ===
  const handleModeChange = (newMode: typeof mode) => {
    if (currentStep !== "input") {
      if (
        !confirm(
          "モードを変更すると、現在の生成データがリセットされます。よろしいですか？"
        )
      ) {
        return;
      }
    }
    setMode(newMode);
    resetToInput();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* ヘッダー */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          動画台本生成
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {mode === "food"
            ? "食べ物を食べすぎるとどうなるのか？をテーマに、ずんだもんたちが面白く解説する動画脚本を作成します"
            : "ずんだもん・めたん・つむぎの3人が、バカバカしい漫談を繰り広げる動画脚本を作成します"}
        </p>
      </div>

      {/* モード選択 */}
      <ModeSelector
        mode={mode}
        onModeChange={handleModeChange}
        disabled={isGenerating}
      />

      {/* ステップインジケーター */}
      <StepIndicator currentStep={currentStep} />

      {/* 入力セクション */}
      {currentStep === "input" && !titleCandidates && (
        <InputSection
          mode={mode}
          inputText={inputText}
          model={model}
          temperature={temperature}
          isGenerating={isGenerating}
          onInputTextChange={setInputText}
          onModelChange={setModel}
          onTemperatureChange={setTemperature}
          onSubmit={handleGenerateTitle}
          onRandomGenerate={
            mode === "comedy" ? handleGenerateRandomTitles : undefined
          }
        />
      )}

      {/* タイトル候補選択（お笑いモード専用） */}
      {currentStep === "input" && titleCandidates && (
        <TitleCandidatesSection
          titleBatch={titleCandidates}
          isGenerating={isGenerating}
          onSelectTitle={handleSelectTitleCandidate}
          onRegenerate={handleGenerateRandomTitles}
        />
      )}

      {/* タイトル確認 */}
      {currentStep === "title" && generatedTitle && (
        <TitleSection
          mode={mode}
          title={generatedTitle}
          isGenerating={isGenerating}
          onApprove={handleGenerateOutline}
          onRegenerate={handleRegenerateTitle}
        />
      )}

      {/* アウトライン確認 */}
      {currentStep === "outline" && generatedOutline && (
        <OutlineSection
          mode={mode}
          outline={generatedOutline}
          isGenerating={isGenerating}
          onApprove={handleGenerateScript}
          onRegenerate={handleRegenerateOutline}
        />
      )}

      {/* 生成進捗 */}
      {isGenerating && currentStep === "script" && (
        <div className="animate-fade-in">
          <ProgressBar
            progress={progress * 100}
            message={statusMessage}
            variant="default"
          />
        </div>
      )}

      {/* 完成台本 */}
      {currentStep === "script" && generatedScript && !isGenerating && (
        <ScriptSection mode={mode} script={generatedScript} />
      )}

      {/* 最初からやり直すボタン */}
      {currentStep !== "input" && !isGenerating && (
        <div className="flex justify-center pt-4">
          <button
            onClick={resetToInput}
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
