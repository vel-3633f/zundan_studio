import os
from app.utils_legacy.constants import Constants


class PathManager:
    @staticmethod
    def get_project_root() -> str:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(current_dir))

    @classmethod
    def get_temp_dir(cls) -> str:
        return os.path.join(cls.get_project_root(), Constants.TEMP_DIR)

    @classmethod
    def get_outputs_dir(cls) -> str:
        return os.path.join(cls.get_project_root(), Constants.OUTPUTS_DIR)

    @classmethod
    def get_required_directories(cls) -> list[str]:
        base_dir = cls.get_project_root()
        return [
            os.path.join(base_dir, Constants.TEMP_DIR),
            os.path.join(base_dir, Constants.OUTPUTS_DIR),
            os.path.join(base_dir, Constants.ASSETS_DIR, Constants.ZUNDAMON_DIR),
            os.path.join(base_dir, Constants.ASSETS_DIR, Constants.BACKGROUNDS_DIR),
        ]
