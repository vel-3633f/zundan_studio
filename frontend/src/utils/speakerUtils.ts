export const getSpeakerName = (speaker: string) => {
  switch (speaker) {
    case "zundamon":
      return "ずんだもん";
    case "metan":
      return "四国めたん";
    case "tsumugi":
      return "つむぎ";
    case "narrator":
      return "ナレーター";
    default:
      return speaker;
  }
};

export const getExpressionLabel = (expression?: string) => {
  const labels: Record<string, string> = {
    happy: "嬉しい",
    sad: "悲しい",
    angry: "怒り",
    surprised: "驚き",
    thinking: "考え中",
    worried: "心配",
    excited: "興奮",
    normal: "通常",
    sick: "病気",
  };
  return labels[expression || "normal"] || expression || "通常";
};

