import streamlit as st

from src.models.food_over import FoodOverconsumptionScript, StoryOutline
from src.core.generate_food_over_sectioned import (
    generate_outline_only,
    generate_sections_from_approved_outline
)
from config.models import AVAILABLE_MODELS, get_recommended_model_id, get_model_config
from src.utils.logger import get_logger

from src.ui.components.food_generation.display_components import (
    display_json_debug,
    display_outline_for_approval,
)
from src.ui.components.food_generation.utils import (
    save_json_to_outputs,
)
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)


def render_food_overconsumption_page():
    """食べ物摂取過多解説動画生成ページを表示"""

    st.title("🍽️ 動画台本生成")
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
            model_options = [model["name"] for model in AVAILABLE_MODELS]

            model_id_map = {model["name"]: model["id"] for model in AVAILABLE_MODELS}

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

    # アウトライン生成ボタン
    if food_name and st.button("📋 アウトラインを生成", type="primary"):
        logger.info(
            f"アウトライン生成ボタンがクリックされました: 食べ物={food_name}"
        )

        # アウトラインのみ生成
        result = generate_outline_only(
            food_name, model=model, temperature=temperature
        )

        if isinstance(result, StoryOutline):
            logger.info("アウトライン生成成功")
            st.session_state.outline_approved = False  # 承認状態をリセット
        else:
            logger.error(f"アウトライン生成失敗: {result}")
            st.error(f"❌ アウトライン生成に失敗しました")
            error_details = result.get("details", "不明なエラー")
            st.error(f"詳細: {error_details}")

    # アウトラインが生成されている場合、表示と承認ボタンを表示
    if hasattr(st.session_state, 'current_outline') and st.session_state.current_outline:
        outline = st.session_state.current_outline

        # アウトラインを表示
        display_outline_for_approval(outline)

        # 承認ボタンと再生成ボタンを横並びで表示
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ このアウトラインで動画を生成", type="primary", use_container_width=True):
                st.session_state.outline_approved = True
                logger.info("アウトライン承認、セクション生成を開始")

        with col2:
            if st.button("🔄 別のアウトラインを生成", use_container_width=True):
                # 再生成
                result = generate_outline_only(
                    st.session_state.current_food_name,
                    model=st.session_state.current_model,
                    temperature=st.session_state.current_temperature
                )
                if isinstance(result, StoryOutline):
                    st.session_state.outline_approved = False
                    st.rerun()

    # アウトラインが承認された場合、セクション生成を実行
    if hasattr(st.session_state, 'outline_approved') and st.session_state.outline_approved:
        logger.info("承認されたアウトラインからセクション生成を開始")

        result = generate_sections_from_approved_outline()

        if isinstance(result, FoodOverconsumptionScript):
            logger.info("脚本生成成功、プレビューを表示")
            st.success("🎉 食べ物摂取過多解説動画脚本が完成したのだ〜！")

            saved_file_path = save_json_to_outputs(result.model_dump(), st.session_state.current_food_name)
            if saved_file_path:
                st.success(f"💾 JSONファイルを保存しました: {saved_file_path}")
            else:
                st.warning("⚠️ JSONファイルの保存に失敗しました")

            display_json_debug(result, "生成された食べ物摂取過多脚本データ")

            # 承認状態をクリア
            st.session_state.outline_approved = False
            st.session_state.current_outline = None

        else:
            logger.error(f"脚本生成失敗: {result}")
            st.error(f"❌ 食べ物摂取過多脚本の生成に失敗しました")

            error_details = result.get("details", "不明なエラー")
            st.error(f"詳細: {error_details}")

            # 承認状態をクリア
            st.session_state.outline_approved = False
