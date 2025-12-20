// 共通型定義

// === 生成モード ===
export type ScriptMode = "food" | "comedy";

export interface ConversationLine {
  speaker: string;
  text: string;
  text_for_voicevox?: string;
  expression?: string;
  background?: string;
}

export interface VideoGenerationRequest {
  conversations: ConversationLine[];
  enable_subtitles?: boolean;
  conversation_mode?: string;
  sections?: VideoSection[];
  speed?: number;
  pitch?: number;
  intonation?: number;
}

export interface VideoGenerationResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface VideoStatusResponse {
  task_id: string;
  status: string;
  progress: number;
  message?: string;
  result?: {
    video_path?: string;
    status?: string;
    message?: string;
  };
  error?: string;
}

// === 共通セクション定義 ===
export interface SectionDefinition {
  section_key: string;
  section_name: string;
  purpose: string;
  content_summary: string;
  min_lines: number;
  max_lines: number;
  fixed_background?: string | null;
}

// === 食べ物モード ===
export interface FoodTitle {
  title: string;
  mode: ScriptMode;
  food_name: string;
  hook_phrase: string;
}

export interface FoodOutline {
  title: string;
  mode: ScriptMode;
  food_name: string;
  story_summary: string;
  sections: SectionDefinition[];
}

export interface FoodScript {
  title: string;
  mode: ScriptMode;
  food_name: string;
  estimated_duration: string;
  sections: VideoSection[];
  all_segments: ConversationSegment[];
}

// === お笑いモード ===
export interface CharacterMood {
  zundamon: number;
  metan: number;
  tsumugi: number;
}

export interface ComedyTitle {
  title: string;
  mode: ScriptMode;
  theme: string;
  clickbait_elements: string[];
}

export interface ComedyTitleCandidate {
  id: number;
  title: string;
  hook_pattern: string;
  situation: string;
  chaos_element: string;
  expected_conflict: string;
}

export interface ComedyTitleBatch {
  titles: ComedyTitleCandidate[];
}

export interface ComedyOutline {
  title: string;
  mode: ScriptMode;
  theme: string;
  story_summary: string;
  character_moods: CharacterMood;
  forced_ending_type: string;
  sections: SectionDefinition[];
}

export interface ComedyScript {
  title: string;
  mode: ScriptMode;
  theme: string;
  estimated_duration: string;
  character_moods: CharacterMood;
  sections: VideoSection[];
  all_segments: ConversationSegment[];
  ending_type: string;
}

// === 旧型定義（後方互換性のため保持） ===
export interface StoryOutline {
  title: string;
  food_name: string;
  hook_content: string;
  background_content: string;
  daily_content: string;
  honeymoon_content: string;
  deterioration_content: string[];
  crisis_content: string;
  learning_content: string;
  recovery_content: string;
}

export interface OutlineRequest {
  food_name: string;
  model?: string;
  temperature?: number;
}

export interface OutlineResponse {
  outline: StoryOutline;
  search_results: Record<string, any>;
  reference_info: string;
  model: string;
  temperature: number;
}

export interface ConversationSegment {
  speaker: string;
  text: string;
  text_for_voicevox: string;
  expression: string;
  visible_characters: string[];
  character_expressions: Record<string, string>;
  display_item?: string;
}

export interface VideoSection {
  section_name: string;
  section_key?: string;
  scene_background: string;
  bgm_id: string;
  bgm_volume: number;
  segments: ConversationSegment[];
}

export interface FoodOverconsumptionScript {
  title: string;
  food_name: string;
  estimated_duration: string;
  sections: VideoSection[];
  all_segments: ConversationSegment[];
}

export interface SectionRequest {
  outline: StoryOutline;
  food_name: string;
  reference_info: string;
  model: string;
  temperature: number;
  model_config: Record<string, any>;
}

export interface Background {
  id: string;
  name: string;
  path: string;
}

export interface Item {
  id: string;
  name: string;
  path: string;
  description?: string;
}

export interface Food {
  id: number;
  name: string;
  created_at?: string;
}

export interface FoodCreateRequest {
  name: string;
}

// === 統合API型定義 ===
export interface TitleRequest {
  mode: ScriptMode;
  input_text: string;
  model?: string;
  temperature?: number;
}

export interface TitleResponse {
  title: FoodTitle | ComedyTitle;
  reference_info: string;
  search_results: Record<string, any>;
  model: string;
  temperature: number;
}

export interface UnifiedOutlineRequest {
  mode: ScriptMode;
  title_data: FoodTitle | ComedyTitle;
  reference_info?: string;
  model?: string;
  temperature?: number;
}

export interface UnifiedOutlineResponse {
  outline: FoodOutline | ComedyOutline;
  model: string;
  temperature: number;
}

export interface ScriptRequest {
  mode: ScriptMode;
  outline_data: FoodOutline | ComedyOutline;
  reference_info?: string;
  model?: string;
  temperature?: number;
}

export interface ScriptResponse {
  script: FoodScript | ComedyScript;
}

export interface FullScriptRequest {
  mode: ScriptMode;
  input_text: string;
  model?: string;
  temperature?: number;
}

export interface FullScriptResponse {
  script: FoodScript | ComedyScript;
}
