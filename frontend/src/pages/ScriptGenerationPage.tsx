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
import SingleTitleCandidateSection from "@/components/script/SingleTitleCandidateSection";
import OutlineSection from "@/components/script/OutlineSection";
import ScriptSection from "@/components/script/ScriptSection";
import TestModeButton from "@/components/script/TestModeButton";
import type { ComedyTitleBatch, ComedyTitle } from "@/types";
import {
  mockFoodTitle,
  mockFoodOutline,
  mockFoodScript,
  mockComedyTitle,
  mockComedyOutline,
  mockComedyScript,
  mockReferenceInfo,
  mockSearchResults,
} from "@/utils/mockData";

const ScriptGenerationPage = () => {
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
      // エラーメッセージを適切に抽出
      let errorMsg = "タイトル量産に失敗しました";

      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail
            .map((e: any) => `${e.loc.join(".")}: ${e.msg}`)
            .join(", ");
        } else if (typeof err.response.data.detail === "string") {
          errorMsg = err.response.data.detail;
        }
      }

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
      clickbait_elements: [
        selected.hook_pattern,
        selected.chaos_element,
        selected.expected_conflict,
      ],
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
    setStatusMessage("タイトルを生成中...");

    try {
      const result = await scriptApi.generateTitle({
        mode,
        input_text: inputText,
        model,
        temperature,
      });

      // タイトルを候補として保存（自動的に次のステップに進まない）
      setSingleTitleCandidate({
        title: result.title,
        referenceInfo: result.reference_info,
        searchResults: result.search_results,
      });

      toast.success("タイトルを生成しました！選択して次へ進んでください");
    } catch (err: any) {
      // エラーメッセージを適切に抽出
      let errorMsg = "タイトル生成に失敗しました";

      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail
            .map((e: any) => `${e.loc.join(".")}: ${e.msg}`)
            .join(", ");
        } else if (typeof err.response.data.detail === "string") {
          errorMsg = err.response.data.detail;
        }
      }

      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Title generation error:", err);
    } finally {
      setGenerating(false);
    }
  };

  // === 単一タイトル選択 ===
  const handleSelectSingleTitle = () => {
    if (!singleTitleCandidate) return;

    setGeneratedTitle(singleTitleCandidate.title);
    setReferenceInfo(singleTitleCandidate.referenceInfo);
    setSearchResults(singleTitleCandidate.searchResults);
    setCurrentStep("title");
    setSingleTitleCandidate(null);
    toast.success("タイトルを選択しました！");
  };

  // === アウトライン生成 ===
  const handleGenerateOutline = async () => {
    if (!generatedTitle) {
      toast.error("タイトルが生成されていません");
      return;
    }

    setGenerating(true);
    setGeneratingAction("approve");
    setError(null);
    setStatusMessage("アウトラインを生成中...");

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
      // エラーメッセージを適切に抽出
      let errorMsg = "アウトライン生成に失敗しました";

      if (err.response?.data?.detail) {
        // detailが配列の場合（FastAPIのバリデーションエラー）
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail
            .map((e: any) => `${e.loc.join(".")}: ${e.msg}`)
            .join(", ");
        } else if (typeof err.response.data.detail === "string") {
          errorMsg = err.response.data.detail;
        }
      }

      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Outline generation error:", err);
    } finally {
      setGenerating(false);
      setGeneratingAction(null);
    }
  };

  // === 台本生成 ===
  const handleGenerateScript = async () => {
    if (!generatedOutline) {
      toast.error("アウトラインが生成されていません");
      return;
    }

    setGenerating(true);
    setGeneratingAction("approve");
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
      // エラーメッセージを適切に抽出
      let errorMsg = "台本生成に失敗しました";

      if (err.response?.data?.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail
            .map((e: any) => `${e.loc.join(".")}: ${e.msg}`)
            .join(", ");
        } else if (typeof err.response.data.detail === "string") {
          errorMsg = err.response.data.detail;
        }
      }

      toast.error(errorMsg);
      setError(errorMsg);
      console.error("Script generation error:", err);
    } finally {
      setGenerating(false);
      setGeneratingAction(null);
    }
  };

  // === タイトル再生成 ===
  const handleRegenerateTitle = async () => {
    setGeneratedTitle(null);
    setSingleTitleCandidate(null);
    setCurrentStep("input");
    setGeneratingAction("regenerate");
    await handleGenerateTitle();
  };

  // === アウトライン再生成 ===
  const handleRegenerateOutline = async () => {
    setGeneratedOutline(null);
    setGeneratingAction("regenerate");
    await handleGenerateOutline();
  };

  // === モード変更 ===
  const handleModeChange = (newMode: typeof mode) => {
    if (currentStep !== "input" || titleCandidates || singleTitleCandidate) {
      if (
        !confirm(
          "モードを変更すると、現在の生成データがリセットされます。よろしいですか？"
        )
      ) {
        return;
      }
    }
    setMode(newMode);
    setTitleCandidates(null);
    setSingleTitleCandidate(null);
    resetToInput();
  };

  // === リセット処理のオーバーライド ===
  const handleResetToInput = () => {
    setTitleCandidates(null);
    setSingleTitleCandidate(null);
    resetToInput();
  };

  // === テストデータ読み込み ===
  const handleLoadTestData = (step: "title" | "outline" | "script") => {
    try {
      if (mode === "food") {
        // 食べ物モードのテストデータ
        if (step === "title") {
          setGeneratedTitle(mockFoodTitle);
          setReferenceInfo(mockReferenceInfo);
          setSearchResults(mockSearchResults);
          setCurrentStep("title");
          toast.success("テストデータ（タイトル）を読み込みました");
        } else if (step === "outline") {
          setGeneratedTitle(mockFoodTitle);
          setGeneratedOutline(mockFoodOutline);
          setReferenceInfo(mockReferenceInfo);
          setSearchResults(mockSearchResults);
          setCurrentStep("outline");
          toast.success("テストデータ（アウトライン）を読み込みました");
        } else if (step === "script") {
          setGeneratedTitle(mockFoodTitle);
          setGeneratedOutline(mockFoodOutline);
          setGeneratedScript(mockFoodScript);
          setReferenceInfo(mockReferenceInfo);
          setSearchResults(mockSearchResults);
          setCurrentStep("script");
          toast.success("テストデータ（完成台本）を読み込みました");
        }
      } else {
        // お笑いモードのテストデータ
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
      }
    } catch (error) {
      console.error("Test data load error:", error);
      toast.error("テストデータの読み込みに失敗しました");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* ヘッダー */}
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              動画台本生成
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {mode === "food"
                ? "食べ物を食べすぎるとどうなるのか？をテーマに、ずんだもんたちが面白く解説する動画脚本を作成します"
                : "ずんだもん・めたん・つむぎの3人が、バカバカしい漫談を繰り広げる動画脚本を作成します"}
            </p>
          </div>
          <TestModeButton
            mode={mode}
            currentStep={currentStep}
            disabled={isGenerating}
            onLoadTestData={handleLoadTestData}
          />
        </div>
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
      {currentStep === "input" &&
        !titleCandidates &&
        !singleTitleCandidate && (
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

      {/* タイトル候補選択（お笑いモード・ランダム生成） */}
      {currentStep === "input" && titleCandidates && (
        <TitleCandidatesSection
          titleBatch={titleCandidates}
          isGenerating={isGenerating}
          onSelectTitle={handleSelectTitleCandidate}
          onRegenerate={handleGenerateRandomTitles}
          onBack={() => setTitleCandidates(null)}
        />
      )}

      {/* 単一タイトル候補選択（通常生成） */}
      {currentStep === "input" && singleTitleCandidate && (
        <SingleTitleCandidateSection
          mode={mode}
          title={singleTitleCandidate.title}
          isGenerating={isGenerating}
          onSelectTitle={handleSelectSingleTitle}
          onRegenerate={handleRegenerateTitle}
          onBack={() => setSingleTitleCandidate(null)}
        />
      )}

      {/* タイトル確認 */}
      {currentStep === "title" && generatedTitle && (
        <TitleSection
          mode={mode}
          title={generatedTitle}
          isGenerating={isGenerating}
          isApprovingLoading={isGenerating && generatingAction === "approve"}
          isRegeneratingLoading={isGenerating && generatingAction === "regenerate"}
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
          isApprovingLoading={isGenerating && generatingAction === "approve"}
          isRegeneratingLoading={isGenerating && generatingAction === "regenerate"}
          onApprove={handleGenerateScript}
          onRegenerate={handleRegenerateOutline}
        />
      )}

      {/* 台本生成中のローディング表示 */}
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
