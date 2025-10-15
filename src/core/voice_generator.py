import requests
import json
import os
import logging
from typing import Dict, Any, Optional, List
from config import Characters

logger = logging.getLogger(__name__)


class VoiceGenerator:
    def __init__(self, api_url: str = None):
        self.api_url = api_url or os.getenv(
            "VOICEVOX_API_URL", "http://localhost:50021"
        )
        self.zundamon_speaker_id = 3
        self.metan_speaker_id = 2  # 四国めたん

        # キャラクター設定をconfigから動的に取得
        characters = Characters.get_all()
        self.speakers = {
            char_name: char_config.speaker_id
            for char_name, char_config in characters.items()
        }

    def check_health(self) -> bool:
        """Check if VOICEVOX API is available"""
        try:
            response = requests.get(f"{self.api_url}/speakers", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"VOICEVOX API health check failed: {e}")
            return False

    def generate_audio_query(
        self, text: str, speaker_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """Generate audio query from text"""
        speaker_id = speaker_id or self.zundamon_speaker_id

        try:
            params = {"text": text, "speaker": speaker_id}

            response = requests.post(
                f"{self.api_url}/audio_query", params=params, timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Audio query generation failed: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Audio query request failed: {e}")
            return None

    def synthesize_audio(
        self, audio_query: Dict[str, Any], speaker_id: int = None
    ) -> Optional[bytes]:
        """Synthesize audio from audio query"""
        speaker_id = speaker_id or self.zundamon_speaker_id

        try:
            response = requests.post(
                f"{self.api_url}/synthesis",
                headers={"Content-Type": "application/json"},
                params={"speaker": speaker_id},
                data=json.dumps(audio_query),
                timeout=60,
            )

            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Audio synthesis failed: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Audio synthesis request failed: {e}")
            return None

    def generate_voice(
        self,
        text: str,
        speed: float = 1.0,
        pitch: float = 0.0,
        intonation: float = 1.0,
        output_path: str = None,
        speaker: str = "zundamon",
    ) -> Optional[str]:
        """Generate voice file from text with parameters"""

        # 話者IDを取得
        speaker_id = self.speakers.get(speaker, self.zundamon_speaker_id)

        # Generate audio query
        audio_query = self.generate_audio_query(text, speaker_id)
        if not audio_query:
            return None

        # Apply voice parameters
        audio_query["speedScale"] = speed
        audio_query["pitchScale"] = pitch
        audio_query["intonationScale"] = intonation

        # Synthesize audio
        audio_data = self.synthesize_audio(audio_query, speaker_id)
        if not audio_data:
            return None

        # Save to file
        if not output_path:
            output_path = "/app/temp/generated_voice.wav"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            with open(output_path, "wb") as f:
                f.write(audio_data)
            logger.info(f"Voice generated successfully for {speaker}: {output_path}")
            return output_path
        except IOError as e:
            logger.error(f"Failed to save audio file: {e}")
            return None

    def generate_conversation_voices(
        self,
        conversations: List[Dict],
        speed: float = None,
        pitch: float = None,
        intonation: float = None,
        output_dir: str = None,
    ) -> List[str]:
        """Generate voice files for conversation in sequence

        Args:
            conversations: List of conversation items with keys: 'speaker', 'text'
            speed, pitch, intonation: Global voice parameters (None = use character defaults)
            output_dir: Output directory for audio files

        Returns:
            List of audio file paths in conversation order
        """
        if not output_dir:
            output_dir = "/app/temp"

        os.makedirs(output_dir, exist_ok=True)

        audio_paths = []

        # 会話順序に従って各セリフの音声を生成
        for i, conv in enumerate(conversations):
            speaker = conv.get("speaker", "zundamon")
            # VOICEVOX用のひらがなテキストを優先、なければ通常のテキストを使用
            text = conv.get("text_for_voicevox", conv.get("text", "")).strip()

            if not text:
                continue

            # キャラクター設定を取得
            characters = Characters.get_all()
            char_config = characters.get(speaker)

            # 音声パラメータを決定（グローバル設定があればそれを優先、なければキャラクター個別設定）
            final_speed = speed if speed is not None else (char_config.default_speed if char_config else 1.0)
            final_pitch = pitch if pitch is not None else (char_config.default_pitch if char_config else 0.0)
            final_intonation = intonation if intonation is not None else (char_config.default_intonation if char_config else 1.0)

            logger.info(f"Speaker: {speaker}, Final params - Speed: {final_speed}, Pitch: {final_pitch}, Intonation: {final_intonation}")

            # 出力ファイル名（会話順序を含む）
            audio_filename = f"conv_{i:03d}_{speaker}.wav"
            audio_path = os.path.join(output_dir, audio_filename)

            # 音声生成
            generated_path = self.generate_voice(
                text=text,
                speed=final_speed,
                pitch=final_pitch,
                intonation=final_intonation,
                output_path=audio_path,
                speaker=speaker,
            )

            if generated_path:
                audio_paths.append(generated_path)
                logger.info(
                    f"Generated conversation voice {i}: {speaker} - {generated_path}"
                )
            else:
                logger.warning(
                    f"Failed to generate voice for conversation {i}: {speaker}"
                )

        return audio_paths

