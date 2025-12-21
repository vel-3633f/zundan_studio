import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Tuple
from app.utils_legacy.constants import Constants
from app.utils_legacy.paths import PathManager
from app.utils_legacy.logger import get_logger

logger = get_logger(__name__)


class FileOperations:
    @staticmethod
    def delete_file_safe(file_path: str, file_type: str = "file") -> bool:
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
    @staticmethod
    def generate_unique_filename(
        prefix: str = Constants.DEFAULT_PREFIX,
        extension: str = Constants.DEFAULT_EXTENSION,
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"

    @staticmethod
    def cleanup_temp_files(temp_dir: str = None) -> int:
        if temp_dir is None:
            temp_dir = PathManager.get_temp_dir()

        return FileOperations.cleanup_directory(temp_dir, "temp")

    @staticmethod
    def cleanup_all_generated_files() -> int:
        total_deleted = 0

        temp_deleted = FileOperations.cleanup_directory(
            PathManager.get_temp_dir(), "temp"
        )
        total_deleted += temp_deleted

        output_deleted = FileOperations.cleanup_directory(
            PathManager.get_outputs_dir(), "output"
        )
        total_deleted += output_deleted

        logger.info(f"Total cleanup completed. Deleted {total_deleted} files.")
        return total_deleted

    @staticmethod
    def get_generated_files_info() -> Dict[str, float]:
        temp_count, temp_size = FileOperations.count_files_in_directory(
            PathManager.get_temp_dir()
        )

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
        directories = PathManager.get_required_directories()
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    @staticmethod
    def get_file_size_mb(file_path: str) -> Optional[float]:
        try:
            if os.path.exists(file_path):
                return os.path.getsize(file_path) / (1024 * 1024)
            return None
        except Exception:
            return None
