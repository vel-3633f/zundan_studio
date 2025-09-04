import streamlit as st
import os
import logging
from typing import List, Dict, Optional

from src.core.voice_generator import VoiceGenerator
from src.video_generator import VideoGenerator
from src.utils.utils import (
    setup_logging,
    generate_unique_filename,
    cleanup_temp_files,
    ensure_directories,
    cleanup_all_generated_files,
    get_generated_files_info,
)
from config import (
    APP_CONFIG,
    UI_CONFIG,
    Characters,
    Backgrounds,
    Expressions,
    DefaultConversations,
    Paths,
)

# Setup
setup_logging(debug=os.getenv("DEBUG_MODE", "false").lower() == "true")
logger = logging.getLogger(__name__)
ensure_directories()

# Page config
st.set_page_config(
    page_title=APP_CONFIG.title,
    page_icon=APP_CONFIG.page_icon,
    layout=APP_CONFIG.layout,
    initial_sidebar_state="expanded",
)


def init_session_state():
    """Initialize session state variables"""
    if "conversation_lines" not in st.session_state:
        st.session_state.conversation_lines = (
            DefaultConversations.get_sample_conversation()
        )

    for key, default in [
        ("generated_video_path", None),
        ("generation_in_progress", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


def check_voicevox_connection() -> bool:
    """Check VOICEVOX API connection"""
    try:
        return VoiceGenerator().check_health()
    except Exception as e:
        logger.error(f"VOICEVOX connection check failed: {e}")
        return False


def generate_conversation_video(
    conversations: List[Dict],
    speed: float,
    pitch: float,
    intonation: float,
    progress_bar,
    status_text,
    enable_subtitles: bool = True,
    conversation_mode: str = "duo",
) -> Optional[str]:
    """Generate conversation video"""
    try:
        voice_gen = VoiceGenerator()
        video_gen = VideoGenerator()
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Generate audio
        progress_bar.progress(0.1)
        status_text.text("会話音声を生成中...")

        audio_files = voice_gen.generate_conversation_voices(
            conversations=conversations,
            speed=speed,
            pitch=pitch,
            intonation=intonation,
            output_dir=Paths.get_temp_dir(),
        )

        if not audio_files:
            st.error("音声生成に失敗しました")
            return None

        # Generate video
        progress_bar.progress(0.5)
        status_text.text("会話動画を生成中...")

        video_path = os.path.join(
            Paths.get_outputs_dir(),
            generate_unique_filename("conversation_video", "mp4"),
        )

        def progress_callback(progress):
            progress_bar.progress(0.5 + (progress * 0.4))
            status_text.text(f"会話動画を生成中... ({int(progress * 100)}%)")

        result = video_gen.generate_conversation_video_v2(
            conversations=conversations,
            audio_file_list=audio_files,
            output_path=video_path,
            progress_callback=progress_callback,
            enable_subtitles=enable_subtitles,
            conversation_mode=conversation_mode,
        )

        if result:
            progress_bar.progress(1.0)
            status_text.text("生成完了！")
        else:
            st.error("動画生成に失敗しました")

        return result

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        st.error(f"エラーが発生しました: {str(e)}")
        return None


def render_conversation_input(
    background_options: List[str], expression_options: List[str]
) -> None:
    """Render conversation input interface"""
    st.subheader("会話内容")

    for i, line in enumerate(st.session_state.conversation_lines):
        # Ensure all keys exist
        if "background" not in line:
            line["background"] = "default"
        if "expression" not in line:
            line["expression"] = "normal"
        if "visible_characters" not in line:
            line["visible_characters"] = ["zundamon", line.get("speaker", "zundamon")]

        # Get character info from config
        characters = Characters.get_all()
        char_config = characters[line["speaker"]]

        with st.container():
            cols = st.columns(UI_CONFIG.input_columns)

            # Speaker selection
            with cols[0]:
                char_options = Characters.get_display_options()
                current_char_index = next(
                    (
                        idx
                        for idx, opt in enumerate(char_options)
                        if opt[0] == line["speaker"]
                    ),
                    0,
                )

                selected_option = st.selectbox(
                    "話者",
                    options=[opt[0] for opt in char_options],
                    format_func=lambda x: next(
                        opt[1] for opt in char_options if opt[0] == x
                    ),
                    key=f"speaker_{i}",
                    index=current_char_index,
                )
                line["speaker"] = selected_option

            # Text input
            with cols[1]:
                line["text"] = st.text_area(
                    f"{char_config.emoji} {char_config.display_name} ({char_config.display_position}) のセリフ",
                    value=line["text"],
                    height=UI_CONFIG.text_area_height,
                    key=f"text_{i}",
                    placeholder=f"{char_config.display_name}が話す内容を入力してください...",
                )

            # Background selection
            with cols[2]:
                st.write("背景")
                current_bg_index = (
                    background_options.index(line["background"])
                    if line["background"] in background_options
                    else 0
                )

                line["background"] = st.selectbox(
                    "背景選択",
                    options=background_options,
                    key=f"background_{i}",
                    index=current_bg_index,
                    format_func=Backgrounds.get_display_name,
                    label_visibility="collapsed",
                )

            # Expression selection
            with cols[3]:
                st.write("表情")
                current_expr_index = (
                    expression_options.index(line["expression"])
                    if line["expression"] in expression_options
                    else 0
                )

                line["expression"] = st.selectbox(
                    "表情選択",
                    options=expression_options,
                    key=f"expression_{i}",
                    index=current_expr_index,
                    format_func=Expressions.get_display_name,
                    label_visibility="collapsed",
                )

            # Visible characters selection
            with cols[4]:
                st.write("表示キャラクター")
                char_names = [opt[0] for opt in Characters.get_display_options()]
                char_display_names = {
                    opt[0]: opt[1].split(" ")[1]
                    for opt in Characters.get_display_options()
                }

                line["visible_characters"] = st.multiselect(
                    "表示キャラクター選択",
                    options=char_names,
                    default=line["visible_characters"],
                    key=f"visible_chars_{i}",
                    format_func=lambda x: char_display_names.get(x, x),
                    label_visibility="collapsed",
                    help="このセリフの間に表示するキャラクターを選択",
                )

                # 話者が含まれていない場合は自動で追加
                if line["speaker"] not in line["visible_characters"]:
                    line["visible_characters"].append(line["speaker"])

            # Delete button
            with cols[5]:
                st.write("")
                st.write("")  # Spacing
                if st.button(
                    "🗑️",
                    key=f"delete_{i}",
                    help="この行を削除",
                    disabled=len(st.session_state.conversation_lines) <= 1,
                ):
                    st.session_state.conversation_lines.pop(i)
                    st.rerun()

        if i < len(st.session_state.conversation_lines) - 1:
            st.markdown("---")


def render_control_buttons() -> None:
    """Render control buttons for adding/resetting conversations"""
    col1, col2, col3 = st.columns(UI_CONFIG.button_columns)

    zundamon_config = Characters.ZUNDAMON
    metan_config = Characters.METAN

    with col1:
        if st.button(
            f"➕ {zundamon_config.display_name}を追加",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.conversation_lines.append(
                {
                    "speaker": "zundamon",
                    "text": "",
                    "background": "default",
                    "expression": "normal",
                    "visible_characters": ["zundamon"],
                }
            )
            st.rerun()

    with col2:
        if st.button(
            f"➕ {metan_config.display_name}を追加",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.conversation_lines.append(
                {
                    "speaker": "metan",
                    "text": "",
                    "background": "default",
                    "expression": "normal",
                    "visible_characters": ["zundamon", "metan"],
                }
            )
            st.rerun()

    with col3:
        if st.button("🔄 会話をリセット", use_container_width=True):
            st.session_state.conversation_lines = (
                DefaultConversations.get_reset_conversation()
            )
            st.rerun()


def render_sidebar() -> tuple:
    """Render sidebar and return parameters"""
    with st.sidebar:
        st.header("音声パラメータ")

        speed_range = UI_CONFIG.speed_range
        pitch_range = UI_CONFIG.pitch_range
        intonation_range = UI_CONFIG.intonation_range

        speed = st.slider("話速", *speed_range, help="話すスピードを調整")
        pitch = st.slider("音高", *pitch_range, help="声の高さを調整")
        intonation = st.slider("抑揚", *intonation_range, help="抑揚の強さを調整")

        st.markdown("---")
        st.header("会話モード")
        conversation_mode = st.selectbox(
            "キャラクター表示設定",
            options=["duo", "solo"],
            index=0,
            format_func=lambda x: {
                "duo": "🎭 デュオ会話（常に2人表示）",
                "solo": "🎤 ソロ発表（話している人のみ表示）",
            }[x],
            help="デュオ: ずんだもんと1人のゲストが常に表示されます\nソロ: 話している人だけが表示されます",
        )

        st.markdown("---")
        st.header("字幕設定")
        enable_subtitles = st.checkbox(
            "字幕を表示",
            value=APP_CONFIG.default_subtitles,
            help="動画に字幕を埋め込みます",
        )

        st.markdown("---")
        st.header("ファイル管理")

        file_info = get_generated_files_info()
        if file_info["total_count"] > 0:
            st.info(
                f"📁 生成済みファイル: {file_info['total_count']}個 ({file_info['total_size_mb']:.1f}MB)"
            )
        else:
            st.info("📁 生成済みファイルなし")

        if st.button(
            "🗑️ 全ファイル削除",
            help="動画・音声・一時ファイルを含む全ての生成ファイルを削除",
            type="secondary",
            use_container_width=True,
        ):
            if file_info["total_count"] > 0:
                cleanup_all_generated_files()
                cleanup_temp_files()
                st.success(f"全ファイル({file_info['total_count']}個)を削除しました")
                st.session_state.generated_video_path = None
                st.rerun()
            else:
                cleanup_temp_files()
                st.info(
                    "削除するファイルがありませんでした（一時ファイルのクリーンアップを実行）"
                )

    return speed, pitch, intonation, enable_subtitles, conversation_mode


def render_results() -> None:
    """Render generation results"""
    if not (
        st.session_state.generated_video_path
        and os.path.exists(st.session_state.generated_video_path)
    ):
        return

    st.header("生成結果")
    st.video(st.session_state.generated_video_path)

    with open(st.session_state.generated_video_path, "rb") as f:
        st.download_button(
            label="📥 動画をダウンロード",
            data=f.read(),
            file_name=os.path.basename(st.session_state.generated_video_path),
            mime="video/mp4",
            type="secondary",
            use_container_width=True,
        )


def main():
    """Main application"""
    init_session_state()

    # Header
    st.title(APP_CONFIG.title)
    st.markdown(APP_CONFIG.description)

    # Check VOICEVOX connection
    if not check_voicevox_connection():
        st.error(
            "⚠️ VOICEVOX APIに接続できません。Dockerコンテナが起動しているか確認してください。"
        )
        st.info("コマンド: `docker-compose up voicevox`")
        return

    st.success("✅ VOICEVOX API接続完了")

    # Sidebar
    speed, pitch, intonation, enable_subtitles, conversation_mode = render_sidebar()

    # Main content
    col1, col2 = st.columns(UI_CONFIG.main_columns)

    with col1:
        # Get available backgrounds and expressions
        background_options = ["default"] + VideoGenerator().video_processor.get_background_names()
        expression_options = Expressions.get_available_names()

        # Conversation input
        render_conversation_input(background_options, expression_options)
        render_control_buttons()

        st.markdown("---")

        # Generation button
        _, col_gen, _ = st.columns(UI_CONFIG.generate_columns)
        with col_gen:
            valid_lines = [
                line
                for line in st.session_state.conversation_lines
                if line["text"].strip()
            ]
            has_valid_text = bool(valid_lines)

            if has_valid_text:
                st.info(f"📝 {len(valid_lines)}個のセリフが生成対象です")

            if st.button(
                "🎭 会話動画を生成",
                type="primary",
                disabled=not has_valid_text or st.session_state.generation_in_progress,
                use_container_width=True,
                help="入力されたセリフから会話動画を生成します",
            ):

                st.session_state.generation_in_progress = True

                try:
                    with col2:
                        st.header("生成状況")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        status_text.text("生成中...")

                    result = generate_conversation_video(
                        conversations=valid_lines,
                        speed=speed,
                        pitch=pitch,
                        intonation=intonation,
                        progress_bar=progress_bar,
                        status_text=status_text,
                        enable_subtitles=enable_subtitles,
                        conversation_mode=conversation_mode,
                    )

                    if result:
                        st.session_state.generated_video_path = result
                        st.success("🎉 会話動画生成完了！")

                finally:
                    st.session_state.generation_in_progress = False

    with col2:
        if not st.session_state.generation_in_progress:
            st.header("生成状況")
            st.progress(0)
            st.text("待機中...")

    # Results
    render_results()

    # Footer
    st.markdown("---")
    st.markdown(
        """
    **注意事項:**
    - 生成には時間がかかる場合があります
    - 長いテキストほど処理時間が長くなります
    - 各セリフごとに背景を変更できます
    """
    )


if __name__ == "__main__":
    main()
