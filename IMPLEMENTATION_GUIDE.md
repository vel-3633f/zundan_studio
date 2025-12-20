# 統合台本生成システム 実装ガイド

## 概要

このシステムは、「食べ物摂取過多」と「お笑い漫談」の 2 つのモードで台本を生成できる統合システムです。
両モードとも、Title → Outline → Script の 3 段階パイプラインで動的セクション構造の台本を生成します。

## アーキテクチャ

### バックエンド構造

```
backend/app/
├── models/
│   └── script_models.py          # 統合データモデル
├── core/
│   ├── unified_script_generator.py    # 統合生成エンジン
│   ├── generic_section_generator.py   # 汎用セクションジェネレーター
│   ├── food_script_generator.py       # 食べ物モード専用
│   └── comedy_script_generator.py     # お笑いモード専用
├── api/
│   └── scripts.py                # 統合API
└── prompts/
    ├── food/                     # 食べ物モードプロンプト
    │   ├── title_generation.md
    │   ├── outline_generation.md
    │   ├── section_generation.md
    │   └── common_rules.md
    └── comedy/                   # お笑いモードプロンプト
        ├── character_rules.md
        ├── title_generation.md
        ├── outline_generation.md
        ├── section_generation.md
        ├── common_rules.md
        └── chaos_rules.md
```

### フロントエンド構造

```
frontend/src/
├── types/
│   └── index.ts                  # 型定義（統合）
├── stores/
│   └── scriptStore.ts            # 状態管理（モード対応）
├── api/
│   └── scripts.ts                # APIクライアント（統合）
├── components/
│   └── script/                   # 台本生成専用コンポーネント
│       ├── ModeSelector.tsx
│       ├── StepIndicator.tsx
│       ├── InputSection.tsx
│       ├── TitleSection.tsx
│       ├── OutlineSection.tsx
│       └── ScriptSection.tsx
└── pages/
    └── ScriptGenerationPage.tsx  # メインページ（全面改造）
```

## 主な機能

### 1. モード選択

- 食べ物モード: 医学的検証型、教育的
- お笑いモード: バカバカしい漫談、教訓なし

### 2. 3 段階パイプライン

#### Step 1: Title Generation

- **食べ物モード**: Tavily 検索 → 煽りタイトル生成
- **お笑いモード**: バカバカしいタイトル生成

#### Step 2: Outline Generation

- **両モード共通**: 動的セクション構造のアウトライン生成
- LLM が内容に応じて最適なセクション数・構成を決定
- 各セクションに名前・目的・セリフ数範囲を設定

#### Step 3: Script Generation

- **両モード共通**: 各セクションの詳細台本生成
- 汎用セクションジェネレーターを使用
- モード別のルールを適用

### 3. お笑いモード専用機能

#### ランダム機嫌システム

- 各キャラクターの機嫌レベルを 0-100 でランダム生成
- 機嫌レベルに応じて口調・反応が変化
- 毎回異なる展開を実現

#### 強制終了パターン

- physical_destruction: 物理的破壊
- selfish_quit: わがまま終了
- ignore: 無視・放置
- third_party: 第三者介入

#### 教育的要素の完全排除

- NG ワード検出
- まとめ・結論・教訓の禁止
- 何も解決しない終わり方

## API エンドポイント

### 統合 API

```
POST /api/scripts/title      # タイトル生成
POST /api/scripts/outline    # アウトライン生成
POST /api/scripts/script     # 台本生成
POST /api/scripts/full       # 3段階一括生成
GET  /api/scripts/health     # ヘルスチェック
```

### リクエスト例

#### タイトル生成（食べ物モード）

```json
{
  "mode": "food",
  "input_text": "チョコレート",
  "model": "claude-3-5-sonnet",
  "temperature": 0.7
}
```

#### タイトル生成（お笑いモード）

```json
{
  "mode": "comedy",
  "input_text": "猫",
  "model": "claude-3-5-sonnet",
  "temperature": 0.9
}
```

## 動的セクション構造

### セクション定義

各セクションは以下の情報を持ちます：

```typescript
interface SectionDefinition {
  section_key: string; // 英語識別子
  section_name: string; // 日本語表示名
  purpose: string; // 目的・役割
  content_summary: string; // 内容要約
  min_lines: number; // 最低セリフ数（5-50）
  max_lines: number; // 最大セリフ数（5-50）
  fixed_background?: string; // 固定背景（任意）
}
```

### 食べ物モードのセクション例

```
1. 冒頭フック (6-10セリフ)
2. 背景情報 (10-15セリフ)
3. 摂取開始 (12-18セリフ)
4. 初期の様子 (15-25セリフ)
5. 異変の始まり (20-30セリフ)
6. 症状悪化 (25-35セリフ)
7. 決定的イベント (20-30セリフ)
8. 医学的解説 (15-25セリフ)
9. 回復と解決策 (10-20セリフ)

合計: 約133-208セリフ
```

### お笑いモードのセクション例

```
1. 導入・誤解 (10-20セリフ)
2. 喧嘩勃発 (15-25セリフ)
3. 論点ずれ (15-20セリフ)
4. カオス化 (20-30セリフ)
5. 強制終了 (5-10セリフ)

合計: 約65-105セリフ
```

## プロンプト設計の特徴

### 食べ物モード

#### 重視する要素

- 医学的正確性
- 参考情報（Tavily 検索）の活用
- 教育的価値
- エンターテイメント性

#### キャラクター設定

- ずんだもん: 主人公、体験者、楽観的
- めたん: ツッコミ役、心配する友人
- つむぎ: 素朴な友人、視聴者代表
- ナレーター: 客観的解説、医学的説明

### お笑いモード

#### 重視する要素

- バカバカしさ
- カオス
- 教育的要素の完全排除
- 強制終了

#### キャラクター設定

- ずんだもん: ボケ担当、傲慢、無知、誤解の天才
- めたん: ツッコミ担当、プライド高い、本気でキレる
- つむぎ: 煽り担当、適当、話をややこしくする

#### 絶対禁止事項

- 「勉強になった」「学んだ」「反省」「頑張ろう」
- まとめ、結論、教訓
- 仲直り、理解し合う、成長する

## 使用方法

### 1. バックエンド起動

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. フロントエンド起動

```bash
cd frontend
npm run dev
```

### 3. ブラウザでアクセス

```
http://localhost:5173
```

### 4. 台本生成フロー

1. モード選択（食べ物 or お笑い）
2. 入力（食べ物名 or テーマ）
3. タイトル確認・承認
4. アウトライン確認・承認
5. 台本生成・完了

## 設定推奨値

### Temperature 設定

- **食べ物モード**: 0.7（バランス重視）
- **お笑いモード**: 0.8-0.9（創造性・カオス重視）

### モデル選択

- **Claude 3.5 Sonnet**: 推奨（バランスが良い）
- **GPT-4**: 論理的な展開
- **Gemini Pro**: 創造的な展開

## トラブルシューティング

### バックエンドエラー

#### プロンプトファイルが見つからない

```
FileNotFoundError: プロンプトファイルが見つかりません
```

→ `backend/app/prompts/food/` と `backend/app/prompts/comedy/` が存在するか確認

#### Tavily API Key エラー

```
TAVILY_API_KEY が設定されていません
```

→ `.env` ファイルに `TAVILY_API_KEY` を設定

### フロントエンドエラー

#### API 接続エラー

```
Network Error
```

→ バックエンドが起動しているか確認
→ CORS 設定を確認

## 今後の拡張

### 新しいモードの追加

1. `ScriptMode` に新しいモードを追加
2. 専用ジェネレータークラスを作成
3. プロンプトディレクトリを作成
4. `UnifiedScriptGenerator` に分岐処理を追加

### プロンプトの調整

各モードのプロンプトファイルを編集することで、生成内容を調整できます：

- `prompts/food/` - 食べ物モード
- `prompts/comedy/` - お笑いモード

## 注意事項

1. **既存の古いプロンプト**

   - `backend/app/prompts/sections/` は旧システムのファイル
   - 新システムでは使用しない
   - 削除推奨（手動で削除してください）

2. **後方互換性**

   - 旧 API エンドポイントは保持されています
   - 既存の動画生成機能との連携は維持

3. **お笑いモードの特性**
   - 高い temperature 推奨（0.8 以上）
   - ランダム性により毎回異なる展開
   - 教育的要素は完全排除

## 実装完了チェックリスト

- ✅ 統合データモデル作成
- ✅ 汎用セクションジェネレーター作成
- ✅ 食べ物モードジェネレーター作成
- ✅ お笑いモードジェネレーター作成
- ✅ 統合生成エンジン作成
- ✅ 食べ物モードプロンプト作成
- ✅ お笑いモードプロンプト作成
- ✅ 統合 API 実装
- ✅ フロントエンド型定義更新
- ✅ API クライアント更新
- ✅ 状態管理更新
- ✅ UI コンポーネント作成
- ✅ メインページ改造
- ✅ TypeScript コンパイルチェック
- ✅ Python コンパイルチェック

## 次のステップ

1. バックエンド・フロントエンドを起動
2. 食べ物モードで動作確認
3. お笑いモードで動作確認
4. モード切替の動作確認
5. 必要に応じてプロンプトを調整
