import streamlit as st
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any, Union
from src.models.food_over import FoodOverconsumptionScript
from src.utils.utils import process_conversation_segments

from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_community.retrievers import TavilySearchAPIRetriever


# =============================================================================
# ロガー設定
# =============================================================================

# ログレベルの環境変数からの取得（デフォルト: INFO）
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# モジュール専用ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# ハンドラーが既に追加されていない場合のみ追加
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)


# =============================================================================
# 設定データ
# =============================================================================

# プロンプトファイルの設定
PROMPTS_DIR = Path("src/prompts")
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "food_system_template.md"
USER_PROMPT_FILE = PROMPTS_DIR / "food_user_template.md"

# Tavily検索設定
TAVILY_SEARCH_RESULTS_COUNT = 3


class CharacterInfo:
    def __init__(self, name: str, display_name: str, personality: str):
        self.name = name
        self.display_name = display_name
        self.personality = personality


class ExpressionInfo:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name


class BackgroundInfo:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name


class ItemInfo:
    def __init__(self, name: str, display_name: str, emoji: str):
        self.name = name
        self.display_name = display_name
        self.emoji = emoji


class Characters:
    _characters = {
        "zundamon": CharacterInfo(
            "zundamon", "ずんだもん", "東北地方の妖精、語尾に「〜のだ」「〜なのだ」"
        ),
        "metan": CharacterInfo("metan", "四国めたん", "ツッコミ役、常識的で冷静な性格"),
        "tsumugi": CharacterInfo(
            "tsumugi", "春日部つむぎ", "素朴で純粋、疑問をよく投げかける"
        ),
        "narrator": CharacterInfo("narrator", "ナレーター", "客観的で落ち着いた解説役"),
    }

    @classmethod
    def get_character(cls, name: str) -> Optional[CharacterInfo]:
        return cls._characters.get(name)

    @classmethod
    def get_display_name(cls, name: str) -> str:
        char = cls._characters.get(name)
        return char.display_name if char else name


class Expressions:
    _expressions = {
        "normal": ExpressionInfo("normal", "通常"),
        "happy": ExpressionInfo("happy", "喜び"),
        "sad": ExpressionInfo("sad", "悲しみ"),
        "angry": ExpressionInfo("angry", "怒り"),
        "surprised": ExpressionInfo("surprised", "驚き"),
        "thinking": ExpressionInfo("thinking", "考え中"),
        "worried": ExpressionInfo("worried", "心配"),
        "excited": ExpressionInfo("excited", "興奮"),
        "sick": ExpressionInfo("sick", "体調不良"),
    }

    @classmethod
    def get_display_name(cls, name: str) -> str:
        expr = cls._expressions.get(name)
        return expr.display_name if expr else name


class Backgrounds:
    _backgrounds = {
        "default": BackgroundInfo("default", "デフォルト"),
        "blue_sky": BackgroundInfo("blue_sky", "青空"),
        "sunset": BackgroundInfo("sunset", "夕焼け"),
        "night": BackgroundInfo("night", "夜"),
        "forest": BackgroundInfo("forest", "森"),
        "ocean": BackgroundInfo("ocean", "海"),
        "sakura": BackgroundInfo("sakura", "桜"),
        "snow": BackgroundInfo("snow", "雪"),
        "kitchen": BackgroundInfo("kitchen", "キッチン"),
        "hospital": BackgroundInfo("hospital", "病院"),
        "laboratory": BackgroundInfo("laboratory", "研究室"),
    }

    @classmethod
    def get_display_name(cls, name: str) -> str:
        bg = cls._backgrounds.get(name)
        return bg.display_name if bg else name


class Items:
    _items = {
        "none": ItemInfo("none", "なし", ""),
        "coffee": ItemInfo("coffee", "コーヒー", "☕"),
        "tea": ItemInfo("tea", "お茶", "🍵"),
        "juice": ItemInfo("juice", "ジュース", "🥤"),
        "book": ItemInfo("book", "本", "📚"),
        "notebook": ItemInfo("notebook", "ノート", "📝"),
        "pen": ItemInfo("pen", "ペン", "✒️"),
        "phone": ItemInfo("phone", "スマホ", "📱"),
        "food": ItemInfo("food", "食べ物", "🍽️"),
        "medicine": ItemInfo("medicine", "薬", "💊"),
        "magnifying_glass": ItemInfo("magnifying_glass", "虫眼鏡", "🔍"),
    }

    @classmethod
    def get_item(cls, name: str) -> Optional[ItemInfo]:
        return cls._items.get(name)


_prompt_cache = {}


def load_prompt_from_file(file_path: Path, cache_key: str = None) -> str:
    """プロンプトファイルを読み込む（キャッシュ機能付き）"""
    if cache_key and cache_key in _prompt_cache:
        logger.debug(f"プロンプトキャッシュからロード: {cache_key}")
        return _prompt_cache[cache_key]

    try:
        if not file_path.exists():
            raise FileNotFoundError(f"プロンプトファイルが見つかりません: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if cache_key:
            _prompt_cache[cache_key] = content
            logger.debug(f"プロンプトファイルをキャッシュに保存: {cache_key}")

        logger.info(f"プロンプトファイル読み込み成功: {file_path}")
        return content

    except Exception as e:
        error_msg = f"プロンプトファイル読み込みエラー ({file_path}): {str(e)}"
        logger.error(error_msg)


def search_food_information(food_name: str) -> Dict[str, List[str]]:
    """TavilyAPIを使用して食べ物の情報を検索する"""
    logger.info(f"食べ物情報検索開始: {food_name}")

    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            error_msg = "TAVILY_API_KEY が設定されていません"
            logger.error(error_msg)
            return {"overeating": [], "benefits": [], "disadvantages": []}

        retriever = TavilySearchAPIRetriever(k=TAVILY_SEARCH_RESULTS_COUNT)

        search_queries = [
            f"{food_name} 食べ過ぎ",
            f"{food_name} メリット",
            f"{food_name} デメリット",
        ]

        search_results = {"overeating": [], "benefits": [], "disadvantages": []}

        result_keys = ["overeating", "benefits", "disadvantages"]

        for i, query in enumerate(search_queries):
            logger.info(f"検索実行: {query}")
            try:
                docs = retriever.invoke(query)
                content_list = []
                for doc in docs:
                    if hasattr(doc, "page_content") and doc.page_content:
                        content_list.append(doc.page_content.strip())

                search_results[result_keys[i]] = content_list
                logger.info(f"検索結果取得: {query} - {len(content_list)}件")

            except Exception as e:
                logger.error(f"検索エラー: {query} - {str(e)}")
                search_results[result_keys[i]] = []

        return search_results

    except Exception as e:
        error_msg = f"Tavily検索で予期せぬエラー: {str(e)}"
        logger.error(error_msg)
        return {"overeating": [], "benefits": [], "disadvantages": []}


def format_search_results_for_prompt(search_results: Dict[str, List[str]]) -> str:
    """検索結果をプロンプト用にフォーマットする"""
    formatted_text = "## 参考情報\n\n"

    sections = [
        ("overeating", "食べ過ぎに関する情報"),
        ("benefits", "メリットに関する情報"),
        ("disadvantages", "デメリットに関する情報"),
    ]

    for key, title in sections:
        formatted_text += f"### {title}\n"
        if search_results[key]:
            for i, content in enumerate(search_results[key], 1):
                formatted_text += f"{i}. {content}\n\n"
        else:
            formatted_text += "情報が見つかりませんでした。\n\n"

    return formatted_text


# =============================================================================
# 脚本生成関数
# =============================================================================


def generate_food_overconsumption_script(
    food_name: str, model: str = "gpt-4.1", temperature: float = 0.8
) -> Union[FoodOverconsumptionScript, Dict[str, Any]]:
    """食べ物摂取過多動画脚本を生成する"""
    logger.info(
        f"脚本生成開始: 食べ物={food_name}, モデル={model}, temperature={temperature}"
    )

    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            error_msg = "OPENAI_API_KEY が設定されていません"
            logger.error(error_msg)
            return {
                "error": "API Key Error",
                "details": error_msg,
            }

        search_results = search_food_information(food_name)
        reference_information = format_search_results_for_prompt(search_results)

        st.session_state.last_search_results = search_results

        # プロンプトファイルから読み込み
        system_template = load_prompt_from_file(SYSTEM_PROMPT_FILE, "system")
        user_template = load_prompt_from_file(USER_PROMPT_FILE, "user")

        llm = ChatOpenAI(model=model, temperature=temperature, api_key=openai_api_key)
        parser = PydanticOutputParser(pydantic_object=FoodOverconsumptionScript)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                ("user", user_template),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = prompt | llm | parser

        logger.info(f"{food_name}の摂取過多動画脚本をLLMで生成中...")
        response_object = chain.invoke(
            {"food_name": food_name, "reference_information": reference_information}
        )

        # all_segmentsを作成
        all_segments = []
        for section in response_object.sections:
            all_segments.extend(section.segments)

        logger.info(f"LLMから受信したセグメント数: {len(all_segments)}")

        # 文字数チェックと分割処理
        processed_segments = process_conversation_segments(all_segments)
        response_object.all_segments = processed_segments

        # セクション内のセグメントも更新
        segment_index = 0
        for section in response_object.sections:
            section_segments = []
            for _ in section.segments:
                if segment_index < len(processed_segments):
                    section_segments.append(processed_segments[segment_index])
                    segment_index += 1
            section.segments = section_segments

        logger.info("食べ物摂取過多動画脚本の生成に成功")

        st.session_state.last_generated_json = response_object
        st.session_state.last_llm_output = "パース成功: 構造化データに変換済み"

        return response_object

    except OutputParserException as e:
        error_msg = "パースエラー: LLMの出力形式が不正です"
        logger.error(f"{error_msg}. LLM出力: {e.llm_output}")

        st.session_state.last_llm_output = e.llm_output
        st.session_state.last_generated_json = None

        return {
            "error": "Pydantic Parse Error",
            "details": str(e),
            "raw_output": e.llm_output,
        }
    except Exception as e:
        error_msg = f"予期せぬエラーが発生しました: {e}"
        logger.error(error_msg, exc_info=True)

        st.session_state.last_llm_output = f"予期せぬエラー: {str(e)}"
        st.session_state.last_generated_json = None

        return {"error": "Unexpected Error", "details": str(e)}


# =============================================================================
# 表示・ユーティリティ関数
# =============================================================================


def display_json_debug(data: Any, title: str = "JSON Debug"):
    """JSONデータをデバッグ用に表示する"""
    with st.expander(f"🔍 {title}", expanded=False):
        if isinstance(data, (dict, list)):
            st.json(data)
        elif hasattr(data, "model_dump"):
            st.json(data.model_dump())
        else:
            try:
                json_str = json.dumps(data, indent=2, ensure_ascii=False)
                st.code(json_str, language="json")
            except Exception as e:
                logger.error(f"JSON変換エラー: {e}")
                st.text(f"JSON変換エラー: {e}")
                st.text(str(data))


def display_raw_llm_output(output: str, title: str = "LLM Raw Output"):
    """LLMの生出力を表示する"""
    with st.expander(f"🤖 {title}", expanded=False):
        st.code(output, language="json")


def display_search_results_debug(search_results: Dict[str, List[str]]):
    """検索結果をデバッグ用に表示する"""
    with st.expander("🔍 Tavily検索結果", expanded=False):
        sections = [
            ("overeating", "食べ過ぎに関する検索結果"),
            ("benefits", "メリットに関する検索結果"),
            ("disadvantages", "デメリットに関する検索結果"),
        ]

        for key, title in sections:
            st.subheader(title)
            if search_results.get(key):
                for i, content in enumerate(search_results[key], 1):
                    st.text_area(f"結果 {i}", content, height=100, key=f"{key}_{i}")
            else:
                st.info("検索結果が見つかりませんでした")


def estimate_video_duration(segments: List[Dict]) -> str:
    """動画の推定時間を計算"""
    total_chars = sum(len(segment["text"]) for segment in segments)
    total_seconds = total_chars * 0.5
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    duration = f"約{minutes}分{seconds:02d}秒"
    logger.debug(f"動画時間推定: {total_chars}文字 → {duration}")
    return duration


def display_food_script_preview(script_data: Union[FoodOverconsumptionScript, Dict]):
    """食べ物摂取過多動画脚本プレビューを表示"""
    if isinstance(script_data, FoodOverconsumptionScript):
        data = script_data.model_dump()
    else:
        data = script_data

    if not data or "all_segments" not in data:
        logger.warning("表示するスクリプトデータが不正です")
        return

    st.subheader("🍽️ 食べ物摂取過多動画脚本プレビュー")

    # 動画情報表示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("YouTubeタイトル", data.get("title", "未設定"))
    with col2:
        st.metric("対象食品", data.get("food_name", "未設定"))
    with col3:
        duration = data.get(
            "estimated_duration", estimate_video_duration(data["all_segments"])
        )
        st.metric("推定時間", duration)
    with col4:
        st.metric("総セリフ数", len(data["all_segments"]))

    # テーマ表示
    if "theme" in data:
        st.info(f"🎯 動画テーマ: {data['theme']}")

    # セクション別表示
    if "sections" in data:
        st.markdown("### 📋 セクション構成")
        for i, section in enumerate(data["sections"]):
            with st.expander(
                f"**{i+1}. {section['section_name']}** ({len(section['segments'])}セリフ)",
                expanded=True,
            ):
                st.write(f"**目的**: {section['purpose']}")

                for j, segment in enumerate(section["segments"]):
                    text_length = len(segment["text"])
                    length_color = "🟢" if text_length <= 30 else "🔴"

                    speaker_name = Characters.get_display_name(
                        segment.get("speaker", "unknown")
                    )
                    expression_name = Expressions.get_display_name(
                        segment.get("expression", "normal")
                    )

                    st.markdown(
                        f"**{j+1}. {speaker_name}** {expression_name} {length_color}({text_length}文字)"
                    )
                    st.write(f"💬 {segment['text']}")

                    # アイテムと背景情報
                    col_a, col_b = st.columns(2)
                    with col_a:
                        items = segment.get("character_items", {})
                        for char, item in items.items():
                            if item != "none":
                                item_info = Items.get_item(item)
                                if item_info:
                                    st.write(
                                        f"📦 {item_info.emoji} {item_info.display_name}"
                                    )

                    with col_b:
                        bg_name = segment.get("background", "default")
                        bg_display = Backgrounds.get_display_name(bg_name)
                        st.write(f"🖼️ {bg_display}")

                    if j < len(section["segments"]) - 1:
                        st.markdown("---")

    logger.info("脚本プレビュー表示完了")


def display_prompt_file_status():
    """プロンプトファイルの状態を表示"""
    with st.expander("📄 プロンプトファイル設定", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**システムプロンプト**")
            if SYSTEM_PROMPT_FILE.exists():
                st.success(f"✅ {SYSTEM_PROMPT_FILE}")
                file_size = SYSTEM_PROMPT_FILE.stat().st_size
                st.caption(f"ファイルサイズ: {file_size} bytes")
                logger.debug(f"システムプロンプトファイル存在確認: {file_size} bytes")
            else:
                st.error(f"❌ ファイルが見つかりません: {SYSTEM_PROMPT_FILE}")
                logger.warning(
                    f"システムプロンプトファイルが見つかりません: {SYSTEM_PROMPT_FILE}"
                )

        with col2:
            st.write("**ユーザープロンプト**")
            if USER_PROMPT_FILE.exists():
                st.success(f"✅ {USER_PROMPT_FILE}")
                file_size = USER_PROMPT_FILE.stat().st_size
                st.caption(f"ファイルサイズ: {file_size} bytes")
                logger.debug(f"ユーザープロンプトファイル存在確認: {file_size} bytes")
            else:
                st.error(f"❌ ファイルが見つかりません: {USER_PROMPT_FILE}")
                logger.warning(
                    f"ユーザープロンプトファイルが見つかりません: {USER_PROMPT_FILE}"
                )

        st.info("💡 プロンプトファイルを編集することで、AIの動作をカスタマイズできます")


def display_debug_section():
    """デバッグ情報セクションを表示"""
    if (
        hasattr(st.session_state, "last_generated_json")
        or hasattr(st.session_state, "last_llm_output")
        or hasattr(st.session_state, "last_search_results")
    ):
        st.subheader("🔧 デバッグ情報")

        debug_mode = st.checkbox("デバッグモードを有効にする", value=False)

        if debug_mode:
            logger.debug("デバッグモードが有効化されました")

            display_prompt_file_status()

            if hasattr(st.session_state, "last_search_results"):
                display_search_results_debug(st.session_state.last_search_results)

            if (
                hasattr(st.session_state, "last_generated_json")
                and st.session_state.last_generated_json
            ):
                display_json_debug(
                    st.session_state.last_generated_json,
                    "生成されたPydanticオブジェクト",
                )

            if hasattr(st.session_state, "last_llm_output"):
                display_raw_llm_output(st.session_state.last_llm_output, "LLMの生出力")


def add_conversation_to_session(conversation_data: Dict):
    """会話データをセッションに追加"""
    if "conversation_lines" not in st.session_state:
        st.session_state.conversation_lines = []

    # Food形式の脚本データから全セグメントを取得
    segments = conversation_data.get("all_segments", [])

    for segment in segments:
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

    logger.info(f"会話リストに{len(segments)}個のセリフを追加")
    st.success(f"🎉 {len(segments)}個のセリフを会話リストに追加しました！")
    st.info("ホームページの会話入力セクションで確認できます。")


# =============================================================================
# メインページ表示関数
# =============================================================================


def render_food_overconsumption_page():
    """食べ物摂取過多解説動画生成ページを表示"""
    logger.info("食べ物摂取過多解説動画生成ページを表示開始")

    st.title("🍽️ 食べ物摂取過多解説動画ジェネレーター")
    st.markdown(
        "食べ物を食べすぎるとどうなるのか？をテーマに、ずんだもんたちが面白く解説する動画脚本を作成するのだ〜！"
    )

    # 食べ物入力セクション
    st.subheader("🥘 調べたい食べ物を入力")

    # 人気の食べ物例を表示
    st.markdown(
        "**人気の食べ物例**: チョコレート、コーヒー、バナナ、お米、卵、牛乳、パン、アイスクリーム、ナッツ、お茶など"
    )

    food_name = st.text_input(
        "食べ物名を入力してください",
        placeholder="例: チョコレート",
        help="一般的な食べ物や飲み物の名前を入力してください。より具体的な名前（例：ダークチョコレート）でも構いません。",
    )

    # 生成設定
    with st.expander("⚙️ 生成設定（詳細設定）"):
        col1, col2 = st.columns(2)
        with col1:
            model = st.selectbox(
                "使用するAIモデル",
                ["gpt-4.1", "gpt-4", "gpt-3.5-turbo"],
                index=0,
                help="gpt-4.1が最も高品質ですが、処理に時間がかかります",
            )
        with col2:
            temperature = st.slider(
                "創造性レベル",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.1,
                help="高いほど創造的だが、一貫性が下がる可能性があります",
            )

    # 生成ボタン
    if food_name and st.button("🎬 食べ物摂取過多解説動画を作成！", type="primary"):
        logger.info(f"動画生成ボタンがクリックされました: 食べ物={food_name}")

        with st.spinner(
            f"🔍 {food_name}の情報を検索中...（検索→脚本生成で1-2分程度お待ちください）"
        ):
            result = generate_food_overconsumption_script(
                food_name, model=model, temperature=temperature
            )

            if isinstance(result, FoodOverconsumptionScript):
                logger.info("脚本生成成功、プレビューを表示")
                st.success("🎉 食べ物摂取過多解説動画脚本が完成したのだ〜！")
                display_food_script_preview(result)

                # JSON表示
                display_json_debug(result, "生成された食べ物摂取過多脚本データ")

                # 会話リストに追加ボタン
                if st.button("📝 会話リストに追加する", type="secondary"):
                    add_conversation_to_session(result.model_dump())
            else:
                logger.error(f"脚本生成失敗: {result}")
                st.error(f"❌ 食べ物摂取過多脚本の生成に失敗しました")

                error_details = result.get("details", "不明なエラー")
                st.error(f"詳細: {error_details}")

                # プロンプトファイルエラーの場合は設定方法を案内
                if result.get("error") == "Prompt File Error":
                    st.info("💡 以下のプロンプトファイルが必要です:")
                    st.code(f"- {SYSTEM_PROMPT_FILE}")
                    st.code(f"- {USER_PROMPT_FILE}")
                    st.info("これらのファイルを作成してから再度お試しください。")

    # デバッグセクション
    display_debug_section()
