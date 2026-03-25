# MelodyClaw Phase 1 - Environment Setup Guide

## System Requirements

- **OS:** Ubuntu 20.04+ (tested on 4c16g server)
- **CPU:** 4+ cores (8+ recommended)
- **RAM:** 16GB minimum
- **GPU:** Not required (CPU inference supported)
- **Python:** 3.10+
- **Storage:** 10GB+ free space for models

## Quick Start

### 1. Setup Environment

```bash
# Run setup script
chmod +x setup_env.sh
./setup_env.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Install RVC Dependencies (Optional)

```bash
pip install -r requirements-rvc.txt
```

### 3. Run Tests

```bash
chmod +x run_phase1_tests.sh
./run_phase1_tests.sh
```

## Model Download Locations

Models will be automatically downloaded on first use:

| Model | Size | Location |
|-------|------|----------|
| Demucs htdemucs_ft | ~800MB | `~/.cache/torch/hub` |
| Silero VAD | ~50MB | `~/.cache/torch/hub` |
| Hubert (RVC) | ~200MB | `~/.cache/melodyclaw/` |

## Memory Optimization

For 16GB systems, use **sequential model loading**:

```python
# Load model 1
model1 = load_demucs()
process_audio()
del model1  # Unload
gc.collect()

# Load model 2
model2 = load_silero()
process_audio()
del model2
gc.collect()
```

**DO NOT** load all models simultaneously on 16GB systems.

## Troubleshooting

### Out of Memory (OOM)

1. Close other applications
2. Use sequential loading (see above)
3. Reduce audio duration for testing

### Model Download Failed

```bash
# Clear cache and retry
rm -rf ~/.cache/torch/hub/snakers4_silero-vad
python tests/test_silero_vad.py
```

### fairseq Installation Failed

```bash
# Try with no build isolation
pip install --no-build-isolation fairseq==0.12.2
```

## Performance Benchmarks

Expected performance on 4c16g CPU server:

| Model | Load Time | RTF (Real-time Factor) |
|-------|-----------|------------------------|
| Demucs | ~10s | 0.5-1.0x |
| Silero VAD | ~5s | 0.1x |
| Hubert | ~3s | 0.3x |

*RTF < 1.0 means faster than real-time*

## Next Steps

After Phase 1 tests pass:

1. Review test results in `tests/results/`
2. Proceed to Phase 2: Backend API Development
3. See `../README.md` for project overview
