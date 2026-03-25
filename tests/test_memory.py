#!/usr/bin/env python3
"""
MelodyClaw Phase 1 - Memory Pressure Test
Tests model loading strategies on 16GB RAM server
Target: 4c16g CPU server (16GB RAM, no GPU)
"""

import os
import sys
import time
import gc
import torch
import psutil
from pathlib import Path
from loguru import logger
from typing import Dict, List

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

# Configure for CPU-only
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

def get_memory_mb():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def get_system_memory():
    """Get system memory info"""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total / 1024 / 1024 / 1024,
        'available': mem.available / 1024 / 1024 / 1024,
        'used': mem.used / 1024 / 1024 / 1024,
        'percent': mem.percent
    }

def test_sequential_loading():
    """Test loading models one at a time (recommended strategy)"""
    logger.info("=" * 60)
    logger.info("Memory Test: Sequential Model Loading")
    logger.info("=" * 60)
    
    system_mem = get_system_memory()
    logger.info(f"System: {system_mem['total']:.1f}GB total, {system_mem['available']:.1f}GB available")
    
    initial_process_mem = get_memory_mb()
    logger.info(f"Process memory: {initial_process_mem:.1f} MB")
    logger.info("")
    
    models_to_test = [
        ('Demucs htdemucs_ft', 'demucs_htdemucs_ft', '~800MB'),
        ('Silero VAD', 'silero_vad', '~50MB'),
        ('Hubert (RVC)', 'hubert_base', '~200MB'),
    ]
    
    results = []
    peak_memory = initial_process_mem
    
    for model_name, model_id, expected_size in models_to_test:
        logger.info(f"Loading: {model_name} (expected: {expected_size})")
        
        before_load = get_memory_mb()
        
        try:
            if model_id == 'demucs_htdemucs_ft':
                from demucs.pretrained import get_model
                model = get_model('htdemucs_ft')
                model = model.to('cpu')
                model = model.eval()
            elif model_id == 'silero_vad':
                model, utils = torch.hub.load(
                    'snakers4/silero-vad', 'silero_vad',
                    force_reload=False, trust_repo=True
                )
            elif model_id == 'hubert_base':
                from fairseq import checkpoint_utils
                hubert_path = Path.home() / ".cache" / "melodyclaw" / "hubert_base.pt"
                if hubert_path.exists():
                    models, _, _ = checkpoint_utils.load_model_ensemble_and_task(
                        [str(hubert_path)], suffix=""
                    )
                    model = models[0].to('cpu').eval()
                else:
                    logger.warning("  Hubert model not found, skipping")
                    results.append({
                        'model': model_name,
                        'status': 'skipped',
                        'reason': 'model_not_found'
                    })
                    continue
            else:
                logger.warning(f"  Unknown model: {model_id}")
                continue
            
            after_load = get_memory_mb()
            memory_used = after_load - before_load
            peak_memory = max(peak_memory, after_load)
            
            logger.info(f"  ✓ Loaded: +{memory_used:.1f} MB")
            
            results.append({
                'model': model_name,
                'status': 'success',
                'memory_used': memory_used
            })
            
            # Simulate some work
            time.sleep(0.5)
            
            # Unload model
            del model
            gc.collect()
            
            after_unload = get_memory_mb()
            logger.info(f"  Unloaded: {after_unload:.1f} MB (freed ~{after_load - after_unload:.1f} MB)")
            logger.info("")
            
        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")
            results.append({
                'model': model_name,
                'status': 'failed',
                'error': str(e)
            })
            logger.info("")
    
    final_process_mem = get_memory_mb()
    system_mem_end = get_system_memory()
    
    logger.info("=" * 60)
    logger.info("Sequential Loading Summary")
    logger.info("=" * 60)
    logger.info(f"Initial process memory: {initial_process_mem:.1f} MB")
    logger.info(f"Peak process memory: {peak_memory:.1f} MB (+{peak_memory - initial_process_mem:.1f} MB)")
    logger.info(f"Final process memory: {final_process_mem:.1f} MB")
    logger.info(f"System available: {system_mem_end['available']:.1f}GB ({system_mem_end['percent']:.1f}% used)")
    
    return {
        'test_type': 'sequential',
        'initial_memory': initial_process_mem,
        'peak_memory': peak_memory,
        'final_memory': final_process_mem,
        'system_available_gb': system_mem_end['available'],
        'results': results
    }

def test_concurrent_loading():
    """Test loading all models at once (NOT recommended for 16GB)"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("Memory Test: Concurrent Model Loading (NOT recommended)")
    logger.info("=" * 60)
    
    system_mem = get_system_memory()
    logger.info(f"System: {system_mem['total']:.1f}GB total, {system_mem['available']:.1f}GB available")
    
    initial_process_mem = get_memory_mb()
    logger.info(f"Process memory: {initial_process_mem:.1f} MB")
    logger.info("")
    
    loaded_models = []
    
    try:
        # Load Demucs
        logger.info("Loading Demucs...")
        from demucs.pretrained import get_model
        demucs = get_model('htdemucs_ft').to('cpu').eval()
        loaded_models.append(('Demucs', demucs))
        logger.info(f"  Memory: {get_memory_mb():.1f} MB")
        
        # Load Silero VAD
        logger.info("Loading Silero VAD...")
        silero, _ = torch.hub.load('snakers4/silero-vad', 'silero_vad', force_reload=False)
        loaded_models.append(('Silero', silero))
        logger.info(f"  Memory: {get_memory_mb():.1f} MB")
        
        # Load Hubert (if available)
        hubert_path = Path.home() / ".cache" / "melodyclaw" / "hubert_base.pt"
        if hubert_path.exists():
            logger.info("Loading Hubert...")
            from fairseq import checkpoint_utils
            models, _, _ = checkpoint_utils.load_model_ensemble_and_task([str(hubert_path)])
            hubert = models[0].to('cpu').eval()
            loaded_models.append(('Hubert', hubert))
            logger.info(f"  Memory: {get_memory_mb():.1f} MB")
        
        peak_memory = get_memory_mb()
        logger.info("")
        logger.info(f"Peak memory (all models loaded): {peak_memory:.1f} MB")
        logger.info(f"Memory increase: {peak_memory - initial_process_mem:.1f} MB")
        
        # Check if we're close to system limit
        system_mem_end = get_system_memory()
        if system_mem_end['available'] < 2.0:  # Less than 2GB free
            logger.warning("⚠️  WARNING: Less than 2GB system memory available!")
            logger.warning("   This may cause OOM errors during inference")
        
        # Cleanup
        logger.info("\nUnloading all models...")
        for name, model in loaded_models:
            del model
        gc.collect()
        
        final_memory = get_memory_mb()
        logger.info(f"Final memory: {final_memory:.1f} MB (freed {peak_memory - final_memory:.1f} MB)")
        
        return {
            'test_type': 'concurrent',
            'initial_memory': initial_process_mem,
            'peak_memory': peak_memory,
            'final_memory': final_memory,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Concurrent loading failed: {e}")
        
        # Cleanup on error
        for name, model in loaded_models:
            del model
        gc.collect()
        
        return {
            'test_type': 'concurrent',
            'initial_memory': initial_process_mem,
            'peak_memory': get_memory_mb(),
            'final_memory': get_memory_mb(),
            'success': False,
            'error': str(e)
        }

def main():
    """Run all memory tests"""
    logger.info("=" * 60)
    logger.info("MelodyClaw Phase 1 - Memory Pressure Test")
    logger.info("Target: 4c16g Ubuntu Server (16GB RAM, CPU only)")
    logger.info("=" * 60)
    logger.info("")
    
    results = {
        'sequential': test_sequential_loading(),
        'concurrent': test_concurrent_loading()
    }
    
    # Save results
    results_file = Path(__file__).parent / "results_memory.json"
    import json
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("FINAL RECOMMENDATIONS")
    logger.info("=" * 60)
    
    seq_peak = results['sequential']['peak_memory']
    con_peak = results['concurrent']['peak_memory']
    
    logger.info(f"Sequential peak: {seq_peak:.1f} MB")
    logger.info(f"Concurrent peak: {con_peak:.1f} MB")
    
    if seq_peak < 8000:  # Less than 8GB
        logger.info("✓ Sequential loading is SAFE for 16GB system")
    else:
        logger.warning("⚠️  Sequential loading may be risky on 16GB system")
    
    if con_peak > 12000:  # More than 12GB
        logger.warning("⚠️  Concurrent loading is NOT recommended (uses too much memory)")
    
    logger.info("")
    logger.info("Recommended strategy:")
    logger.info("  1. Load models one at a time")
    logger.info("  2. Unload previous model before loading next")
    logger.info("  3. Use gc.collect() after unloading")
    logger.info("  4. Monitor system memory during long operations")
    logger.info("")
    logger.info(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()
