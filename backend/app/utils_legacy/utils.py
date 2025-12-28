from typing import Optional, Tuple, Dict

from app.utils_legacy.constants import Constants
from app.utils_legacy.files import FileManager, FileOperations
from app.utils_legacy.validators import TextValidator
from app.utils_legacy.logging_config import LoggingConfig


def setup_logging(debug: bool = False):
    LoggingConfig.setup_logging(debug)


def generate_unique_filename(
    prefix: str = Constants.DEFAULT_PREFIX, extension: str = Constants.DEFAULT_EXTENSION
) -> str:
    return FileManager.generate_unique_filename(prefix, extension)


def cleanup_temp_files(temp_dir: str = None):
    return FileManager.cleanup_temp_files(temp_dir)


def cleanup_all_generated_files():
    return FileManager.cleanup_all_generated_files()


def get_generated_files_info():
    return FileManager.get_generated_files_info()


def ensure_directories():
    FileManager.ensure_directories()


def get_file_size_mb(file_path: str) -> Optional[float]:
    return FileManager.get_file_size_mb(file_path)


def validate_text_input(
    text: str, max_length: int = Constants.MAX_TEXT_LENGTH
) -> Tuple[bool, str]:
    return TextValidator.validate_text_input(text, max_length)


def sanitize_filename(filename: str) -> str:
    return TextValidator.sanitize_filename(filename)


__all__ = [
    "Constants",
    "FileManager",
    "FileOperations",
    "TextValidator",
    "LoggingConfig",
    "setup_logging",
    "generate_unique_filename",
    "cleanup_temp_files",
    "cleanup_all_generated_files",
    "get_generated_files_info",
    "ensure_directories",
    "get_file_size_mb",
    "validate_text_input",
    "sanitize_filename",
]
