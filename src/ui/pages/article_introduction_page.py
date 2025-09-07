import streamlit as st
import os
import json
import random
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import TextLoader, WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter


from config import Characters, Expressions, Items, Backgrounds


class ArticleIntroductionGenerator:
    """記事紹介生成器"""

    def __init__(self):
        if not LANGCHAIN_AVAILABLE:
            st.error(
                "LangChainがインストールされていません。pip install langchain openai でインストールしてください。"
            )
            self.available = False
            return

        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if openai_api_key:
            self.llm = OpenAI(
                temperature=0.8,
                openai_api_key=openai_api_key,
                model_name="gpt-4.1",
            )
            self.available = True
        else:
            st.error("OPENAI_API_KEY が .env ファイルに設定されていません。")
            self.available = False

    def create_zundamon_introduction_prompt(self) -> "PromptTemplate":
        """ずんだもんによる記事紹介用プロンプトを作成"""
        template = """
あなたは「ずんだもん」という東北地方の妖精キャラクターです。
語尾に「〜のだ」「〜なのだ」をつけて話し、親しみやすく面白おかしく記事を紹介してください。

記事内容:
{article_content}

以下の条件で記事を紹介してください:
1. ずんだもんの口調で話す（語尾に「〜のだ」「〜なのだ」）
2. 記事の要点を3-5個のセリフに分けて紹介
3. 各セリフには適切な表情や仕草を含める
4. 面白い例え話やダジャレを織り交ぜる
5. 読者が興味を持つような工夫をする

出力形式:
以下のJSON形式で出力してください:

{{
    "title": "記事タイトル",
    "segments": [
        {{
            "speaker": "zundamon",
            "text": "セリフ内容",
            "expression": "表情名",
            "background": "背景名",
            "visible_characters": ["zundamon"],
            "character_items": {{
                "zundamon": "アイテム名"
            }}
        }}
    ]
}}

利用可能な表情: normal, happy, sad, angry, surprised, thinking
利用可能な背景: default, blue_sky, sunset, night, forest, ocean, sakura, snow
利用可能なアイテム: none, coffee, tea, juice, book, notebook, pen, phone
"""
        return PromptTemplate(input_variables=["article_content"], template=template)

    def generate_introduction(self, article_content: str) -> Optional[Dict]:
        """記事紹介を生成"""
        if not self.available:
            return None

        prompt = self.create_zundamon_introduction_prompt()
        chain = LLMChain(llm=self.llm, prompt=prompt)

        try:
            response = chain.run(article_content=article_content)
            # JSONレスポンスをパース
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception as e:
            st.error(f"記事紹介生成エラー: {e}")
            return None


def load_article_from_url(url: str) -> Optional[str]:
    """URLから記事を読み込み"""
    if not LANGCHAIN_AVAILABLE:
        return None

    try:
        loader = WebBaseLoader(url)
        documents = loader.load()

        # テキストを分割
        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        # 最初の数チャンクを結合
        content = "\n\n".join([doc.page_content for doc in texts[:3]])
        return content
    except Exception as e:
        st.error(f"URL読み込みエラー: {e}")
        return None


def load_article_from_text(text: str) -> str:
    """テキストから記事を読み込み"""
    return text


def create_sample_conversation() -> Dict:
    """サンプル会話データを作成"""
    return {
        "title": "ずんだもんのサンプル紹介",
        "segments": [
            {
                "speaker": "zundamon",
                "text": "やあやあ、みんな！今日は面白い記事を見つけたのだ〜！",
                "expression": "happy",
                "background": "default",
                "visible_characters": ["zundamon"],
                "character_items": {"zundamon": "book"},
            },
            {
                "speaker": "zundamon",
                "text": "この記事はとっても勉強になるのだ。まるでずんだ餅のように甘くて栄養満点なのだ！",
                "expression": "normal",
                "background": "default",
                "visible_characters": ["zundamon"],
                "character_items": {"zundamon": "coffee"},
            },
            {
                "speaker": "zundamon",
                "text": "みんなもぜひ読んでみるのだ〜！きっと新しい発見があるはずなのだ！",
                "expression": "thinking",
                "background": "default",
                "visible_characters": ["zundamon"],
                "character_items": {"zundamon": "none"},
            },
        ],
    }


def display_conversation_preview(conversation_data: Dict):
    """会話プレビューを表示"""
    if not conversation_data or "segments" not in conversation_data:
        return

    st.subheader("📖 ずんだもんの紹介プレビュー")

    for i, segment in enumerate(conversation_data["segments"]):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                speaker_name = Characters.ZUNDAMON.display_name
                expression_name = Expressions.get_display_name(
                    segment.get("expression", "normal")
                )

                st.markdown(f"**{speaker_name}** {expression_name}")
                st.write(f"💬 {segment['text']}")

            with col2:
                # アイテム表示
                items = segment.get("character_items", {})
                if items.get("zundamon", "none") != "none":
                    item_name = items["zundamon"]
                    item_config = Items.get_item(item_name)
                    if item_config:
                        st.write(f"📦 {item_config.emoji} {item_config.display_name}")

                # 背景表示
                bg_name = segment.get("background", "default")
                bg_display = Backgrounds.get_display_name(bg_name)
                st.write(f"🖼️ {bg_display}")

        if i < len(conversation_data["segments"]) - 1:
            st.divider()


def render_article_introduction_page():
    """記事紹介ページを表示"""
    st.title("📚 ずんだもん記事紹介ジェネレーター")
    st.markdown(
        "LangChainを使って、ずんだもんが記事を面白おかしく紹介してくれるのだ〜！"
    )

    # Check if API key is available
    api_key_available = bool(os.getenv("OPENAI_API_KEY"))

    if not api_key_available:
        st.warning("⚠️ OPENAI_API_KEY が .env ファイルに設定されていません。")
        st.info(
            "📝 プロジェクトルートの .env ファイルに `OPENAI_API_KEY=your_api_key_here` を追加してください。"
        )
        return

    # 記事入力方法選択
    input_method = st.radio(
        "記事の入力方法を選んでください",
        ["テキスト直接入力", "URL指定", "サンプル表示"],
    )

    article_content = None

    if input_method == "テキスト直接入力":
        article_content = st.text_area(
            "記事内容を入力してください",
            height=300,
            placeholder="ここに記事の内容を貼り付けてください...",
        )

    elif input_method == "URL指定":
        url = st.text_input(
            "記事のURLを入力してください", placeholder="https://example.com/article"
        )

        if url and st.button("記事を読み込む"):
            with st.spinner("記事を読み込み中..."):
                article_content = load_article_from_url(url)
                if article_content:
                    st.success("記事を読み込みました！")
                    with st.expander("読み込んだ記事内容"):
                        st.text(
                            article_content[:1000] + "..."
                            if len(article_content) > 1000
                            else article_content
                        )

    elif input_method == "サンプル表示":
        st.info("サンプル会話を表示します")
        conversation_data = create_sample_conversation()
        display_conversation_preview(conversation_data)

        if st.button("サンプルを会話リストに追加"):
            if "conversation_lines" not in st.session_state:
                st.session_state.conversation_lines = []

            for segment in conversation_data["segments"]:
                st.session_state.conversation_lines.append(
                    {
                        "speaker": segment["speaker"],
                        "text": segment["text"],
                        "expression": segment["expression"],
                        "background": segment["background"],
                        "visible_characters": segment["visible_characters"],
                        "character_items": segment.get("character_items", {}),
                    }
                )

            st.success(
                f"{len(conversation_data['segments'])}個のセリフを会話リストに追加しました！"
            )
            st.info("ホームページの会話入力セクションで確認できます。")
        return

    # 記事紹介生成
    if article_content:
        if st.button("ずんだもんに記事を紹介してもらう！", type="primary"):
            generator = ArticleIntroductionGenerator()

            if generator.available:
                with st.spinner("ずんだもんが記事を読んでいる..."):
                    conversation_data = generator.generate_introduction(article_content)

                    if conversation_data:
                        st.success("記事紹介が完成したのだ〜！")
                        display_conversation_preview(conversation_data)

                        # 会話リストに追加ボタン
                        if st.button("会話リストに追加する"):
                            if "conversation_lines" not in st.session_state:
                                st.session_state.conversation_lines = []

                            for segment in conversation_data["segments"]:
                                st.session_state.conversation_lines.append(
                                    {
                                        "speaker": segment["speaker"],
                                        "text": segment["text"],
                                        "expression": segment["expression"],
                                        "background": segment["background"],
                                        "visible_characters": segment[
                                            "visible_characters"
                                        ],
                                        "character_items": segment.get(
                                            "character_items", {}
                                        ),
                                    }
                                )

                            st.success(
                                f"{len(conversation_data['segments'])}個のセリフを会話リストに追加しました！"
                            )
                            st.info(
                                "ホームページの会話入力セクションで確認・編集できます。"
                            )
                    else:
                        st.error("記事紹介の生成に失敗しました...")

    elif not LANGCHAIN_AVAILABLE:
        st.error("LangChainが利用できません。以下のコマンドでインストールしてください:")
        st.code("pip install langchain openai", language="bash")

    # 使い方説明
    with st.expander("📖 使い方"):
        st.markdown(
            """
        ### 使い方
        
        1. **APIキー設定**: .envファイルにOPENAI_API_KEYを設定
        2. **記事入力**: テキスト直接入力またはURL指定で記事を読み込み
        3. **生成実行**: 「ずんだもんに記事を紹介してもらう！」ボタンをクリック
        4. **確認・追加**: 生成された会話を確認し、気に入ったら会話リストに追加
        5. **動画作成**: ホームページで動画を生成
        
        ### 特徴
        - ずんだもん特有の口調（〜のだ）で記事を紹介
        - 適切な表情・背景・アイテムを自動選択
        - 面白い例え話やダジャレを織り交ぜた紹介
        - 複数のセリフに自動分割
        """
        )


if __name__ == "__main__":
    render_article_introduction_page()
