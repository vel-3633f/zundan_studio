# ずんだもん動画生成スタジオ v2.0

React + FastAPI で完全リニューアルされた、ずんだもん動画生成アプリケーションです。

## 🎯 主な機能

- 🎬 **会話動画生成**: ずんだもんとゲストキャラクターの会話動画を自動生成
- 📚 **AI 台本生成**: 食べ物をテーマにした解説動画の台本を自動生成
- 🎙️ **音声合成**: VOICEVOX による高品質な音声生成
- 🖼️ **画像処理**: 口パクアニメーションと背景合成
- 🎵 **BGM ミキシング**: セクションごとの BGM 自動配置
- ⚙️ **管理機能**: 背景・アイテム・食べ物データの管理

## 🏗️ 技術スタック

### Frontend

- **React 18** + TypeScript
- **Vite** - 高速ビルドツール
- **Tailwind CSS** - ユーティリティファースト CSS
- **Zustand** - 軽量状態管理
- **React Query** - サーバー状態管理
- **Axios** - HTTP クライアント

### Backend

- **FastAPI** - 高速 API フレームワーク
- **Celery** - 非同期タスクキュー
- **Redis** - メッセージブローカー
- **WebSocket** - リアルタイム進捗通知
- **Pydantic** - データバリデーション

### 既存機能（継続使用）

- **VOICEVOX** - 音声合成エンジン
- **OpenCV** - 画像処理
- **MoviePy** - 動画生成
- **LangChain** - LLM 統合
- **Supabase** - データベース

## 📦 セットアップ

### 必要条件

- Docker & Docker Compose
- 環境変数設定（`.env`ファイル）

### 起動方法

```bash
# リポジトリをクローン
git clone <repository-url>
cd zundan_studio

# 環境変数ファイルを作成
cp .env.example .env
# .envファイルを編集して必要な環境変数を設定

# Docker Composeで全サービスを起動
docker-compose up --build
```

### アクセス URL

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **VOICEVOX**: http://localhost:50021

## 🚀 使用方法

### 1. 会話動画生成

1. ホームページ（http://localhost:3000）にアクセス
2. 話者を選択してセリフを入力
3. 「セリフを追加」で会話リストに追加
4. 「会話動画を生成」をクリック
5. WebSocket でリアルタイム進捗を確認
6. 完成した動画をダウンロード

### 2. AI 台本生成

1. 台本生成ページ（http://localhost:3000/scripts）にアクセス
2. 食べ物名を入力（例: チョコレート）
3. 「アウトラインを生成」をクリック
4. 生成されたアウトラインを確認
5. 「このアウトラインで動画を生成」をクリック
6. 完成した台本を JSON でダウンロード

### 3. データ管理

1. 管理ページ（http://localhost:3000/management）にアクセス
2. 背景画像・アイテム画像・食べ物データを管理

## 📂 プロジェクト構造

```
zundan_studio/
├── backend/                 # FastAPI バックエンド
│   ├── app/
│   │   ├── api/            # APIエンドポイント
│   │   ├── core/           # コアロジック
│   │   ├── services/       # ビジネスロジック
│   │   ├── models/         # データモデル
│   │   ├── tasks/          # Celeryタスク
│   │   ├── config/         # 設定
│   │   └── main.py         # エントリーポイント
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React フロントエンド
│   ├── src/
│   │   ├── pages/          # ページコンポーネント
│   │   ├── components/     # UIコンポーネント
│   │   ├── stores/         # Zustand状態管理
│   │   ├── api/            # APIクライアント
│   │   ├── types/          # TypeScript型定義
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── assets/                  # 画像・音声アセット
├── outputs/                 # 生成動画出力
├── docker-compose.yml       # Docker Compose設定
└── README.md
```

## 🔧 開発

### バックエンド開発

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンド開発

```bash
cd frontend
npm install
npm run dev
```

### Celery ワーカー起動

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## 🐛 トラブルシューティング

### VOICEVOX に接続できない

```bash
# VOICEVOXコンテナの状態確認
docker-compose ps voicevox

# VOICEVOXコンテナを再起動
docker-compose restart voicevox
```

### Celery タスクが実行されない

```bash
# Redisの接続確認
docker-compose exec redis redis-cli ping

# Celeryワーカーのログ確認
docker-compose logs celery-worker
```

### フロントエンドがバックエンドに接続できない

- 環境変数`VITE_API_URL`と`VITE_WS_URL`が正しく設定されているか確認
- バックエンドが起動しているか確認（http://localhost:8000/health）

## 📝 API ドキュメント

FastAPI の自動生成ドキュメントを参照してください：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 v1.0 からの主な変更点

### アーキテクチャ

- ❌ Streamlit → ✅ React + FastAPI
- ❌ 同期処理 → ✅ 非同期処理（Celery）
- ❌ セッション状態 → ✅ REST API + WebSocket

### メリット

- ⚡ **パフォーマンス向上**: 非同期処理により複数ユーザー対応
- 🎨 **モダン UI**: React による洗練されたインターフェース
- 📈 **スケーラビリティ**: Celery ワーカーの水平スケーリング
- 🔌 **API 化**: 他のクライアントからも利用可能
- 🔒 **型安全性**: TypeScript による開発体験向上

## 📄 ライセンス

MIT License

## 🙏 謝辞

- VOICEVOX プロジェクト
- ずんだもん・四国めたん キャラクター
- その他のオープンソースプロジェクト
