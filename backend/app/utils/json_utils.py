from typing import Dict, Any, List


def extract_background_names_from_json(json_data: Dict[str, Any]) -> List[str]:
    background_names = set()

    if json_data.get("sections") and isinstance(json_data["sections"], list):
        for section in json_data["sections"]:
            if section.get("scene_background"):
                background_names.add(section["scene_background"])

    return list(background_names)

