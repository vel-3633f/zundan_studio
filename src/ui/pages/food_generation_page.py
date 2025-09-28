import streamlit as st

from src.models.food_over import FoodOverconsumptionScript
from src.core.generate_food_over import generate_food_overconsumption_script
from config.models import AVAILABLE_MODELS, get_recommended_model_id, get_model_config
from src.utils.logger import get_logger

from src.ui.components.food_generation.display_components import (
    display_json_debug,
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

                saved_file_path = save_json_to_outputs(result.model_dump(), food_name)
                if saved_file_path:
                    st.success(f"💾 JSONファイルを保存しました: {saved_file_path}")
                else:
                    st.warning("⚠️ JSONファイルの保存に失敗しました")

                display_json_debug(result, "生成された食べ物摂取過多脚本データ")

            else:
                logger.error(f"脚本生成失敗: {result}")
                st.error(f"❌ 食べ物摂取過多脚本の生成に失敗しました")

                error_details = result.get("details", "不明なエラー")
                st.error(f"詳細: {error_details}")
