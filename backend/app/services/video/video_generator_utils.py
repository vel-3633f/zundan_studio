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
        ffmpeg_params=["-crf", "18", "-preset", "medium"],
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
    import logging
    logger = logging.getLogger(__name__)
    
    section_durations = []
    current_segment_index = 0
    
    total_segments = sum(len(section.segments) for section in sections)
    logger.info(
        f"calculate_section_durations: "
        f"セクション数={len(sections)}, "
        f"総セグメント数={total_segments}, "
        f"音声ファイル数={len(audio_file_list)}"
    )

    for i, section in enumerate(sections):
        segment_count = len(section.segments)
        if current_segment_index + segment_count > len(audio_file_list):
            logger.error(
                f"セクション{i} ({section.section_name}): "
                f"インデックス範囲外エラー "
                f"(current_segment_index={current_segment_index}, "
                f"segment_count={segment_count}, "
                f"audio_file_list長さ={len(audio_file_list)})"
            )
            # 残りの音声ファイルをすべて使用
            section_audio_files = audio_file_list[current_segment_index:]
        else:
            section_audio_files = audio_file_list[
                current_segment_index : current_segment_index + segment_count
            ]
        
        section_duration = sum(
            audio_durations.get(audio_path, 0.0)
            for audio_path in section_audio_files
        )
        section_durations.append(section_duration)
        logger.info(
            f"セクション{i} ({section.section_name}): "
            f"セグメント数={segment_count}, "
            f"音声ファイル数={len(section_audio_files)}, "
            f"長さ={section_duration:.2f}秒"
        )
        current_segment_index += segment_count

    return section_durations

