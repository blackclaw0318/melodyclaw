#!/usr/bin/env python3
"""
MelodyClaw Phase 1 - Demucs Vocal Separation Test
Tests htdemucs_ft model for vocal/instrumental separation
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

def test_demucs_model():
    """Test Demucs vocal separation model"""
    logger.info("=" * 50)
    logger.info("Demucs Vocal Separation Test")
    logger.info("=" * 50)
    
    initial_memory = get_memory_mb()
    logger.info(f"Initial memory: {initial_memory:.1f} MB")
    
    # Import demucs
    logger.info("Loading Demucs library...")
    from demucs.pretrained import get_model
    from demucs.audio import save_audio
    from demucs.apply import apply_model
    from torch import nn
    
    # Load model
    logger.info("Loading htdemucs_ft model (this may take a while)...")
    load_start = time.time()
    
    try:
        model = get_model('htdemucs_ft')
        model = model.to('cpu')
        model = model.eval()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False
    
    load_time = time.time() - load_start
    model_memory = get_memory_mb()
    logger.info(f"Model loaded in {load_time:.2f}s")
    logger.info(f"Memory after load: {model_memory:.1f} MB (+{model_memory - initial_memory:.1f} MB)")
    
    # Create test audio (silent, just to test the pipeline)
    logger.info("Creating test audio tensor...")
    test_duration = 5  # seconds
    sample_rate = 44100
    test_audio = torch.zeros(1, 2, sample_rate * test_duration)  # stereo, 5 seconds
    
    # Run separation
    logger.info(f"Running separation on {test_duration}s test audio...")
    infer_start = time.time()
    
    with torch.no_grad():
        refs = model.reference_audio
        if refs is not None:
            refs = refs.to('cpu')
        
        # Apply model
        out = apply_model(model, test_audio, device='cpu', split=True)
    
    infer_time = time.time() - infer_start
    final_memory = get_memory_mb()
    
    logger.info(f"Inference completed in {infer_time:.2f}s")
    logger.info(f"Output shape: {out.shape}")
    logger.info(f"Memory after inference: {final_memory:.1f} MB")
    logger.info(f"Total memory increase: {final_memory - initial_memory:.1f} MB")
    
    # Calculate throughput
    audio_duration = test_duration
    rtf = infer_time / audio_duration
    logger.info(f"Real-time factor: {rtf:.2f}x (lower is better)")
    
    # Cleanup
    del model, out, test_audio
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    logger.info("Test completed successfully!")
    
    return {
        'load_time': load_time,
        'infer_time': infer_time,
        'rtf': rtf,
        'memory_increase': final_memory - initial_memory,
        'success': True
    }

if __name__ == "__main__":
    results = test_demucs_model()
    
    # Save results
    results_file = Path(__file__).parent / "results_demucs.json"
    import json
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")
