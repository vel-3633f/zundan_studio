"""
背景透過ページ

画像から背景を除去して透過PNG画像を生成します。
"""

import streamlit as st
import logging
from PIL import Image
from io import BytesIO
from src.core.background_remover import BackgroundRemover

logger = logging.getLogger(__name__)


def render_background_removal_page():
    """背景透過ページをレンダリング"""
    st.title("🖼️ 背景透過")
    st.markdown("画像をアップロードすると、背景を自動的に除去して透過PNG画像を作成します。")

    st.markdown("---")

    # 画像アップロード
    uploaded_file = st.file_uploader(
        "画像を選択してください",
        type=["png", "jpg", "jpeg"],
        help="PNG、JPG、JPEG形式の画像ファイルをアップロードできます",
    )

    if uploaded_file is not None:
        try:
            # 元画像を読み込み
            input_image = Image.open(uploaded_file)

            # 元画像を表示
            st.subheader("📤 元画像")
            st.image(input_image, caption="アップロードされた画像", use_container_width=True)

            st.markdown("---")

            # 背景除去ボタン
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🎨 背景を除去する",
                    type="primary",
                    use_container_width=True,
                    help="クリックすると背景除去処理を開始します",
                ):
                    with st.spinner("背景を除去中..."):
                        try:
                            # 背景除去処理
                            remover = BackgroundRemover()
                            output_image = remover.remove_background(input_image)

                            # セッションステートに保存
                            st.session_state.processed_image = output_image
                            st.session_state.original_filename = uploaded_file.name

                            st.success("✅ 背景除去が完了しました！")

                        except Exception as e:
                            st.error(f"❌ エラーが発生しました: {e}")
                            logger.error(f"背景除去処理エラー: {e}")

            # 処理結果を表示
            if hasattr(st.session_state, "processed_image"):
                st.markdown("---")
                st.subheader("📥 処理結果")

                # 処理後の画像を表示
                st.image(
                    st.session_state.processed_image,
                    caption="背景除去後の画像",
                    use_container_width=True,
                )

                # ダウンロードボタン
                st.markdown("### 💾 ダウンロード")

                # 画像をバイトストリームに変換
                buf = BytesIO()
                st.session_state.processed_image.save(buf, format="PNG")
                byte_data = buf.getvalue()

                # ファイル名を生成（元のファイル名に _nobg を追加）
                original_name = st.session_state.original_filename
                name_without_ext = original_name.rsplit(".", 1)[0]
                output_filename = f"{name_without_ext}_nobg.png"

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="📥 PNG画像をダウンロード",
                        data=byte_data,
                        file_name=output_filename,
                        mime="image/png",
                        use_container_width=True,
                        help="背景が透過されたPNG画像をダウンロードします",
                    )

        except Exception as e:
            st.error(f"❌ 画像の読み込みに失敗しました: {e}")
            logger.error(f"画像読み込みエラー: {e}")

    else:
        st.info("👆 まずは画像をアップロードしてください")
