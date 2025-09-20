"""Data models for food generation components"""

from typing import Dict


class CharacterInfo:
    def __init__(self, name: str, display_name: str, personality: str):
        self.name = name
        self.display_name = display_name
        self.personality = personality


class ExpressionInfo:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name


class Characters:
    _characters = {
        "zundamon": CharacterInfo(
            "zundamon", "ずんだもん", "東北地方の妖精、語尾に「〜のだ」「〜なのだ」"
        ),
        "metan": CharacterInfo("metan", "四国めたん", "ツッコミ役、常識的で冷静な性格"),
        "tsumugi": CharacterInfo(
            "tsumugi", "春日部つむぎ", "素朴で純粋、疑問をよく投げかける"
        ),
        "narrator": CharacterInfo("narrator", "ナレーター", "客観的で落ち着いた解説役"),
    }

    @classmethod
    def get_display_name(cls, name: str) -> str:
        char = cls._characters.get(name)
        return char.display_name if char else name


class Expressions:
    _expressions = {
        "normal": ExpressionInfo("normal", "通常"),
        "happy": ExpressionInfo("happy", "喜び"),
        "sad": ExpressionInfo("sad", "悲しみ"),
        "angry": ExpressionInfo("angry", "怒り"),
        "surprised": ExpressionInfo("surprised", "驚き"),
        "thinking": ExpressionInfo("thinking", "考え中"),
        "worried": ExpressionInfo("worried", "心配"),
        "excited": ExpressionInfo("excited", "興奮"),
        "sick": ExpressionInfo("sick", "体調不良"),
    }

    @classmethod
    def get_display_name(cls, name: str) -> str:
        expr = cls._expressions.get(name)
        return expr.display_name if expr else name
