// 共通型定義

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
