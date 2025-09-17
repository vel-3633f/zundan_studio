import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any
from src.models.food_over import FoodOverconsumptionScript
from src.core.generate_food_over import generate_food_overconsumption_script
from config.app import SYSTEM_PROMPT_FILE, USER_PROMPT_FILE
from config.models import AVAILABLE_MODELS, get_recommended_model_id, get_model_config
from src.utils.logger import get_logger

from dotenv import load_dotenv

load_dotenv()

# ロガーの設定
logger = get_logger(__name__)


class CharacterInfo:
    def __init__(self, name: str, display_name: str, personality: str):
        self.name = name
        self.display_name = display_name
        self.personality = personality


class ExpressionInfo:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name


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
    if not segments:
        return "約0分00秒"

    total_chars = sum(len(segment.get("text", "")) for segment in segments)
    total_seconds = total_chars * 0.4
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    duration = f"約{minutes}分{seconds:02d}秒"
    logger.debug(f"動画時間推定: {total_chars}文字 → {duration}")
    return duration


def display_background_and_items_info(data: Dict):
    """背景とアイテム情報を表示する"""
    st.markdown("### 🎨 背景・アイテム情報")

    all_segments = data.get("all_segments", [])
    if not all_segments:
        st.info("背景・アイテム情報が見つかりませんでした")
        return

    backgrounds = set()
    character_items_all = {}

    for segment in all_segments:
        if "background" in segment:
            backgrounds.add(segment["background"])

        if "character_items" in segment and segment["character_items"]:
            for char, item in segment["character_items"].items():
                if char not in character_items_all:
                    character_items_all[char] = set()
                character_items_all[char].add(item)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🖼️ 使用される背景")
        if backgrounds:
            for bg in sorted(backgrounds):
                st.write(f"• {bg}")
        else:
            st.info("背景情報が見つかりませんでした")

    with col2:
        st.subheader("🎯 キャラクター別アイテム")
        if character_items_all:
            for char, items in character_items_all.items():
                char_display = Characters.get_display_name(char)
                st.write(f"**{char_display}**:")
                for item in sorted(items):
                    st.write(f"  • {item}")
        else:
            st.info("アイテム情報が見つかりませんでした")

    # 詳細なJSON表示
    with st.expander("🔍 背景・アイテム詳細情報（JSON）", expanded=False):
        background_items_data = {
            "backgrounds": list(backgrounds),
            "character_items": {
                char: list(items) for char, items in character_items_all.items()
            },
            "segment_details": [
                {
                    "segment_index": i,
                    "speaker": segment.get("speaker", "unknown"),
                    "background": segment.get("background", ""),
                    "character_items": segment.get("character_items", {}),
                }
                for i, segment in enumerate(all_segments)
                if segment.get("background") or segment.get("character_items")
            ],
        }
        st.json(background_items_data)


def display_food_script_preview(script_data: FoodOverconsumptionScript):
    """食べ物摂取過多動画脚本プレビューを表示"""
    data = script_data.model_dump()

    if not data or "all_segments" not in data:
        logger.warning("表示するスクリプトデータが不正です")
        return

    st.subheader("🍽️ 食べ物摂取過多動画脚本プレビュー")

    st.metric("YouTubeタイトル", data.get("title", "未設定"))

    # 動画情報表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("対象食品", data.get("food_name", "未設定"))
    with col2:
        duration = data.get(
            "estimated_duration", estimate_video_duration(data["all_segments"])
        )
        st.metric("推定時間", duration)
    with col3:
        st.metric("総セリフ数", len(data["all_segments"]))

    # テーマ表示を削除

    # 背景・アイテム情報表示
    display_background_and_items_info(data)

    # セクション別表示
    if "sections" in data:
        st.markdown("### 📋 セクション構成")
        for i, section in enumerate(data["sections"]):
            with st.expander(
                f"**{i+1}. {section['section_name']}** ({len(section['segments'])}セリフ)",
                expanded=True,
            ):

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

                    # 背景情報表示
                    if segment.get("background"):
                        st.caption(f"🖼️ 背景: {segment['background']}")

                    # アイテム情報表示
                    if segment.get("character_items"):
                        items_text = ", ".join(
                            [
                                f"{Characters.get_display_name(char)}: {item}"
                                for char, item in segment["character_items"].items()
                            ]
                        )
                        st.caption(f"🎯 アイテム: {items_text}")

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


def save_json_to_outputs(data: Dict, food_name: str) -> Optional[str]:
    """JSONデータをoutputsフォルダに保存する"""
    try:
        # outputsフォルダのパスを作成
        outputs_dir = Path("outputs/json")

        # ファイル名を生成（食べ物名_日付時刻.json）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 食べ物名をファイル名に使用できるよう処理
        safe_food_name = "".join(
            c for c in food_name if c.isalnum() or c in "-_"
        ).rstrip()
        filename = f"{safe_food_name}_{timestamp}.json"
        file_path = outputs_dir / filename

        # JSONファイルとして保存
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"JSONファイルを保存: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"JSONファイル保存エラー: {e}")
        return None


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
                "background": segment.get("background", ""),
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
            # モデル選択肢を動的に生成
            model_options = [model["name"] for model in AVAILABLE_MODELS]
            model_descriptions = {
                model["name"]: model["description"] for model in AVAILABLE_MODELS
            }
            model_id_map = {model["name"]: model["id"] for model in AVAILABLE_MODELS}

            # 推奨モデルをデフォルトに設定
            recommended_model_id = get_recommended_model_id()
            default_index = 0
            for i, model in enumerate(AVAILABLE_MODELS):
                if model["id"] == recommended_model_id:
                    default_index = i
                    break

            selected_model_name = st.selectbox(
                "使用するAIモデル",
                model_options,
                index=default_index,
                help="推奨モデルが最も高品質ですが、処理に時間がかかる場合があります",
            )
            model = model_id_map[selected_model_name]
        with col2:
            # 選択されたモデルの設定を取得
            selected_model_config = get_model_config(model)
            temp_range = selected_model_config["temperature_range"]
            default_temp = selected_model_config["default_temperature"]

            temperature = st.slider(
                "創造性レベル",
                min_value=temp_range[0],
                max_value=temp_range[1],
                value=default_temp,
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

                saved_file_path = save_json_to_outputs(result.model_dump(), food_name)
                if saved_file_path:
                    st.success(f"💾 JSONファイルを保存しました: {saved_file_path}")
                else:
                    st.warning("⚠️ JSONファイルの保存に失敗しました")

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
