from typing import Tuple
from app.utils_legacy.constants import Constants


class TextValidator:
    @staticmethod
    def validate_text_input(
        text: str, max_length: int = Constants.MAX_TEXT_LENGTH
    ) -> Tuple[bool, str]:
        if not text or not text.strip():
            return False, "テキストを入力してください"

        if len(text) > max_length:
            return False, f"テキストは{max_length}文字以内で入力してください"

        return True, ""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        for char in Constants.INVALID_FILENAME_CHARS:
            filename = filename.replace(char, "_")
        return filename[: Constants.MAX_FILENAME_LENGTH]
