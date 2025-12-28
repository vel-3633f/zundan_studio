import toast from "react-hot-toast";
import type {
  ConversationLine,
  VideoSection,
  ConversationSegment,
  JsonScriptData,
} from "@/types";

/**
 * JSONデータから使用されている背景画像名を抽出
 */
export const extractBackgroundNames = (jsonData: any): string[] => {
  const backgroundNames = new Set<string>();

  if (jsonData.sections && Array.isArray(jsonData.sections)) {
    jsonData.sections.forEach((section: any) => {
      if (section.scene_background) {
        backgroundNames.add(section.scene_background);
      }
    });
  }

  return Array.from(backgroundNames);
};

const speakerMap: Record<string, string> = {
  めたん: "metan",
  ずんだもん: "zundamon",
  つむぎ: "tsumugi",
  ナレーター: "narrator",
};

export const processJsonData = (
  jsonData: any,
  setConversations: (conversations: ConversationLine[]) => void,
  setSections: (sections: VideoSection[] | null) => void,
  setJsonScriptData: (data: JsonScriptData | null) => void
): boolean => {
  if (!jsonData.sections || !Array.isArray(jsonData.sections)) {
    toast.error("無効なJSON形式です。sections配列が見つかりません。");
    return false;
  }

  const videoSections: VideoSection[] = jsonData.sections.map(
    (section: any) => ({
      section_name: section.section_name || "",
      section_key: section.section_key,
      scene_background: section.scene_background || "",
      bgm_id: section.bgm_id || "none",
      bgm_volume: section.bgm_volume ?? 0,
      segments: section.segments || [],
    })
  );

  const conversationLines: ConversationLine[] = [];
  videoSections.forEach((section) => {
    section.segments.forEach((segment: ConversationSegment) => {
      const speakerKey = speakerMap[segment.speaker] || segment.speaker;

      conversationLines.push({
        speaker: speakerKey,
        text: segment.text,
        text_for_voicevox: segment.text_for_voicevox,
        expression: segment.expression || "normal",
        background: section.scene_background,
        section_name: section.section_name,
        section_key: section.section_key,
        scene_background: section.scene_background,
        bgm_id: section.bgm_id,
        bgm_volume: section.bgm_volume,
        visible_characters: segment.visible_characters,
        character_expressions: segment.character_expressions,
        voice_speed: segment.voice_speed,
        voice_pitch: segment.voice_pitch,
      });
    });
  });

  if (conversationLines.length === 0) {
    toast.error("会話データが見つかりませんでした。");
    return false;
  }

  const jsonScriptData: JsonScriptData = {
    title: jsonData.title || "",
    mode: jsonData.mode || "",
    estimated_duration: jsonData.estimated_duration,
    theme: jsonData.theme,
    character_moods: jsonData.character_moods,
    sections: videoSections,
  };

  setConversations(conversationLines);
  setSections(videoSections);
  setJsonScriptData(jsonScriptData);

  toast.success(`${conversationLines.length}件の会話を読み込みました`);
  return true;
};

