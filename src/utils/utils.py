import os
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Tuple
import re
from typing import Dict, Optional, List
from src.models.food_over import ConversationSegment
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Constants:
    DEFAULT_PREFIX = "output"
    DEFAULT_EXTENSION = "mp4"
    MAX_TEXT_LENGTH = 1000
    MAX_FILENAME_LENGTH = 255
    INVALID_FILENAME_CHARS = '<>:"/\\|?*'

    # ディレクトリ名
    TEMP_DIR = "temp"
    OUTPUTS_DIR = "outputs"
    ASSETS_DIR = "assets"
    ZUNDAMON_DIR = "zundamon"
    BACKGROUNDS_DIR = "backgrounds"

    # ログ設定
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SUPPRESSED_LOGGERS = ["moviepy", "PIL", "matplotlib"]


class PathManager:
    """パス管理を担当するクラス"""

    @staticmethod
    def get_project_root() -> str:
        """プロジェクトルートディレクトリを取得"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(current_dir))

    @classmethod
    def get_temp_dir(cls) -> str:
        """一時ファイルディレクトリのパスを取得"""
        return os.path.join(cls.get_project_root(), Constants.TEMP_DIR)

    @classmethod
    def get_outputs_dir(cls) -> str:
        """出力ファイルディレクトリのパスを取得"""
        return os.path.join(cls.get_project_root(), Constants.OUTPUTS_DIR)

    @classmethod
    def get_required_directories(cls) -> list[str]:
        """必要なディレクトリのリストを取得"""
        base_dir = cls.get_project_root()
        return [
            os.path.join(base_dir, Constants.TEMP_DIR),
            os.path.join(base_dir, Constants.OUTPUTS_DIR),
            os.path.join(base_dir, Constants.ASSETS_DIR, Constants.ZUNDAMON_DIR),
            os.path.join(base_dir, Constants.ASSETS_DIR, Constants.BACKGROUNDS_DIR),
            os.path.join(base_dir, Constants.ASSETS_DIR, "items"),
            os.path.join(base_dir, Constants.ASSETS_DIR, "items", "drinks"),
            os.path.join(base_dir, Constants.ASSETS_DIR, "items", "books"),
            os.path.join(base_dir, Constants.ASSETS_DIR, "items", "tools"),
            os.path.join(base_dir, Constants.ASSETS_DIR, "items", "weapons"),
        ]


class FileOperations:
    """ファイル操作を担当するクラス"""

    @staticmethod
    def delete_file_safe(file_path: str, file_type: str = "file") -> bool:
        """安全にファイルを削除"""
        try:
            os.remove(file_path)
            filename = os.path.basename(file_path)
            logger.info(f"Cleaned up {file_type}: {filename}")
            return True
        except PermissionError:
            filename = os.path.basename(file_path)
            logger.warning(f"Permission denied for {file_type}: {filename}")
            return False
        except OSError as e:
            filename = os.path.basename(file_path)
            logger.warning(f"Could not delete {file_type} {filename}: {e}")
            return False

    @staticmethod
    def cleanup_directory(directory: str, dir_type: str) -> int:
        """指定されたディレクトリをクリーンアップ"""
        if not os.path.exists(directory):
            if dir_type == "temp":
                logger.info(f"Temp directory not found: {directory}")
            return 0

        deleted_count = 0
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    if FileOperations.delete_file_safe(file_path, f"{dir_type} file"):
                        deleted_count += 1

            logger.info(
                f"{dir_type.capitalize()} cleanup completed. Deleted {deleted_count} files."
            )
        except Exception as e:
            logger.error(f"Failed to cleanup {dir_type} files: {e}")

        return deleted_count

    @staticmethod
    def count_files_in_directory(directory: str) -> Tuple[int, int]:
        """ディレクトリ内のファイル数とサイズを取得"""
        count = 0
        total_size = 0

        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    count += 1
                    total_size += os.path.getsize(file_path)

        return count, total_size


class FileManager:
    """ファイル管理を担当するメインクラス"""

    @staticmethod
    def generate_unique_filename(
        prefix: str = Constants.DEFAULT_PREFIX,
        extension: str = Constants.DEFAULT_EXTENSION,
    ) -> str:
        """Generate unique filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"

    @staticmethod
    def cleanup_temp_files(temp_dir: str = None) -> int:
        """Clean up temporary files"""
        if temp_dir is None:
            temp_dir = PathManager.get_temp_dir()

        return FileOperations.cleanup_directory(temp_dir, "temp")

    @staticmethod
    def cleanup_all_generated_files() -> int:
        """Clean up all generated files (temp and outputs)"""
        total_deleted = 0

        # Clean temp directory
        temp_deleted = FileOperations.cleanup_directory(
            PathManager.get_temp_dir(), "temp"
        )
        total_deleted += temp_deleted

        # Clean outputs directory
        output_deleted = FileOperations.cleanup_directory(
            PathManager.get_outputs_dir(), "output"
        )
        total_deleted += output_deleted

        logger.info(f"Total cleanup completed. Deleted {total_deleted} files.")
        return total_deleted

    @staticmethod
    def get_generated_files_info() -> Dict[str, float]:
        """Get information about generated files"""
        # Count temp files
        temp_count, temp_size = FileOperations.count_files_in_directory(
            PathManager.get_temp_dir()
        )

        # Count output files
        output_count, output_size = FileOperations.count_files_in_directory(
            PathManager.get_outputs_dir()
        )

        return {
            "temp_count": temp_count,
            "temp_size_mb": temp_size / (1024 * 1024),
            "output_count": output_count,
            "output_size_mb": output_size / (1024 * 1024),
            "total_count": temp_count + output_count,
            "total_size_mb": (temp_size + output_size) / (1024 * 1024),
        }

    @staticmethod
    def ensure_directories():
        """Ensure required directories exist"""
        directories = PathManager.get_required_directories()
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def get_file_size_mb(file_path: str) -> Optional[float]:
        """Get file size in MB"""
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path) / (1024 * 1024)
            return None
        except Exception:
            return None


class TextValidator:
    """テキスト検証を担当するクラス"""

    @staticmethod
    def validate_text_input(
        text: str, max_length: int = Constants.MAX_TEXT_LENGTH
    ) -> Tuple[bool, str]:
        """Validate text input"""
        if not text or not text.strip():
            return False, "テキストを入力してください"

        if len(text) > max_length:
            return False, f"テキストは{max_length}文字以内で入力してください"

        return True, ""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations"""
        for char in Constants.INVALID_FILENAME_CHARS:
            filename = filename.replace(char, "_")
        return filename[: Constants.MAX_FILENAME_LENGTH]


class LoggingConfig:
    """ログ設定を担当するクラス"""

    @staticmethod
    def setup_logging(debug: bool = False):
        """Setup logging configuration"""
        level = logging.DEBUG if debug else logging.WARNING
        logging.basicConfig(
            level=level,
            format=Constants.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
            ],
        )

        if not debug:
            LoggingConfig._suppress_third_party_logs()

    @staticmethod
    def _suppress_third_party_logs():
        """サードパーティライブラリのログを抑制"""
        for logger_name in Constants.SUPPRESSED_LOGGERS:
            logging.getLogger(logger_name).setLevel(logging.WARNING)


def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    LoggingConfig.setup_logging(debug)


def generate_unique_filename(
    prefix: str = Constants.DEFAULT_PREFIX, extension: str = Constants.DEFAULT_EXTENSION
) -> str:
    """Generate unique filename with timestamp"""
    return FileManager.generate_unique_filename(prefix, extension)


def cleanup_temp_files(temp_dir: str = None):
    """Clean up temporary files"""
    return FileManager.cleanup_temp_files(temp_dir)


def cleanup_all_generated_files():
    """Clean up all generated files (temp and outputs)"""
    return FileManager.cleanup_all_generated_files()


def get_generated_files_info():
    """Get information about generated files"""
    return FileManager.get_generated_files_info()


def ensure_directories():
    """Ensure required directories exist"""
    FileManager.ensure_directories()


def get_file_size_mb(file_path: str) -> Optional[float]:
    """Get file size in MB"""
    return FileManager.get_file_size_mb(file_path)


def validate_text_input(
    text: str, max_length: int = Constants.MAX_TEXT_LENGTH
) -> Tuple[bool, str]:
    """Validate text input"""
    return TextValidator.validate_text_input(text, max_length)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    return TextValidator.sanitize_filename(filename)
