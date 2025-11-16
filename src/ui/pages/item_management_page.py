"""アイテム画像管理ページ"""

import streamlit as st
import os
from PIL import Image
import traceback
from typing import Dict, List
from pathlib import Path

from src.core.item_generator import ItemImageGenerator
from config import Paths
from src.ui.components.home.json_loader import (
    get_json_files_list,
    load_json_file,
    extract_items_from_json,
)
from src.ui.components.home.item_gallery import (
    render_item_status_check,
    render_item_upload_section,
    render_item_management_section,
)


def get_item_segment_mapping(data: Dict) -> Dict[str, List[str]]:
    """アイテム名とそれが使用されているセグメントのマッピングを取得

    Args:
        data: 台本JSONデータ

    Returns:
        Dict[str, List[str]]: {アイテム名: [セリフテキストのリスト]}
    """
    item_to_segments = {}
    sections = data.get("sections", [])

    for section in sections:
        segments = section.get("segments", [])
        for segment in segments:
            display_item = segment.get("display_item")
            text = segment.get("text", "")

            if display_item and display_item != "none":
                if display_item not in item_to_segments:
                    item_to_segments[display_item] = []
                # セリフの最初の30文字を保存
                preview_text = text[:30] + "..." if len(text) > 30 else text
                item_to_segments[display_item].append(preview_text)

    return item_to_segments


def render_script_item_generation_tab(generator: ItemImageGenerator):
    """台本からアイテム生成タブをレンダリング

    Args:
        generator: ItemImageGenerator インスタンス
    """
    st.subheader("📋 台本JSONからアイテムを生成")

    st.markdown(
        """
    台本JSONファイルから使用されているアイテムを自動抽出し、未生成のアイテムを一括生成できます。
    """
    )

    # JSON選択セクション
    st.markdown("---")
    st.markdown("### 📂 台本JSONを選択")

    json_files = get_json_files_list()

    if not json_files:
        st.warning("📂 outputs/jsonディレクトリにJSONファイルが見つかりません")
        return

    selected_file = st.selectbox(
        "台本JSONファイルを選択",
        options=[""] + json_files,
        format_func=lambda x: "ファイルを選択..." if x == "" else x,
        key="script_item_json_selector",
    )

    if not selected_file or selected_file == "":
        st.info("👆 台本JSONファイルを選択してください")
        return

    # JSONファイルを読み込み
    try:
        data = load_json_file(selected_file)
        if not data:
            st.error("JSONファイルの読み込みに失敗しました")
            return

        # メタデータ表示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("タイトル", data.get("title", "N/A"))
        with col2:
            st.metric("食べ物", data.get("food_name", "N/A"))
        with col3:
            st.metric("推定時間", data.get("estimated_duration", "N/A"))

    except Exception as e:
        st.error(f"ファイルの読み込みエラー: {e}")
        st.code(traceback.format_exc())
        return

    # アイテム抽出と分析
    st.markdown("---")
    st.markdown("### 📊 使用アイテムの分析")

    try:
        # アイテムを抽出
        items = extract_items_from_json(data)

        if not items:
            st.info("この台本ではアイテム画像が使用されていません")
            return

        # アイテムの存在チェック
        item_status = []
        existing_count = 0
        missing_items = []

        # アイテムとセグメントのマッピング
        item_to_segments = get_item_segment_mapping(data)

        for item_name in items:
            exists = generator.check_item_exists(item_name)
            is_valid_name = generator.validate_item_name(item_name)
            segments_used = item_to_segments.get(item_name, [])

            if exists:
                existing_count += 1
            else:
                missing_items.append(item_name)

            remark = ""
            if not is_valid_name:
                remark = "⚠️ 命名規則違反（3単語形式推奨）"

            item_status.append(
                {
                    "アイテム名": item_name,
                    "状態": "✅" if exists else "❌",
                    "命名規則": "✅" if is_valid_name else "⚠️",
                    "使用箇所": f"{len(segments_used)}箇所",
                    "備考": remark,
                }
            )

        # 統計情報
        total_items = len(items)
        missing_count = len(missing_items)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("合計アイテム数", total_items)
        with col2:
            st.metric("既存", existing_count)
        with col3:
            st.metric("未生成", missing_count)

        # アイテムリストをテーブル表示
        if item_status:
            st.dataframe(
                item_status,
                use_container_width=True,
                hide_index=True,
            )

        # 未生成アイテムがある場合
        if missing_items:
            st.warning(f"⚠️ {missing_count}個のアイテムが未生成です")

            # 一括生成セクション
            st.markdown("---")
            st.markdown("### 🎨 未生成アイテムを一括生成")

            st.info(f"生成対象: {', '.join(missing_items)}")

            with st.expander("📝 生成されるアイテムの詳細", expanded=False):
                for item_name in missing_items:
                    segments_used = item_to_segments.get(item_name, [])
                    is_valid = generator.validate_item_name(item_name)
                    st.markdown(
                        f"**{item_name}** ({'✅ 命名規則適合' if is_valid else '⚠️ 命名規則違反'})"
                    )
                    st.caption(f"使用箇所: {len(segments_used)}箇所")
                    if segments_used:
                        st.caption(f"例: {segments_used[0]}")

            if st.button(
                "🚀 未生成アイテムを一括生成",
                type="primary",
                use_container_width=True,
            ):
                st.markdown("---")
                st.subheader("生成中...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = {"generated": [], "failed": []}

                for i, item_name in enumerate(missing_items):
                    status_text.text(
                        f"処理中: {item_name} ({i+1}/{len(missing_items)})"
                    )

                    # 既存チェック（念のため）
                    if generator.check_item_exists(item_name):
                        progress_bar.progress((i + 1) / len(missing_items))
                        continue

                    # 生成
                    try:
                        with st.expander(f"🎨 {item_name} を生成中...", expanded=True):
                            # プロンプト生成
                            st.text("1️⃣ プロンプトを生成中...")
                            prompt = generator.generate_item_prompt(item_name)
                            st.text_area(
                                "生成プロンプト", prompt, height=100, disabled=True
                            )

                            # 画像生成
                            st.text("2️⃣ 画像を生成中...")
                            output_path = generator.generate_item_image(
                                item_name, validate_name=False
                            )

                            # 生成画像を表示
                            st.success(f"✅ 生成完了: {item_name}")
                            img = Image.open(output_path)
                            st.image(
                                img, caption=item_name, use_container_width=True
                            )

                        results["generated"].append(item_name)
                    except Exception as e:
                        st.error(f"❌ {item_name} の生成に失敗: {e}")
                        results["failed"].append((item_name, str(e)))

                    progress_bar.progress((i + 1) / len(missing_items))

                status_text.empty()
                progress_bar.empty()

                # 結果サマリー
                st.markdown("---")
                st.subheader("📊 生成結果")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✅ 生成", len(results["generated"]))
                with col2:
                    st.metric("❌ 失敗", len(results["failed"]))

                if results["generated"]:
                    with st.expander("✅ 生成されたアイテム", expanded=True):
                        for item_name in results["generated"]:
                            st.text(f"- {item_name}")

                if results["failed"]:
                    with st.expander("❌ 失敗したアイテム", expanded=True):
                        for item_name, error in results["failed"]:
                            st.text(f"- {item_name}")
                            st.code(error)

                st.success("🎉 一括生成が完了しました！")
                st.button("🔄 ページを再読み込み", on_click=st.rerun)

        else:
            st.success("✅ すべてのアイテムが生成済みです！")

        # アイテムギャラリー
        st.markdown("---")
        st.markdown("### 🖼️ 台本使用アイテムギャラリー")

        script_items = [
            item for item in items if generator.check_item_exists(item)
        ]

        if script_items:
            cols_per_row = 4
            rows = [
                script_items[i : i + cols_per_row]
                for i in range(0, len(script_items), cols_per_row)
            ]

            for row in rows:
                cols = st.columns(cols_per_row)
                for col, item_name in zip(cols, row):
                    with col:
                        segments_used = item_to_segments.get(item_name, [])
                        st.markdown(f"**{item_name}**")
                        st.caption(f"使用: {len(segments_used)}箇所")

                        # 画像表示
                        item_path = os.path.join(
                            generator.output_dir, f"{item_name}.png"
                        )
                        if os.path.exists(item_path):
                            try:
                                img = Image.open(item_path)
                                st.image(img, use_container_width=True)
                            except Exception as e:
                                st.error(f"画像読み込みエラー: {e}")
        else:
            st.info("台本で使用するアイテム画像がまだ生成されていません")

    except Exception as e:
        st.error(f"アイテム分析エラー: {e}")
        st.code(traceback.format_exc())


def render_item_management_page():
    """アイテム画像管理ページをレンダリング"""
    st.title("🧩 アイテム画像管理")
    st.markdown("---")

    st.info(
        "台本JSONからアイテムを自動生成、または個別にアイテム画像を生成できます。\n\n"
        "**命名規則**: アイテム名は3つの英単語をアンダースコアで区切る形式（例: `steaming_hot_ramen`, `yellow_vitamin_capsules`）"
    )

    # ジェネレータ初期化
    try:
        generator = ItemImageGenerator()
        st.success(f"✅ ItemImageGeneratorを初期化しました")
        st.text(f"アイテム保存先: {generator.output_dir}")
    except Exception as e:
        st.error(f"❌ 初期化エラー: {e}")
        st.code(traceback.format_exc())
        return

    # タブで機能を分ける
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 台本から生成", "🖼️ 既存アイテム一覧", "🎨 単一生成テスト", "📦 一括生成テスト"]
    )

    # タブ1: 台本から生成
    with tab1:
        render_script_item_generation_tab(generator)

    # タブ2: 既存アイテム一覧
    with tab2:
        st.subheader("既存のアイテム画像")

        try:
            # カテゴリー別に取得
            items_by_category = generator.get_items_by_category()

            if items_by_category:
                total_items = sum(len(items) for items in items_by_category.values())
                st.success(f"アイテム画像が {total_items} 個見つかりました")

                # カテゴリーごとに表示
                for category, items in items_by_category.items():
                    st.markdown(f"### 📁 {category} ({len(items)}個)")

                    # グリッド表示
                    cols_per_row = 4
                    rows = [
                        items[i : i + cols_per_row]
                        for i in range(0, len(items), cols_per_row)
                    ]

                    for row in rows:
                        cols = st.columns(cols_per_row)
                        for col, item_name in zip(cols, row):
                            with col:
                                st.text(item_name)
                                # 画像表示
                                if category == "uncategorized":
                                    item_path = os.path.join(
                                        generator.output_dir, f"{item_name}.png"
                                    )
                                else:
                                    item_path = os.path.join(
                                        generator.output_dir,
                                        category,
                                        f"{item_name}.png",
                                    )

                                if os.path.exists(item_path):
                                    try:
                                        img = Image.open(item_path)
                                        st.image(
                                            img,
                                            use_container_width=True,
                                            caption=item_name,
                                        )
                                    except Exception as e:
                                        st.error(f"画像読み込みエラー: {e}")

                    st.markdown("---")
            else:
                st.warning("アイテム画像が見つかりませんでした")

        except Exception as e:
            st.error(f"エラー: {e}")
            st.code(traceback.format_exc())

    # タブ3: 単一生成テスト
    with tab3:
        st.subheader("単一アイテムの生成テスト")

        st.markdown(
            """
        アイテム名を入力して、Imagen 4で画像を生成します。

        **アイテム名の例（3単語形式）:**
        - `steaming_hot_ramen` - 湯気の立つラーメン
        - `yellow_vitamin_capsules` - 黄色いビタミンカプセル
        - `fresh_green_spinach` - 新鮮な緑のほうれん草
        - `red_meat_steak` - 赤身肉のステーキ
        """
        )

        with st.form("single_item_generation_form"):
            item_name_input = st.text_input(
                "アイテム名（英語、3単語をアンダースコア区切り）",
                placeholder="例: steaming_hot_ramen",
                help="3つの英単語をアンダースコアで区切って入力してください",
            )

            # 3単語形式のバリデーション表示
            if item_name_input:
                parts = item_name_input.split("_")
                if len(parts) == 3 and all(
                    part.islower() and part.isalpha() for part in parts
                ):
                    st.success("✅ 命名規則に適合しています")
                elif len(parts) != 3:
                    st.warning(
                        f"⚠️ 3単語形式にしてください（現在: {len(parts)}単語）"
                    )
                else:
                    st.warning("⚠️ 各単語は小文字の英字のみで構成してください")

            # プロンプトプレビュー
            if item_name_input:
                try:
                    preview_prompt = generator.generate_item_prompt(item_name_input)
                    st.text_area(
                        "生成プロンプト（プレビュー）",
                        value=preview_prompt,
                        height=100,
                        disabled=True,
                    )
                except Exception as e:
                    st.warning(f"プロンプト生成エラー: {e}")

            col1, col2 = st.columns([1, 3])
            with col1:
                generate_btn = st.form_submit_button("🎨 生成", use_container_width=True)
            with col2:
                force_regenerate = st.checkbox(
                    "既存の画像がある場合も再生成する", value=False
                )

        if generate_btn:
            if not item_name_input:
                st.error("アイテム名を入力してください")
            else:
                # 既存チェック
                if not force_regenerate and generator.check_item_exists(
                    item_name_input
                ):
                    st.warning(f"⚠️ アイテム '{item_name_input}' は既に存在します")

                    # 既存画像を表示
                    item_path = os.path.join(
                        generator.output_dir, f"{item_name_input}.png"
                    )
                    if os.path.exists(item_path):
                        st.image(item_path, caption=f"既存: {item_name_input}")
                else:
                    # 生成実行
                    with st.spinner(f"🎨 '{item_name_input}' を生成中..."):
                        try:
                            output_path = generator.generate_item_image(
                                item_name_input, validate_name=False
                            )
                            st.success(f"✅ 生成完了: {output_path}")

                            # 生成画像を表示
                            img = Image.open(output_path)
                            st.image(img, caption=f"生成: {item_name_input}")

                        except ImportError as e:
                            st.error(
                                f"❌ google-genai パッケージがインストールされていません"
                            )
                            st.code("pip install google-genai")
                            st.code(traceback.format_exc())

                        except Exception as e:
                            st.error(f"❌ 生成エラー: {e}")
                            st.code(traceback.format_exc())

    # タブ4: 一括生成テスト
    with tab4:
        st.subheader("一括アイテム生成テスト")

        st.markdown(
            """
        複数のアイテム名を一度に指定して生成できます。
        既に存在するアイテムはスキップされます。
        """
        )

        # サンプルアイテムリスト
        sample_items = [
            "steaming_hot_ramen",
            "yellow_vitamin_capsules",
            "fresh_green_spinach",
            "red_meat_steak",
            "white_rice_bowl",
            "orange_carrot_vegetable",
        ]

        items_text = st.text_area(
            "アイテム名リスト（1行に1つ）",
            value="\n".join(sample_items),
            height=150,
            help="各行に1つずつアイテム名を入力してください（3単語形式推奨）",
        )

        if st.button("📦 一括生成", use_container_width=True):
            # アイテム名リストをパース
            item_names = [
                line.strip() for line in items_text.split("\n") if line.strip()
            ]

            if not item_names:
                st.error("アイテム名を入力してください")
            else:
                st.info(f"生成対象: {len(item_names)} 個のアイテム")

                # 3単語形式のチェック
                invalid_names = [
                    name for name in item_names if not generator.validate_item_name(name)
                ]
                if invalid_names:
                    st.warning(
                        f"⚠️ 以下のアイテム名は3単語形式ではありませんが、生成を続行します:\n"
                        + "\n".join(f"- {name}" for name in invalid_names)
                    )

                progress_bar = st.progress(0)
                status_text = st.empty()

                results = {"generated": [], "skipped": [], "failed": []}

                for i, item_name in enumerate(item_names):
                    status_text.text(
                        f"処理中: {item_name} ({i+1}/{len(item_names)})"
                    )

                    # 既存チェック
                    if generator.check_item_exists(item_name):
                        results["skipped"].append((item_name, "既存"))
                        progress_bar.progress((i + 1) / len(item_names))
                        continue

                    # 生成
                    try:
                        output_path = generator.generate_item_image(
                            item_name, validate_name=False
                        )
                        results["generated"].append(item_name)
                    except Exception as e:
                        results["failed"].append((item_name, str(e)))

                    progress_bar.progress((i + 1) / len(item_names))

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
                    with st.expander("✅ 生成されたアイテム", expanded=True):
                        for item_name in results["generated"]:
                            st.text(f"- {item_name}")

                if results["skipped"]:
                    with st.expander("⏭️ スキップされたアイテム"):
                        for item_name, reason in results["skipped"]:
                            st.text(f"- {item_name} ({reason})")

                if results["failed"]:
                    with st.expander("❌ 失敗したアイテム", expanded=True):
                        for item_name, error in results["failed"]:
                            st.text(f"- {item_name}")
                            st.code(error)
