import type {
  ComedyTitle,
  ComedyOutline,
  ComedyScript,
  ComedyTitleBatch,
} from "@/types";

// === お笑いモード：モックデータ ===

export const mockComedyTitleBatch: ComedyTitleBatch = {
  candidates: [
    {
      title: "【衝撃】ずんだもんが「塩」と「砂糖」を間違えて料理したら大惨事www",
      theme: "調味料の取り違え",
      clickbait_elements: ["衝撃", "大惨事", "www"],
      hook_pattern: "absurd_situation",
    },
    {
      title: "【検証】めたんが「透明な液体」を全部飲んでみた結果…まさかの展開に",
      theme: "透明な液体の飲み比べ",
      clickbait_elements: ["検証", "まさかの展開"],
      hook_pattern: "experiment_gone_wrong",
    },
    {
      title: "【悲報】つむぎが「白い粉」を見分けられなくて大変なことになったwww",
      theme: "白い粉の識別",
      clickbait_elements: ["悲報", "大変なこと", "www"],
      hook_pattern: "misunderstanding",
    },
  ],
};

export const mockComedyTitle: ComedyTitle = {
  title: "【衝撃】ずんだもんが「塩」と「砂糖」を間違えて料理したら大惨事www",
  theme: "調味料の取り違え",
  clickbait_elements: ["衝撃", "大惨事", "www"],
};

export const mockComedyOutline: ComedyOutline = {
  title: "【衝撃】ずんだもんが「塩」と「砂糖」を間違えて料理したら大惨事www",
  theme: "調味料の取り違え",
  story_summary:
    "ずんだもんが料理中に塩と砂糖を間違えて使ってしまい、めたんとつむぎを巻き込んだカオスな展開になる",
  character_moods: {
    zundamon: 85,
    metan: 45,
    tsumugi: 70,
  },
  ending_type: "unresolved_chaos",
  sections: [
    {
      section_key: "intro",
      section_name: "料理開始",
      purpose: "ずんだもんが料理を始める",
      content_summary: "ずんだもんが自信満々に料理を始める",
      min_lines: 5,
      max_lines: 8,
    },
    {
      section_key: "mistake",
      section_name: "取り違え発生",
      purpose: "塩と砂糖を間違える",
      content_summary: "ずんだもんが塩と砂糖を間違えて使う",
      min_lines: 8,
      max_lines: 12,
    },
    {
      section_key: "chaos",
      section_name: "カオス展開",
      purpose: "めたんとつむぎが巻き込まれる",
      content_summary: "めたんとつむぎが料理を食べて大騒ぎになる",
      min_lines: 10,
      max_lines: 15,
    },
    {
      section_key: "ending",
      section_name: "強制終了",
      purpose: "何も解決せずに終わる",
      content_summary: "誰も反省せず、カオスなまま終わる",
      min_lines: 5,
      max_lines: 8,
    },
  ],
};

export const mockComedyScript: ComedyScript = {
  title: "【衝撃】ずんだもんが「塩」と「砂糖」を間違えて料理したら大惨事www",
  theme: "調味料の取り違え",
  story_summary:
    "ずんだもんが料理中に塩と砂糖を間違えて使ってしまい、めたんとつむぎを巻き込んだカオスな展開になる",
  character_moods: {
    zundamon: 85,
    metan: 45,
    tsumugi: 70,
  },
  ending_type: "unresolved_chaos",
  estimated_duration: "3分30秒",
  sections: [
    {
      section_key: "intro",
      section_name: "料理開始",
      conversations: [
        {
          speaker: "zundamon",
          text: "今日は最高の料理を作るのだ！",
          text_for_voicevox: "きょうはさいこうのりょうりをつくるのだ！",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "excited",
            metan: "normal",
            tsumugi: "normal",
          },
          scene_background: "home_livingroom_morning",
          bgm_id: "maou_日常_piano25",
          bgm_volume: 0.3,
        },
        {
          speaker: "metan",
          text: "また料理？大丈夫なの？",
          text_for_voicevox: "またりょうり？だいじょうぶなの？",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "excited",
            metan: "worried",
            tsumugi: "normal",
          },
          scene_background: "home_livingroom_morning",
          bgm_id: "maou_日常_piano25",
          bgm_volume: 0.3,
        },
      ],
      background: "home_livingroom_morning",
    },
  ],
};

// モックの参照情報とサーチ結果（Comedy専用）
export const mockReferenceInfo = "";
export const mockSearchResults = {};
