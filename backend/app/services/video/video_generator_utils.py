"""動画生成ユーティリティ関数"""

import os
from typing import List, Dict
from moviepy import VideoFileClip
from app.models.scripts.common import VideoSection


def combine_video_with_audio(
    temp_video_path: str, combined_audio, output_path: str
) -> str:
    """動画と音声を結合する"""
    video_clip = VideoFileClip(temp_video_path)

    video_duration = video_clip.duration
    audio_duration = combined_audio.duration
    duration_diff = abs(video_duration - audio_duration)

    if duration_diff > 0.001:
        video_clip = video_clip.with_duration(audio_duration)

    final_clip = video_clip.with_audio(combined_audio)

    final_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        ffmpeg_params=["-crf", "23", "-preset", "fast", "-threads", "4"],
        verbose=False,
        logger=None,
    )

    video_clip.close()
    final_clip.close()

    del video_clip
    del final_clip

    return output_path


def calculate_section_durations(
    sections: List[VideoSection],
    audio_durations: Dict[str, float],
    audio_file_list: List[str],
) -> List[float]:
    """各セクションの長さを計算する"""
    section_durations = []
    current_segment_index = 0

    for section in sections:
        segment_count = len(section.segments)
        section_audio_files = audio_file_list[
            current_segment_index : current_segment_index + segment_count
        ]
        section_duration = sum(
            audio_durations.get(audio_path, 0.0) for audio_path in section_audio_files
        )
        section_durations.append(section_duration)
        current_segment_index += segment_count

    return section_durations
