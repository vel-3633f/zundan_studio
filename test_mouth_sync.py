#!/usr/bin/env python3
"""口パク機能のテストスクリプト"""
import logging
import sys
from src.core.audio_processor import AudioProcessor

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_audio_analysis():
    """音声解析のテスト"""
    import glob

    # tempディレクトリ内の音声ファイルを探す
    audio_files = glob.glob("temp/*.wav")

    if not audio_files:
        logger.error("No audio files found in temp directory")
        logger.info("Please generate a video first to create audio files")
        return

    logger.info(f"Found {len(audio_files)} audio files")

    # AudioProcessorのインスタンス化
    processor = AudioProcessor(fps=30)

    # 各音声ファイルを解析
    for audio_path in audio_files[:3]:  # 最初の3つだけテスト
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {audio_path}")
        logger.info(f"{'='*60}")

        intensities, duration = processor.analyze_audio_for_mouth_sync(audio_path)

        if intensities:
            logger.info(f"Duration: {duration:.3f}s")
            logger.info(f"Frames: {len(intensities)}")
            logger.info(f"Max intensity: {max(intensities):.3f}")
            logger.info(f"Min intensity: {min(intensities):.3f}")
            logger.info(f"Avg intensity: {sum(intensities)/len(intensities):.3f}")

            # 強度分布を確認
            high_count = sum(1 for i in intensities if i >= 0.4)
            medium_count = sum(1 for i in intensities if 0.1 <= i < 0.4)
            low_count = sum(1 for i in intensities if i < 0.1)

            logger.info(f"\nIntensity distribution:")
            logger.info(f"  High (>= 0.4): {high_count}/{len(intensities)} ({100*high_count/len(intensities):.1f}%)")
            logger.info(f"  Medium (0.1-0.4): {medium_count}/{len(intensities)} ({100*medium_count/len(intensities):.1f}%)")
            logger.info(f"  Low (< 0.1): {low_count}/{len(intensities)} ({100*low_count/len(intensities):.1f}%)")

            # 最初の10フレームの値を表示
            logger.info(f"\nFirst 10 frame intensities:")
            for i, intensity in enumerate(intensities[:10]):
                logger.info(f"  Frame {i}: {intensity:.3f}")
        else:
            logger.error(f"Failed to analyze: {audio_path}")

if __name__ == "__main__":
    test_audio_analysis()
