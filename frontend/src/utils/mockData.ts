import type {
  FoodTitle,
  FoodOutline,
  FoodScript,
  ComedyTitle,
  ComedyOutline,
  ComedyScript,
  ComedyTitleBatch,
} from "@/types";

// === 食べ物モード：モックデータ ===

export const mockFoodTitle: FoodTitle = {
  title:
    "【実録】毎日いきなりステーキだけで1ヶ月生活してみたら…体に起こった衝撃の健康変化と想定外の結末",
  mode: "food",
  food_name: "いきなりステーキ",
  hook_phrase: "毎日食べ続けたら体に異変が…",
};

export const mockFoodOutline: FoodOutline = {
  title:
    "【実録】毎日いきなりステーキだけで1ヶ月生活してみたら…体に起こった衝撃の健康変化と想定外の結末",
  mode: "food",
  food_name: "いきなりステーキ",
  story_summary:
    "ずんだもんがいきなりステーキを毎日食べ続けた結果、深刻な健康被害に見舞われる物語",
  sections: [
    {
      section_key: "hook",
      section_name: "冒頭フック・危機の予告",
      purpose: "視聴者の興味を引き、動画の続きを見たくなる状況を提示",
      content_summary:
        "ずんだもんがレストランのトイレで苦しんでいる。めたんが心配する。",
      min_lines: 8,
      max_lines: 12,
      background: "restaurant_toilet_afternoon",
    },
    {
      section_key: "background",
      section_name: "いきなりステーキの栄養と健康影響を解説",
      purpose: "食べ物の基本情報と栄養素を説明",
      content_summary:
        "いきなりステーキの特徴、栄養成分、適切な摂取量について解説",
      min_lines: 15,
      max_lines: 25,
      background: "modern_study_room",
    },
    {
      section_key: "daily_life",
      section_name: "1週間目：ステーキ生活の始まり",
      purpose: "日常的な摂取の様子を描写",
      content_summary: "ずんだもんがいきなりステーキを毎日食べ始める",
      min_lines: 10,
      max_lines: 15,
      background: "cafe_counter_morning",
    },
    {
      section_key: "honeymoon",
      section_name: "2週間目：ステーキ三昧の幸せな日々",
      purpose: "過剰摂取の初期段階での良い面を描写",
      content_summary: "美味しいステーキを楽しむずんだもん",
      min_lines: 8,
      max_lines: 12,
      background: "restaurant_ikinaristeak_day",
    },
    {
      section_key: "deterioration",
      section_name: "3週間目：体調の変化が始まる",
      purpose: "健康被害の兆候を段階的に描写",
      content_summary: "胃もたれ、倦怠感などの症状が現れ始める",
      min_lines: 12,
      max_lines: 18,
      background: "home_livingroom_morning",
    },
    {
      section_key: "crisis",
      section_name: "4週間目：深刻な健康被害",
      purpose: "最も深刻な健康被害を描写",
      content_summary: "激しい腹痛と吐き気で病院へ",
      min_lines: 10,
      max_lines: 15,
      background: "office_meeting_emergency",
    },
    {
      section_key: "learning",
      section_name: "医師の診断と学び",
      purpose: "医学的な説明と教訓を提示",
      content_summary: "医師から栄養バランスの重要性を学ぶ",
      min_lines: 12,
      max_lines: 18,
      background: "office_meeting_afternoon",
    },
    {
      section_key: "recovery",
      section_name: "回復と結論",
      purpose: "前向きな結末と視聴者へのメッセージ",
      content_summary: "バランスの取れた食事で回復し、適度な楽しみ方を学ぶ",
      min_lines: 10,
      max_lines: 15,
      background: "home_livingroom_morning",
    },
  ],
};

export const mockFoodScript: FoodScript = {
  title:
    "【実録】毎日いきなりステーキだけで1ヶ月生活してみたら…体に起こった衝撃の健康変化と想定外の結末",
  mode: "food",
  food_name: "いきなりステーキ",
  estimated_duration: "11分20秒",
  sections: [
    {
      section_name: "冒頭フック・危機の予告",
      section_key: "hook",
      scene_background: "restaurant_toilet_afternoon",
      bgm_id: "mayonaka_omocha",
      bgm_volume: 0.2,
      segments: [
        {
          speaker: "zundamon",
          text: "うぅ…胃が…もう限界なのだ…！",
          text_for_voicevox: "うう いが もうげんかいなのだ",
          expression: "sick",
          visible_characters: ["zundamon", "metan"],
          character_expressions: {
            zundamon: "sick",
            metan: "surprised",
          },
        },
        {
          speaker: "metan",
          text: "ちょっと大丈夫！？顔真っ青じゃん！",
          text_for_voicevox: "ちょっとだいじょうぶ かおまっさおじゃん",
          expression: "worried",
          visible_characters: ["zundamon", "metan"],
          character_expressions: {
            zundamon: "sick",
            metan: "worried",
          },
        },
        {
          speaker: "zundamon",
          text: "ぜんぜん平気なのだ…ちょっと休めば…",
          text_for_voicevox: "ぜんぜんへいきなのだ ちょっとやすめば",
          expression: "sad",
          visible_characters: ["zundamon", "metan"],
          character_expressions: {
            zundamon: "sad",
            metan: "thinking",
          },
        },
        {
          speaker: "metan",
          text: "嘘つかないでよ！さっきから息苦しそうだし！",
          text_for_voicevox: "うそつかないでよ さっきからいきぐるしそうだし",
          expression: "angry",
          visible_characters: ["zundamon", "metan"],
          character_expressions: {
            zundamon: "sick",
            metan: "angry",
          },
        },
        {
          speaker: "zundamon",
          text: "ステーキ…注文したのに一口も食べられないのだ…",
          text_for_voicevox: "すてーき ちゅうもんしたのにひとくちもたべられないのだ",
          expression: "sick",
          visible_characters: ["zundamon", "metan"],
          character_expressions: {
            zundamon: "sick",
            metan: "worried",
          },
        },
        {
          speaker: "metan",
          text: "毎日ずっといきなりステーキだけ食べてたから…？",
          text_for_voicevox: "まいにちずっといきなりすてーきだけたべてたから",
          expression: "surprised",
          visible_characters: ["zundamon", "metan"],
          character_expressions: {
            zundamon: "sad",
            metan: "surprised",
          },
        },
      ],
    },
    {
      section_name: "いきなりステーキの栄養と健康影響を解説",
      section_key: "background",
      scene_background: "modern_study_room",
      bgm_id: "maou_piano25",
      bgm_volume: 0.2,
      segments: [
        {
          speaker: "narrator",
          text: "今回はいきなりステーキの栄養や健康影響を解説します。",
          text_for_voicevox:
            "こんかいはいきなりすてーきのえいようやけんこうえいきょうをかいせつします。",
          expression: "normal",
          visible_characters: ["metan"],
          character_expressions: {
            metan: "normal",
          },
          display_item: "grilled_beef_steak_plate",
        },
        {
          speaker: "metan",
          text: "いきなりステーキってどんな特徴があるんですか？",
          text_for_voicevox:
            "いきなりすてーきってどんなとくちょうがあるんですか？",
          expression: "thinking",
          visible_characters: ["metan"],
          character_expressions: {
            metan: "thinking",
          },
        },
        {
          speaker: "narrator",
          text: "いきなりステーキは分厚いビーフステーキが看板メニューです。",
          text_for_voicevox:
            "いきなりすてーきはぶあついびーふすてーきがかんばんめにゅーです。",
          expression: "normal",
          visible_characters: ["metan"],
          character_expressions: {
            metan: "thinking",
          },
        },
      ],
    },
  ],
  all_segments: [
    {
      speaker: "zundamon",
      text: "うぅ…胃が…もう限界なのだ…！",
      text_for_voicevox: "うう いが もうげんかいなのだ",
      expression: "sick",
      visible_characters: ["zundamon", "metan"],
      character_expressions: {
        zundamon: "sick",
        metan: "surprised",
      },
    },
    {
      speaker: "metan",
      text: "ちょっと大丈夫！？顔真っ青じゃん！",
      text_for_voicevox: "ちょっとだいじょうぶ かおまっさおじゃん",
      expression: "worried",
      visible_characters: ["zundamon", "metan"],
      character_expressions: {
        zundamon: "sick",
        metan: "worried",
      },
    },
  ],
};

// === お笑いモード：モックデータ ===

export const mockComedyTitleBatch: ComedyTitleBatch = {
  titles: [
    {
      id: 1,
      title: "【緊急】ずんだもんが突然プロポーズしてきた件について",
      hook_pattern: "突然のプロポーズ",
      situation: "ずんだもんが突然プロポーズ",
      chaos_element: "相手は誰？",
      expected_conflict: "めたんとつむぎの反応",
    },
    {
      id: 2,
      title: "【衝撃】めたんが宝くじで3億円当てた結果www",
      hook_pattern: "高額当選",
      situation: "めたんが宝くじで3億円当選",
      chaos_element: "使い道が斜め上",
      expected_conflict: "金銭感覚の崩壊",
    },
    {
      id: 3,
      title: "【悲報】つむぎさん、ついに会社を辞めてしまう",
      hook_pattern: "突然の退職",
      situation: "つむぎが会社を辞める",
      chaos_element: "理由が意味不明",
      expected_conflict: "次の人生設計",
    },
  ],
};

export const mockComedyTitle: ComedyTitle = {
  title: "【緊急】ずんだもんが突然プロポーズしてきた件について",
  mode: "comedy",
  theme: "ずんだもんが突然プロポーズ",
  clickbait_elements: [
    "突然のプロポーズ",
    "相手は誰？",
    "めたんとつむぎの反応",
  ],
};

export const mockComedyOutline: ComedyOutline = {
  title: "【緊急】ずんだもんが突然プロポーズしてきた件について",
  mode: "comedy",
  theme: "ずんだもんが突然プロポーズ",
  story_summary:
    "ずんだもんが突然プロポーズを宣言。相手は誰なのか？めたんとつむぎは困惑しながらも真相を探る。",
  character_moods: {
    zundamon: 8,
    metan: 5,
    tsumugi: 3,
  },
  forced_ending_type: "突然の展開",
  sections: [
    {
      section_key: "intro",
      section_name: "突然の宣言",
      purpose: "ずんだもんのプロポーズ宣言で視聴者を引き込む",
      content_summary: "ずんだもんが突然「プロポーズする」と宣言",
      min_lines: 8,
      max_lines: 12,
      background: "home_livingroom_morning",
    },
    {
      section_key: "development",
      section_name: "相手は誰？",
      purpose: "プロポーズ相手を巡る混乱",
      content_summary: "めたんとつむぎが相手を推測し始める",
      min_lines: 12,
      max_lines: 18,
      background: "home_livingroom_morning",
    },
    {
      section_key: "climax",
      section_name: "衝撃の真相",
      purpose: "予想外の展開で笑いを生む",
      content_summary: "プロポーズ相手が判明",
      min_lines: 10,
      max_lines: 15,
      background: "home_livingroom_morning",
    },
    {
      section_key: "ending",
      section_name: "オチと締め",
      purpose: "強制終了で笑いを取る",
      content_summary: "予想外のオチで終わる",
      min_lines: 6,
      max_lines: 10,
      background: "home_livingroom_morning",
    },
  ],
};

export const mockComedyScript: ComedyScript = {
  title: "【緊急】ずんだもんが突然プロポーズしてきた件について",
  mode: "comedy",
  theme: "ずんだもんが突然プロポーズ",
  estimated_duration: "8分30秒",
  character_moods: {
    zundamon: 8,
    metan: 5,
    tsumugi: 3,
  },
  ending_type: "突然の展開",
  sections: [
    {
      section_name: "突然の宣言",
      section_key: "intro",
      scene_background: "home_livingroom_morning",
      bgm_id: "honwaka_puppu",
      bgm_volume: 0.3,
      segments: [
        {
          speaker: "zundamon",
          text: "みんな聞いてほしいのだ！実は…プロポーズしようと思ってるのだ！",
          text_for_voicevox:
            "みんなきいてほしいのだ じつは ぷろぽーずしようとおもってるのだ",
          expression: "excited",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "excited",
            metan: "surprised",
            tsumugi: "surprised",
          },
        },
        {
          speaker: "metan",
          text: "えええええ！？マジで言ってる！？",
          text_for_voicevox: "えええええ まじでいってる",
          expression: "surprised",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "happy",
            metan: "surprised",
            tsumugi: "surprised",
          },
        },
        {
          speaker: "tsumugi",
          text: "ずんだもん君…ついに…",
          text_for_voicevox: "ずんだもんくん ついに",
          expression: "thinking",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "excited",
            metan: "surprised",
            tsumugi: "thinking",
          },
        },
        {
          speaker: "zundamon",
          text: "もう決めたのだ！今日プロポーズするのだ！",
          text_for_voicevox: "もうきめたのだ きょうぷろぽーずするのだ",
          expression: "excited",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "excited",
            metan: "surprised",
            tsumugi: "worried",
          },
        },
      ],
    },
    {
      section_name: "相手は誰？",
      section_key: "development",
      scene_background: "cafe_counter_morning",
      bgm_id: "hirusagari_kibun",
      bgm_volume: 0.25,
      segments: [
        {
          speaker: "metan",
          text: "で、でも…相手は誰なの？",
          text_for_voicevox: "で でも あいてはだれなの",
          expression: "thinking",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "happy",
            metan: "thinking",
            tsumugi: "thinking",
          },
        },
        {
          speaker: "zundamon",
          text: "それは…まだ秘密なのだ！",
          text_for_voicevox: "それは まだひみつなのだ",
          expression: "excited",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "excited",
            metan: "surprised",
            tsumugi: "thinking",
          },
        },
        {
          speaker: "tsumugi",
          text: "もしかして…私たちの知ってる人？",
          text_for_voicevox: "もしかして わたしたちのしってるひと",
          expression: "worried",
          visible_characters: ["zundamon", "metan", "tsumugi"],
          character_expressions: {
            zundamon: "happy",
            metan: "thinking",
            tsumugi: "worried",
          },
        },
      ],
    },
  ],
  all_segments: [
    {
      speaker: "zundamon",
      text: "みんな聞いてほしいのだ！実は…プロポーズしようと思ってるのだ！",
      text_for_voicevox:
        "みんなきいてほしいのだ じつは ぷろぽーずしようとおもってるのだ",
      expression: "excited",
      visible_characters: ["zundamon", "metan", "tsumugi"],
      character_expressions: {
        zundamon: "excited",
        metan: "surprised",
        tsumugi: "surprised",
      },
    },
    {
      speaker: "metan",
      text: "えええええ！？マジで言ってる！？",
      text_for_voicevox: "えええええ まじでいってる",
      expression: "surprised",
      visible_characters: ["zundamon", "metan", "tsumugi"],
      character_expressions: {
        zundamon: "happy",
        metan: "surprised",
        tsumugi: "surprised",
      },
    },
  ],
};

// === テストデータ参照情報 ===

export const mockReferenceInfo = `
【テストデータ】
このデータはテスト用のモックデータです。
実際のLLM生成結果ではありません。
`;

export const mockSearchResults = {
  test: "モックデータ",
  source: "テスト用データ",
};

