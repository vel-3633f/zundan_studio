from app.models.scripts.common import VideoSection, ConversationSegment


def create_closing_section() -> VideoSection:
    """YouTube動画の締めくくりセクションを生成

    Returns:
        VideoSection: 締めくくりのセクション
    """
    segments = [
        ConversationSegment(
            speaker="zundamon",
            text="今日の動画はここまでだ。",
            text_for_voicevox="きょうのどうがはここまでだ",
            expression="normal",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "normal"},
        ),
        ConversationSegment(
            speaker="zundamon",
            text="頼む……チャンネル登録してくれ……",
            text_for_voicevox="たのむ……ちゃんねるとうろくしてくれ……",
            expression="sick",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "sick"},
        ),
        ConversationSegment(
            speaker="zundamon",
            text="高評価も！な？タダだし減るもんじゃないだろ！？頼むよぉ！",
            text_for_voicevox="こうひょうかも！な？ただだしへるもんじゃないだろ！？たのむよぉ！",
            expression="surprised",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "surprised"},
        ),
        ConversationSegment(
            speaker="zundamon",
            text="……ふぅ。では、また次回の動画で。",
            text_for_voicevox="……ふぅ。では、またじかいのどうがで",
            expression="normal",
            visible_characters=["zundamon"],
            character_expressions={"zundamon": "normal"},
        ),
    ]

    return VideoSection(
        section_name="締めくくり",
        section_key="closing",
        scene_background="blue_sky",
        bgm_id="summer_triangle",
        bgm_volume=0.04,
        segments=segments,
    )
