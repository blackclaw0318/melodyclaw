#!/usr/bin/env python3
"""
MelodyClaw Phase 1 - Silero VAD Test
Tests Silero Voice Activity Detection model
Target: 4c16g CPU server
"""

import os
import sys
import time
import torch
import psutil
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

# Configure for CPU-only
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

def get_memory_mb():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_silero_vad():
    """Test Silero VAD model"""
    logger.info("=" * 50)
    logger.info("Silero VAD (Voice Activity Detection) Test")
    logger.info("=" * 50)
    
    initial_memory = get_memory_mb()
    logger.info(f"Initial memory: {initial_memory:.1f} MB")
    
    # Load Silero VAD
    logger.info("Loading Silero VAD model...")
    load_start = time.time()
    
    try:
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
    except Exception as e:
        logger.error(f"Failed to load Silero VAD: {e}")
        return False
    
    load_time = time.time() - load_start
    model_memory = get_memory_mb()
    logger.info(f"Model loaded in {load_time:.2f}s")
    logger.info(f"Memory after load: {model_memory:.1f} MB (+{model_memory - initial_memory:.1f} MB)")
    
    # Get utility functions
    get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks = utils
    
    # Create test audio (simulated speech pattern)
    logger.info("Creating test audio (simulated speech)...")
    sample_rate = 16000  # Silero VAD requires 16kHz or 8kHz
    test_duration = 10  # seconds
    
    # Create a simple test signal with some "speech" segments
    test_audio = torch.zeros(sample_rate * test_duration)
    
    # Add some simulated speech segments (random noise in certain ranges)
    torch.manual_seed(42)
    speech_segments = [
        (1 * sample_rate, 3 * sample_rate),   # 1-3s
        (5 * sample_rate, 7 * sample_rate),   # 5-7s
        (8 * sample_rate, 9 * sample_rate),   # 8-9s
    ]
    
    for start, end in speech_segments:
        test_audio[start:end] = torch.randn(end - start) * 0.5
    
    # Run VAD
    logger.info("Running VAD detection...")
    vad_start = time.time()
    
    # Convert to appropriate format for Silero
    speech_timestamps = get_speech_timestamps(
        test_audio,
        model,
        sampling_rate=sample_rate,
        min_speech_duration_ms=500,
        min_silence_duration_ms=300,
    )
    
    vad_time = time.time() - vad_start
    final_memory = get_memory_mb()
    
    logger.info(f"VAD completed in {vad_time:.2f}s")
    logger.info(f"Detected {len(speech_timestamps)} speech segments")
    
    for i, segment in enumerate(speech_timestamps):
        start_sec = segment['start'] / sample_rate
        end_sec = segment['end'] / sample_rate
        logger.info(f"  Segment {i+1}: {start_sec:.2f}s - {end_sec:.2f}s")
    
    logger.info(f"Memory after VAD: {final_memory:.1f} MB")
    logger.info(f"Total memory increase: {final_memory - initial_memory:.1f} MB")
    
    # Cleanup
    del model, test_audio
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    logger.info("Test completed successfully!")
    
    return {
        'load_time': load_time,
        'vad_time': vad_time,
        'segments_detected': len(speech_timestamps),
        'memory_increase': final_memory - initial_memory,
        'success': True
    }

if __name__ == "__main__":
    results = test_silero_vad()
    
    # Save results
    results_file = Path(__file__).parent / "results_silero_vad.json"
    import json
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")
