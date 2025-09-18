#!/usr/bin/env python3
"""
JSONローダーのテストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ui.components.json_loader import (
    load_json_file,
    validate_json_structure,
    convert_json_to_conversation_lines,
    validate_and_clean_data
)
from config import Characters, Expressions, Backgrounds, Items

def test_json_loading():
    """JSONファイル読み込みテスト"""
    print("=== JSONファイル読み込みテスト ===")

    # テストファイル
    test_file = "chokoreeto_20250918_124910.json"

    # 利用可能なオプション
    available_characters = list(Characters.get_all().keys())
    available_expressions = Expressions.get_available_names()
    available_backgrounds = list(Backgrounds.get_all().keys())

    print(f"利用可能なキャラクター: {available_characters}")
    print(f"利用可能な表情: {available_expressions}")
    print(f"利用可能な背景: {available_backgrounds}")
    print(f"利用可能なアイテム: {list(Items.get_all().keys())}")
    print()

    # JSONファイル読み込み
    print(f"JSONファイル読み込み: {test_file}")
    data = load_json_file(test_file)

    if not data:
        print("❌ ファイル読み込み失敗")
        return False

    print(f"✅ ファイル読み込み成功")
    print(f"   タイトル: {data.get('title', 'N/A')}")
    print(f"   セグメント数: {len(data.get('all_segments', []))}")
    print()

    # 構造検証
    print("構造検証テスト...")
    if validate_json_structure(data):
        print("✅ 構造検証 OK")
    else:
        print("❌ 構造検証 NG")
        return False
    print()

    # データクリーニングテスト
    print("データクリーニングテスト...")
    try:
        cleaned_data = validate_and_clean_data(
            data, available_characters, available_backgrounds, available_expressions
        )
        print("✅ データクリーニング OK")

        # クリーニング結果のチェック
        segments = cleaned_data.get("all_segments", [])
        for i, segment in enumerate(segments[:3]):  # 最初の3つをチェック
            print(f"   セグメント {i+1}:")
            print(f"     話者: {segment.get('speaker')}")
            print(f"     表情: {segment.get('expression')}")
            print(f"     表示キャラ: {segment.get('visible_characters')}")

    except Exception as e:
        print(f"❌ データクリーニング失敗: {e}")
        return False
    print()

    # 変換テスト
    print("会話データ変換テスト...")
    try:
        conversation_lines = convert_json_to_conversation_lines(
            data, available_characters, available_backgrounds, available_expressions
        )
        print(f"✅ 変換成功 ({len(conversation_lines)}行)")

        # 変換結果のチェック
        for i, line in enumerate(conversation_lines[:3]):  # 最初の3つをチェック
            print(f"   行 {i+1}:")
            print(f"     話者: {line.get('speaker')}")
            print(f"     背景: {line.get('background')}")
            print(f"     表情: {line.get('expression')}")
            print(f"     表示キャラ: {line.get('visible_characters')}")
            print(f"     キャラアイテム: {line.get('character_items')}")

    except Exception as e:
        print(f"❌ 変換失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n🎉 全テスト完了")
    return True

if __name__ == "__main__":
    test_json_loading()