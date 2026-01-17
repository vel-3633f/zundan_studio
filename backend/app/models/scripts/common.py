from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict


class SectionDefinition(BaseModel):
    section_key: str = Field(
        description="セクションのキー（例: hook, background, introduction）"
    )
    section_name: str = Field(description="セクションの表示名")
    purpose: str = Field(description="このセクションの目的・役割")
    content_summary: str = Field(description="このセクションで扱う内容の要約")
    min_lines: int = Field(ge=5, le=50, description="最低セリフ数")
    max_lines: int = Field(ge=5, le=50, description="最大セリフ数")
    background: str = Field(
        description="背景シーン（3単語アンダースコア区切り形式、例: modern_study_room）"
    )

    @field_validator("section_key")
    @classmethod
    def validate_section_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("セクションキーは空にできません")
        if not v.replace("_", "").isalnum():
            raise ValueError("セクションキーは英数字とアンダースコアのみ使用できます")
        return v.strip().lower()

    @field_validator("background")
    @classmethod
    def validate_background_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("背景は空にできません")
        return v.strip()

    @field_validator("min_lines", "max_lines")
    @classmethod
    def validate_line_range(cls, v: int) -> int:
        if v < 5 or v > 50:
            raise ValueError("セリフ数は5-50の範囲である必要があります")
        return v


class ConversationSegment(BaseModel):
    speaker: str = Field(description="話者名（ローマ字で指定: zundamon, metan, tsumugi, narrator のいずれか）")
    text: str = Field(description="セリフ内容（字幕表示用・漢字カタカナ含む）")
    text_for_voicevox: str = Field(
        description="VOICEVOX読み上げ用テキスト（完全ひらがな）"
    )
    expression: str = Field(description="話者の表情名（後方互換性のため維持）")
    visible_characters: List[str] = Field(description="表示するキャラクターのリスト（ローマ字で指定: zundamon, metan, tsumugi のいずれか）")
    character_expressions: Dict[str, str] = Field(
        default_factory=dict,
        description="各キャラクターの表情を個別に指定 {キャラクター名（ローマ字）: 表情名}。例: {\"zundamon\": \"excited\", \"metan\": \"angry\"}",
    )

    @field_validator("speaker", "text", "text_for_voicevox", "expression")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("visible_characters")
    @classmethod
    def validate_visible_characters(cls, v: List[str], info) -> List[str]:
        import logging
        logger = logging.getLogger(__name__)
        
        speaker = info.data.get("speaker", "")
        
        # ナレーターの場合は空配列を許可（声のみ）、または最大2人までキャラクターを表示可能
        if speaker == "narrator":
            if not v:
                return []
            cleaned = [char.strip() for char in v if char and char.strip()]
            if len(cleaned) > 2:
                raise ValueError(f"ナレーターの場合、表示するキャラクターは2人までです。現在{len(cleaned)}人指定されています: {cleaned}")
            
            # めたんとつむぎが同時に含まれている場合、片方を削除
            if "metan" in cleaned and "tsumugi" in cleaned:
                # つむぎを削除（デフォルト）
                cleaned.remove("tsumugi")
                logger.warning(f"ナレーターの場合、めたんとつむぎが同時に指定されていたため、つむぎを削除しました: {cleaned}")
            
            # 3人以上の場合、最初の2人に絞る（めたんとつむぎは同時に含まれない）
            if len(cleaned) > 2:
                result = cleaned[:2]
                logger.info(f"ナレーターの場合、3人以上指定されていたため修正しました: {cleaned} -> {result}")
                return result
            
            # 1人しか指定されていない場合、もう1人を追加
            if len(cleaned) == 1:
                # ずんだもんをデフォルトで追加
                if cleaned[0] != "zundamon":
                    cleaned.insert(0, "zundamon")
                    logger.info(f"ナレーターの場合、1人しか指定されていなかったためずんだもんを追加しました: {cleaned}")
                else:
                    # ずんだもんのみの場合、めたんを追加
                    cleaned.append("metan")
                    logger.info(f"ナレーターの場合、1人しか指定されていなかったためめたんを追加しました: {cleaned}")
            
            return cleaned
        
        # それ以外のキャラクターは空配列を許可しない
        if not v:
            raise ValueError("表示するキャラクターリストは空にできません")
        cleaned = [char.strip() for char in v if char and char.strip()]
        if not cleaned:
            raise ValueError("有効な表示キャラクターが必要です")
        
        original_cleaned = cleaned.copy()
        
        # 1. 話者が含まれていない場合、話者を追加
        if speaker not in cleaned:
            cleaned.insert(0, speaker)
            logger.info(f"話者 {speaker} が含まれていなかったため追加しました: {original_cleaned} -> {cleaned}")
        
        # 2. めたんとつむぎが同時に含まれている場合、話者以外を削除
        if "metan" in cleaned and "tsumugi" in cleaned:
            # 話者を残し、もう一方を削除
            if speaker == "metan":
                cleaned.remove("tsumugi")
                logger.warning(f"めたんとつむぎが同時に指定されていたため、つむぎを削除しました: {original_cleaned} -> {cleaned}")
            elif speaker == "tsumugi":
                cleaned.remove("metan")
                logger.warning(f"めたんとつむぎが同時に指定されていたため、めたんを削除しました: {original_cleaned} -> {cleaned}")
            else:
                # 話者がずんだもんの場合、めたんを残す（デフォルト）
                cleaned.remove("tsumugi")
                logger.warning(f"めたんとつむぎが同時に指定されていたため、つむぎを削除しました: {original_cleaned} -> {cleaned}")
        
        # 3. 3人以上指定されている場合、話者 + もう1人に絞る
        if len(cleaned) > 2:
            result = [speaker]
            # 話者以外で最初に見つかったキャラクターを追加
            for char in cleaned:
                if char != speaker and char in ["zundamon", "metan", "tsumugi"]:
                    result.append(char)
                    break
            # もし誰も見つからなかった場合、ずんだもんをデフォルトで追加
            if len(result) == 1:
                if speaker != "zundamon":
                    result.append("zundamon")
                else:
                    result.append("metan")
            logger.info(f"3人以上指定されていたため修正しました: {cleaned} -> {result}")
            cleaned = result
        
        # 4. 1人しか指定されていない場合の処理
        if len(cleaned) == 1:
            # 自動的にもう1人を追加
            if speaker == "zundamon":
                # ずんだもんが話す場合、めたんを追加（デフォルト）
                cleaned.append("metan")
                logger.info(f"1人のみが指定されたため、めたんを追加しました: {cleaned}")
            elif speaker == "metan":
                # めたんが話す場合、ずんだもんを追加
                cleaned.insert(0, "zundamon")
                logger.info(f"1人のみが指定されたため、ずんだもんを追加しました: {cleaned}")
            elif speaker == "tsumugi":
                # つむぎが話す場合、ずんだもんを追加
                cleaned.insert(0, "zundamon")
                logger.info(f"1人のみが指定されたため、ずんだもんを追加しました: {cleaned}")
            else:
                # その他の場合（ナレーター以外）、ずんだもんを追加
                cleaned.insert(0, "zundamon")
                logger.info(f"1人のみが指定されたため、ずんだもんを追加しました: {cleaned}")
        
        # 5. 最終的なバリデーション: 1人または2人であることを確認
        if len(cleaned) == 0:
            raise ValueError(f"表示するキャラクターは少なくとも1人必要です。現在{len(cleaned)}人: {cleaned}")
        
        if len(cleaned) > 2:
            raise ValueError(f"表示するキャラクターは最大2人までです。現在{len(cleaned)}人: {cleaned}")
        
        # 6. 話者が含まれていることを確認
        if speaker not in cleaned:
            raise ValueError(f"話者 {speaker} は必ず含める必要があります。現在: {cleaned}")
        
        # 7. 2人の場合、めたんとつむぎが同時に含まれていないことを確認
        if len(cleaned) == 2:
            if "metan" in cleaned and "tsumugi" in cleaned:
                raise ValueError(f"めたんとつむぎを同時に表示することはできません（同じ位置に配置されます）。現在: {cleaned}")
        
        return cleaned


class VideoSection(BaseModel):
    section_name: str = Field(description="セクション名")
    section_key: Optional[str] = Field(
        default=None,
        description="セクションのキー（例: hook, background, introduction）",
    )
    scene_background: str = Field(description="このセクションで使用する背景シーン")
    bgm_id: str = Field(default="none", description="このセクションで使用するBGMのID")
    bgm_volume: float = Field(default=0.25, description="BGMの音量（0.0〜1.0）")
    segments: List[ConversationSegment] = Field(
        description="このセクションの会話セグメント"
    )

    @field_validator("section_name", "scene_background", "bgm_id")
    @classmethod
    def validate_string_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文字列は空にできません")
        return v.strip()

    @field_validator("bgm_volume")
    @classmethod
    def validate_bgm_volume_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("BGM音量は0.0～1.0の範囲である必要があります")
        return v

    @field_validator("segments")
    @classmethod
    def validate_segments_not_empty(
        cls, v: List[ConversationSegment]
    ) -> List[ConversationSegment]:
        if not v:
            raise ValueError("セグメントリストは空にできません")
        return v

