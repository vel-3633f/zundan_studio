"""YouTube動画の締めくくりセクション設定

動画の最後に固定で追加される締めくくりのセリフとBGM設定を管理します。
AIは使わずに固定の内容を追加します。
"""

from app.models.food_over import VideoSection, ConversationSegment


def create_closing_section() -> VideoSection:
    """YouTube動画の締めくくりセクションを生成

    Returns:
        VideoSection: 締めくくりのセクション
    """
    segments = [
        ConversationSegment(
            speaker="zundamon",
            text="今日の動画はここまでなのだ！",
            text_for_voicevox="きょうのどうがはここまでなのだ",
            expression="happy",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "happy"},
        ),
        ConversationSegment(
            speaker="zundamon",
            text="この動画が役に立ったら、チャンネル登録と高評価をお願いするのだ！",
            text_for_voicevox="このどうががやくにたったら、ちゃんねるとうろくとこうひょうかをおねがいするのだ",
            expression="excited",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "excited"},
        ),
        ConversationSegment(
            speaker="zundamon",
            text="じゃないと、ずんだもんがお腹空きすぎて倒れちゃうのだ～！",
            text_for_voicevox="じゃないと、ずんだもんがおなかすきすぎてたおれちゃうのだー",
            expression="sick",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "sick"},
        ),
        ConversationSegment(
            speaker="zundamon",
            text="それじゃあまた次の動画で会おうなのだ！バイバイなのだ〜！",
            text_for_voicevox="それじゃあまたつぎのどうがであおうなのだ！ばいばいなのだー",
            expression="happy",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "happy"},
        ),
    ]

    return VideoSection(
        section_name="締めくくり",
        section_key="closing",
        scene_background="blue_sky",
        bgm_id="summer_triangle",
        bgm_volume=0.20,
        segments=segments,
    )
