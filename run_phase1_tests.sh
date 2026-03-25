#!/bin/bash
# MelodyClaw Phase 1 - Run All Tests
# For 4c16g Ubuntu server

set -e

echo "=== MelodyClaw Phase 1 Tests ==="
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found. Run setup_env.sh first."
    exit 1
fi

source venv/bin/activate

# Create results directory
mkdir -p tests/results

# Run tests
echo "[1/4] Testing Demucs vocal separation..."
python tests/test_demucs.py 2>&1 | tee tests/results/demucs.log || echo "Demucs test failed"

echo ""
echo "[2/4] Testing Silero VAD..."
python tests/test_silero_vad.py 2>&1 | tee tests/results/silero.log || echo "Silero test failed"

echo ""
echo "[3/4] Testing RVC v2..."
python tests/test_rvc.py 2>&1 | tee tests/results/rvc.log || echo "RVC test failed"

echo ""
echo "[4/4] Running memory pressure test..."
python tests/test_memory.py 2>&1 | tee tests/results/memory.log || echo "Memory test failed"

echo ""
echo "=== All Tests Complete ==="
echo "Results saved in tests/results/"
