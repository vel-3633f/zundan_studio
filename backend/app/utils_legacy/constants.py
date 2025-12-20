class Constants:
    DEFAULT_PREFIX = "output"
    DEFAULT_EXTENSION = "mp4"
    MAX_TEXT_LENGTH = 1000
    MAX_FILENAME_LENGTH = 255
    INVALID_FILENAME_CHARS = '<>:"/\\|?*'

    TEMP_DIR = "temp"
    OUTPUTS_DIR = "outputs"
    ASSETS_DIR = "assets"
    ZUNDAMON_DIR = "zundamon"
    BACKGROUNDS_DIR = "backgrounds"

    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SUPPRESSED_LOGGERS = ["moviepy", "PIL", "matplotlib"]
