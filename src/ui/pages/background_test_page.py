"""背景画像生成テストページ"""

import streamlit as st
import os
from PIL import Image
import traceback

from src.core.background_generator import BackgroundImageGenerator
from config import Paths


def render_background_test_page():
    """背景画像生成テストページをレンダリング"""
    st.title("🎨 背景画像生成テスト")
    st.markdown("---")

    st.info(
        "このページでは、Imagen 4を使用した背景画像の自動生成機能をテストできます。"
    )

    # ジェネレータ初期化
    try:
        generator = BackgroundImageGenerator()
        st.success(f"✅ BackgroundImageGeneratorを初期化しました")
        st.text(f"背景保存先: {generator.backgrounds_dir}")
    except Exception as e:
        st.error(f"❌ 初期化エラー: {e}")
        st.code(traceback.format_exc())
        return

    # タブで機能を分ける
    tab1, tab2, tab3 = st.tabs(
        ["🖼️ 既存背景一覧", "🎨 単一生成テスト", "📦 一括生成テスト"]
    )

    # タブ1: 既存背景一覧
    with tab1:
        st.subheader("既存の背景画像")

        try:
            existing_backgrounds = generator.get_existing_backgrounds()

            if existing_backgrounds:
                st.success(f"背景画像が {len(existing_backgrounds)} 個見つかりました")

                # グリッド表示の列数
                cols_per_row = 3
                rows = [
                    existing_backgrounds[i : i + cols_per_row]
                    for i in range(0, len(existing_backgrounds), cols_per_row)
                ]

                for row in rows:
                    cols = st.columns(cols_per_row)
                    for col, bg_name in zip(cols, row):
                        with col:
                            st.text(bg_name)
                            # 画像表示
                            bg_path = None
                            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                                test_path = os.path.join(
                                    generator.backgrounds_dir, f"{bg_name}{ext}"
                                )
                                if os.path.exists(test_path):
                                    bg_path = test_path
                                    break

                            if bg_path:
                                try:
                                    img = Image.open(bg_path)
                                    st.image(
                                        img, use_container_width=True, caption=bg_name
                                    )
                                except Exception as e:
                                    st.error(f"画像読み込みエラー: {e}")
            else:
                st.warning("背景画像が見つかりませんでした")

        except Exception as e:
            st.error(f"エラー: {e}")
            st.code(traceback.format_exc())

    # タブ2: 単一生成テスト
    with tab2:
        st.subheader("単一背景の生成テスト")

        st.markdown(
            """
        背景名を入力して、Imagen 4で画像を生成します。

        **背景名の例:**
        - `hospital_room` - 病院の部屋
        - `kitchen` - キッチン
        - `office` - オフィス
        - `park` - 公園
        - `classroom` - 教室
        """
        )

        with st.form("single_generation_form"):
            bg_name_input = st.text_input(
                "背景名（英語、アンダースコア区切り）",
                placeholder="例: cozy_coffee_shop",
                help="英語で背景を表す名前を入力してください（例: hospital_room, sunny_park）",
            )

            # プロンプトプレビュー
            if bg_name_input:
                preview_prompt = generator.generate_background_prompt(bg_name_input)
                st.text_area(
                    "生成プロンプト（プレビュー）",
                    value=preview_prompt,
                    height=100,
                    disabled=True,
                )

            col1, col2 = st.columns([1, 3])
            with col1:
                generate_btn = st.form_submit_button(
                    "🎨 生成", use_container_width=True
                )
            with col2:
                force_regenerate = st.checkbox(
                    "既存の画像がある場合も再生成する", value=False
                )

        if generate_btn:
            if not bg_name_input:
                st.error("背景名を入力してください")
            else:
                # 既存チェック
                if not force_regenerate and generator.check_background_exists(
                    bg_name_input
                ):
                    st.warning(f"⚠️ 背景 '{bg_name_input}' は既に存在します")

                    # 既存画像を表示
                    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                        path = os.path.join(
                            generator.backgrounds_dir, f"{bg_name_input}{ext}"
                        )
                        if os.path.exists(path):
                            st.image(path, caption=f"既存: {bg_name_input}")
                            break
                else:
                    # 生成実行
                    with st.spinner(f"🎨 '{bg_name_input}' を生成中..."):
                        try:
                            output_path = generator.generate_background_image(
                                bg_name_input
                            )
                            st.success(f"✅ 生成完了: {output_path}")

                            # 生成画像を表示
                            img = Image.open(output_path)
                            st.image(img, caption=f"生成: {bg_name_input}")

                        except ImportError as e:
                            st.error(
                                f"❌ google-genai パッケージがインストールされていません"
                            )
                            st.code("pip install google-genai")
                            st.code(traceback.format_exc())

                        except Exception as e:
                            st.error(f"❌ 生成エラー: {e}")
                            st.code(traceback.format_exc())

    # タブ3: 一括生成テスト
    with tab3:
        st.subheader("一括背景生成テスト")

        st.markdown(
            """
        複数の背景名を一度に指定して生成できます。
        既に存在する背景や固定背景はスキップされます。
        """
        )

        # サンプル背景リスト
        sample_backgrounds = [
            "hospital_room",
            "bright_kitchen",
            "cozy_living_room",
            "modern_office",
            "sunny_park",
            "classroom",
        ]

        bg_names_text = st.text_area(
            "背景名リスト（1行に1つ）",
            value="\n".join(sample_backgrounds),
            height=150,
            help="各行に1つずつ背景名を入力してください",
        )

        fixed_backgrounds_text = st.text_input(
            "固定背景（生成スキップ対象）",
            value="modern_study_room, library",
            help="カンマ区切りで指定",
        )

        if st.button("📦 一括生成", use_container_width=True):
            # 背景名リストをパース
            bg_names = [
                line.strip() for line in bg_names_text.split("\n") if line.strip()
            ]
            fixed_backgrounds = [
                name.strip()
                for name in fixed_backgrounds_text.split(",")
                if name.strip()
            ]

            if not bg_names:
                st.error("背景名を入力してください")
            else:
                st.info(f"生成対象: {len(bg_names)} 個の背景")
                st.text(f"固定背景（スキップ）: {', '.join(fixed_backgrounds)}")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = {"generated": [], "skipped": [], "failed": []}

                for i, bg_name in enumerate(bg_names):
                    status_text.text(f"処理中: {bg_name} ({i+1}/{len(bg_names)})")

                    # 固定背景チェック
                    if bg_name in fixed_backgrounds:
                        results["skipped"].append((bg_name, "固定背景"))
                        progress_bar.progress((i + 1) / len(bg_names))
                        continue

                    # 既存チェック
                    if generator.check_background_exists(bg_name):
                        results["skipped"].append((bg_name, "既存"))
                        progress_bar.progress((i + 1) / len(bg_names))
                        continue

                    # 生成
                    try:
                        output_path = generator.generate_background_image(bg_name)
                        results["generated"].append(bg_name)
                    except Exception as e:
                        results["failed"].append((bg_name, str(e)))

                    progress_bar.progress((i + 1) / len(bg_names))

                status_text.empty()
                progress_bar.empty()

                # 結果サマリー
                st.markdown("---")
                st.subheader("📊 生成結果")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ 生成", len(results["generated"]))
                with col2:
                    st.metric("⏭️ スキップ", len(results["skipped"]))
                with col3:
                    st.metric("❌ 失敗", len(results["failed"]))

                # 詳細表示
                if results["generated"]:
                    with st.expander("✅ 生成された背景", expanded=True):
                        for bg_name in results["generated"]:
                            st.text(f"- {bg_name}")

                if results["skipped"]:
                    with st.expander("⏭️ スキップされた背景"):
                        for bg_name, reason in results["skipped"]:
                            st.text(f"- {bg_name} ({reason})")

                if results["failed"]:
                    with st.expander("❌ 失敗した背景", expanded=True):
                        for bg_name, error in results["failed"]:
                            st.text(f"- {bg_name}")
                            st.code(error)
