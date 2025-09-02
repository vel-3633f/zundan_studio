import os
import logging
import uuid
from datetime import datetime
from typing import Optional


def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # 特定のライブラリのログレベルを制御
    if not debug:
        # MoviePyなどのサードパーティライブラリのログを抑制
        logging.getLogger("moviepy").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)


def generate_unique_filename(prefix: str = "output", extension: str = "mp4") -> str:
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{timestamp}_{unique_id}.{extension}"


def cleanup_temp_files(temp_dir: str = None):
    """Clean up temporary files"""
    if temp_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_dir = os.path.join(base_dir, "temp")

    if not os.path.exists(temp_dir):
        return

    try:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f"Cleaned up temp file: {filename}")
    except Exception as e:
        logging.error(f"Failed to cleanup temp files: {e}")


def cleanup_all_generated_files():
    """Clean up all generated files (temp and outputs)"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Clean temp directory
    temp_dir = os.path.join(base_dir, "temp")
    if os.path.exists(temp_dir):
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f"Cleaned up temp file: {filename}")
        except Exception as e:
            logging.error(f"Failed to cleanup temp files: {e}")

    # Clean outputs directory
    outputs_dir = os.path.join(base_dir, "outputs")
    if os.path.exists(outputs_dir):
        try:
            for filename in os.listdir(outputs_dir):
                file_path = os.path.join(outputs_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f"Cleaned up output file: {filename}")
        except Exception as e:
            logging.error(f"Failed to cleanup output files: {e}")


def get_generated_files_info():
    """Get information about generated files"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    temp_count = 0
    temp_size = 0
    output_count = 0
    output_size = 0

    # Count temp files
    temp_dir = os.path.join(base_dir, "temp")
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                temp_count += 1
                temp_size += os.path.getsize(file_path)

    # Count output files
    outputs_dir = os.path.join(base_dir, "outputs")
    if os.path.exists(outputs_dir):
        for filename in os.listdir(outputs_dir):
            file_path = os.path.join(outputs_dir, filename)
            if os.path.isfile(file_path):
                output_count += 1
                output_size += os.path.getsize(file_path)

    return {
        "temp_count": temp_count,
        "temp_size_mb": temp_size / (1024 * 1024),
        "output_count": output_count,
        "output_size_mb": output_size / (1024 * 1024),
        "total_count": temp_count + output_count,
        "total_size_mb": (temp_size + output_size) / (1024 * 1024),
    }


def ensure_directories():
    """Ensure required directories exist"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directories = [
        os.path.join(base_dir, "temp"),
        os.path.join(base_dir, "outputs"),
        os.path.join(base_dir, "assets", "zundamon"),
        os.path.join(base_dir, "assets", "backgrounds"),
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_file_size_mb(file_path: str) -> Optional[float]:
    """Get file size in MB"""
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path) / (1024 * 1024)
        return None
    except Exception:
        return None


def validate_text_input(text: str, max_length: int = 1000) -> tuple[bool, str]:
    """Validate text input"""
    if not text or not text.strip():
        return False, "テキストを入力してください"

    if len(text) > max_length:
        return False, f"テキストは{max_length}文字以内で入力してください"

    return True, ""


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename[:255]  # Limit length
