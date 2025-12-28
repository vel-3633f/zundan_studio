export const useScriptRegenerateHandlers = (
  setGeneratedTitle: (title: any) => void,
  setSingleTitleCandidate: (value: any) => void,
  setGeneratedOutline: (outline: any) => void,
  setCurrentStep: (step: "input" | "title" | "outline" | "script") => void,
  setGeneratingAction: (action: "approve" | "regenerate" | null) => void,
  titleHandlers: any,
  generationHandlers: any
) => {
  const handleRegenerateTitle = async () => {
    setGeneratedTitle(null);
    setSingleTitleCandidate(null);
    setCurrentStep("input");
    setGeneratingAction("regenerate");
    await titleHandlers.handleGenerateTitle();
  };

  const handleRegenerateOutline = async () => {
    setGeneratedOutline(null);
    setGeneratingAction("regenerate");
    await generationHandlers.handleGenerateOutline();
  };

  return { handleRegenerateTitle, handleRegenerateOutline };
};

