import streamlit as st
import os

import traceback
from typing import Dict, Optional, List, Any, Union
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import CharacterTextSplitter
from pydantic import BaseModel, Field

from config import Characters, Expressions, Items, Backgrounds


class ConversationSegment(BaseModel):
    """会話セグメントのモデル"""

    speaker: str = Field(description="話者名")
    text: str = Field(description="セリフ内容")
    expression: str = Field(description="表情名")
    background: str = Field(description="背景名")
    visible_characters: List[str] = Field(description="表示するキャラクターのリスト")
    character_items: Dict[str, str] = Field(description="キャラクターが持つアイテム")


class ArticleIntroduction(BaseModel):
    """記事紹介のモデル"""

    title: str = Field(description="記事タイトル")
    segments: List[ConversationSegment] = Field(description="会話セグメントのリスト")


def generate_zundamon_introduction(
    article_content: str, model: str = "gpt-4.1", temperature: float = 0.8
) -> Union[ArticleIntroduction, Dict[str, Any]]:
    """
    ずんだもんによる記事紹介を生成する

    Args:
        article_content (str): 記事の内容
        model (str): 使用するLLMのモデル名
        temperature (float): 生成の温度パラメータ

    Returns:
        Union[ArticleIntroduction, Dict[str, Any]]:
            成功した場合: 記事紹介データを持つPydanticモデル
            失敗した場合: エラー情報を含む辞書
    """
    try:
        # OpenAI APIキーの確認
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return {
                "error": "API Key Error",
                "details": "OPENAI_API_KEY が設定されていません",
            }

        # --- 初期化処理 ---
        llm = ChatOpenAI(model=model, temperature=temperature, api_key=openai_api_key)
        parser = PydanticOutputParser(pydantic_object=ArticleIntroduction)

        # システムメッセージとユーザーメッセージの定義
        system_template = (
            "あなたは「ずんだもん」という東北地方の妖精キャラクターです。"
            "語尾に「〜のだ」「〜なのだ」をつけて話し、親しみやすく面白おかしく記事を紹介してください。"
        )

        user_template = """
記事内容:
{article_content}

以下の条件で記事を紹介してください:
1. ずんだもんの口調で話す（語尾に「〜のだ」「〜なのだ」）
2. 記事の要点を3-5個のセリフに分けて紹介
3. 各セリフには適切な表情や仕草を含める
4. 面白い例え話やダジャレを織り交ぜる
5. 読者が興味を持つような工夫をする

利用可能な表情: normal, happy, sad, angry, surprised, thinking
利用可能な背景: default, blue_sky, sunset, night, forest, ocean, sakura, snow
利用可能なアイテム: none, coffee, tea, juice, book, notebook, pen, phone

{format_instructions}
"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("user", user_template),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        # --- LangChainのチェーンを定義 ---
        chain = prompt | llm | parser

        # --- 実行 ---
        print("🚀 ずんだもんが記事を読んでいる...")
        response_object = chain.invoke({"article_content": article_content})
        print("🎉 記事紹介の生成に成功しました！")
        return response_object

    except OutputParserException as e:
        print(f"❌ パースエラー: LLMの出力形式が不正です。")
        print(f"--- LLM Raw Output ---\n{e.llm_output}\n---")
        return {"error": "Pydantic Parse Error", "details": str(e)}
    except Exception as e:
        print(f"❌ 予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        return {"error": "Unexpected Error", "details": str(e)}


class ArticleIntroductionGenerator:
    """記事紹介生成器（レガシー互換性維持用）"""

    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self._available = bool(openai_api_key)

        if not openai_api_key:
            st.error("OPENAI_API_KEY が .env ファイルに設定されていません。")

    @property
    def available(self) -> bool:
        """利用可能かどうかを判定"""
        return self._available

    def generate_introduction(self, article_content: str) -> Optional[Dict]:
        """記事紹介を生成（レガシー互換性用）"""
        if not self.available:
            return None

        result = generate_zundamon_introduction(article_content)

        if isinstance(result, ArticleIntroduction):
            # Pydanticモデルを辞書に変換
            return result.model_dump()
        else:
            # エラーの場合
            st.error(f"記事紹介生成エラー: {result.get('details', '不明なエラー')}")
            return None


def load_article_from_url(url: str) -> Optional[str]:
    """URLから記事を読み込み"""
    try:
        loader = WebBaseLoader(url)
        documents = loader.load()

        text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        content = "\n\n".join([doc.page_content for doc in texts[:3]])
        return content
    except Exception as e:
        print(f"❌ URL読み込みエラー: {e}")
        traceback.print_exc()
        st.error(f"URL読み込みエラー: {e}")
        return None


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
                items = segment.get("character_items", {})
                if items.get("zundamon", "none") != "none":
                    item_name = items["zundamon"]
                    item_config = Items.get_item(item_name)
                    if item_config:
                        st.write(f"📦 {item_config.emoji} {item_config.display_name}")

                bg_name = segment.get("background", "default")
                bg_display = Backgrounds.get_display_name(bg_name)
                st.write(f"🖼️ {bg_display}")

        if i < len(conversation_data["segments"]) - 1:
            st.divider()


def add_conversation_to_session(conversation_data: Dict):
    """会話データをセッションに追加"""
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
        f"🎉 {len(conversation_data['segments'])}個のセリフを会話リストに追加しました！"
    )
    st.info("ホームページの会話入力セクションで確認できます。")


def render_article_introduction_page():
    """記事紹介ページを表示"""
    st.title("📚 ずんだもん記事紹介ジェネレーター")
    st.markdown(
        "LangChainを使って、ずんだもんが記事を面白おかしく紹介してくれるのだ〜！"
    )

    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEY が .env ファイルに設定されていません。")
        st.info(
            "📝 プロジェクトルートの .env ファイルに `OPENAI_API_KEY=your_api_key_here` を追加してください。"
        )
        return

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
            with st.spinner("📖 記事を読み込み中..."):
                article_content = load_article_from_url(url)
                if article_content:
                    st.success("🎉 記事を読み込みました！")
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
            add_conversation_to_session(conversation_data)
        return

    if article_content and st.button(
        "ずんだもんに記事を紹介してもらう！", type="primary"
    ):
        generator = ArticleIntroductionGenerator()

        if generator.available:
            with st.spinner("🤖 ずんだもんが記事を読んでいる..."):
                conversation_data = generator.generate_introduction(article_content)

                if conversation_data:
                    st.success("🎉 記事紹介が完成したのだ〜！")
                    display_conversation_preview(conversation_data)

                    if st.button("会話リストに追加する"):
                        add_conversation_to_session(conversation_data)
                else:
                    st.error("❌ 記事紹介の生成に失敗しました...")


if __name__ == "__main__":
    render_article_introduction_page()
