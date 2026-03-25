#!/usr/bin/env python3
"""
MelodyClaw Phase 1 - RVC v2 Test
Tests RVC v2 (Retrieval-based Voice Conversion) model
Target: 4c16g CPU server

Note: RVC requires additional dependencies not in main requirements.txt
Install with: pip install -r requirements-rvc.txt
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

def test_rvc_model():
    """Test RVC v2 model loading and inference"""
    logger.info("=" * 50)
    logger.info("RVC v2 (Voice Conversion) Test")
    logger.info("=" * 50)
    
    initial_memory = get_memory_mb()
    logger.info(f"Initial memory: {initial_memory:.1f} MB")
    
    # Try to import RVC dependencies
    logger.info("Checking RVC dependencies...")
    
    missing_deps = []
    try:
        import fairseq
        logger.info("  ✓ fairseq")
    except ImportError:
        missing_deps.append("fairseq")
        logger.warning("  ✗ fairseq (not installed)")
    
    try:
        import fairseq
        from fairseq import checkpoint_utils
        logger.info("  ✓ fairseq checkpoint_utils")
    except ImportError:
        missing_deps.append("fairseq.checkpoint_utils")
        logger.warning("  ✗ fairseq.checkpoint_utils")
    
    try:
        import librosa
        logger.info("  ✓ librosa")
    except ImportError:
        missing_deps.append("librosa")
        logger.warning("  ✗ librosa (not installed)")
    
    try:
        import numpy as np
        logger.info("  ✓ numpy")
    except ImportError:
        missing_deps.append("numpy")
        logger.warning("  ✗ numpy")
    
    if missing_deps:
        logger.warning(f"\nMissing dependencies: {', '.join(missing_deps)}")
        logger.warning("Install with: pip install fairseq librosa")
        logger.warning("\nRVC model loading test SKIPPED (dependencies not available)")
        
        return {
            'load_time': 0,
            'infer_time': 0,
            'memory_increase': 0,
            'success': False,
            'reason': 'missing_dependencies',
            'missing': missing_deps
        }
    
    # Load Hubert model (required by RVC)
    logger.info("\nLoading Hubert model (RVC backbone)...")
    load_start = time.time()
    
    try:
        # Hubert model URL
        hubert_url = "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt"
        hubert_path = Path.home() / ".cache" / "melodyclaw" / "hubert_base.pt"
        hubert_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not hubert_path.exists():
            logger.info(f"Downloading Hubert model to {hubert_path}...")
            import urllib.request
            urllib.request.urlretrieve(hubert_url, hubert_path)
        
        logger.info(f"Loading Hubert from {hubert_path}...")
        models, saved_cfg, task = checkpoint_utils.load_model_ensemble_and_task(
            [str(hubert_path)],
            suffix="",
        )
        hubert = models[0]
        hubert = hubert.to('cpu')
        hubert = hubert.eval()
        
    except Exception as e:
        logger.error(f"Failed to load Hubert model: {e}")
        return {
            'load_time': 0,
            'infer_time': 0,
            'memory_increase': 0,
            'success': False,
            'reason': str(e)
        }
    
    load_time = time.time() - load_start
    model_memory = get_memory_mb()
    logger.info(f"Hubert model loaded in {load_time:.2f}s")
    logger.info(f"Memory after load: {model_memory:.1f} MB (+{model_memory - initial_memory:.1f} MB)")
    
    # Test inference with dummy audio
    logger.info("\nRunning test inference...")
    test_duration = 3  # seconds
    sample_rate = 16000
    test_audio = torch.randn(1, sample_rate * test_duration)
    
    infer_start = time.time()
    
    with torch.no_grad():
        # Extract features using Hubert
        feats = hubert.extract_features(test_audio, padding_mask=None)
        if isinstance(feats, tuple):
            feats = feats[0]
    
    infer_time = time.time() - infer_start
    final_memory = get_memory_mb()
    
    logger.info(f"Inference completed in {infer_time:.2f}s")
    logger.info(f"Feature shape: {feats.shape}")
    logger.info(f"Memory after inference: {final_memory:.1f} MB")
    logger.info(f"Total memory increase: {final_memory - initial_memory:.1f} MB")
    
    # Cleanup
    del hubert, test_audio, feats
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    logger.info("\nTest completed successfully!")
    
    return {
        'load_time': load_time,
        'infer_time': infer_time,
        'memory_increase': final_memory - initial_memory,
        'success': True
    }

if __name__ == "__main__":
    results = test_rvc_model()
    
    # Save results
    results_file = Path(__file__).parent / "results_rvc.json"
    import json
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\nResults saved to {results_file}")
