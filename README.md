# ずんだもん動画生成アプリ

テキスト入力からずんだもんが喋る動画を自動生成するWebアプリケーションです。

## 機能

- テキストからずんだもん音声の生成（VOICEVOX使用）
- 音声に同期した口パクアニメーション
- 音声パラメータ調整（話速、音高、抑揚）
- MP4動画の生成とダウンロード
- 直感的なWebベースUI（Streamlit）

## 技術スタック

- Python 3.11
- Streamlit（UI）
- VOICEVOX（音声合成）
- OpenCV（画像処理）
- MoviePy（動画生成）
- Docker（コンテナ環境）

## セットアップ

### 必要条件

- Docker
- Docker Compose

### 起動方法

1. リポジトリをクローン
```bash
git clone <repository-url>
cd zundan-studio
```

2. アプリケーションを起動
```bash
docker-compose up --build
```

3. ブラウザでアクセス
```
http://localhost:8505
```

## 使用方法

1. テキストエリアにずんだもんに喋らせたいテキストを入力
2. サイドバーで音声パラメータを調整（任意）
   - 話速: 0.5-2.0
   - 音高: -0.15-0.15
   - 抑揚: 0.0-2.0
3. 「動画生成」ボタンをクリック
4. 生成完了後、動画をプレビュー・ダウンロード

## ファイル構成

```
zundan-studio/
├── docker-compose.yml    # Docker環境設定
├── Dockerfile           # アプリケーションコンテナ
├── main.py             # Streamlitメインアプリ
├── requirements.txt    # Python依存関係
├── src/
│   ├── voice_generator.py  # VOICEVOX API処理
│   ├── video_generator.py  # 動画生成処理
│   └── utils.py           # ユーティリティ関数
├── assets/
│   ├── zundamon/         # キャラクター画像
│   └── backgrounds/      # 背景画像
├── temp/                # 一時ファイル
└── outputs/             # 生成動画出力
```

## カスタマイズ

### キャラクター画像の追加

`assets/zundamon/` に以下の画像ファイルを配置：
- `mouth_closed.png` - 口を閉じた状態
- `mouth_half.png` - 半開きの状態  
- `mouth_open.png` - 口を開いた状態

### 背景画像の変更

`assets/backgrounds/default_bg.jpg` を任意の背景画像に置き換え

## 注意事項

- 初回起動時はVOICEVOXエンジンのダウンロードに時間がかかります
- 長いテキストほど動画生成時間が長くなります
- 生成された動画は `outputs/` ディレクトリに保存されます

## トラブルシューティング

### VOICEVOX APIに接続できない

```bash
# VOICEVOXコンテナの状態確認
docker-compose ps

# VOICEVOXコンテナを再起動
docker-compose restart voicevox
```

### 生成に失敗する

```bash
# ログを確認
docker-compose logs streamlit-app

# 一時ファイルをクリア
docker-compose exec streamlit-app rm -rf /app/temp/*
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。