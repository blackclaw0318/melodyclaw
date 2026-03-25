#!/bin/bash
# MelodyClaw Phase 1 - Environment Setup Script
# For 4c16g Ubuntu server (4 core, 16GB RAM, no GPU)

set -e

echo "=== MelodyClaw Phase 1 Environment Setup ==="
echo "Host: 4c16g Ubuntu Server (CPU only)"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python3 --version
if ! python3 -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'; then
    echo "ERROR: Python 3.10+ required"
    exit 1
fi

# Create virtual environment
echo "[2/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "[3/5] Upgrading pip..."
pip install --upgrade pip

# Install base dependencies
echo "[4/5] Installing base dependencies (FastAPI, numpy, scipy, demucs, silero-vad)..."
pip install -r requirements.txt

# Note: RVC requires special installation
echo "[5/5] RVC installation note:"
echo "  RVC v2 requires additional setup. See docs/RVC_SETUP.md"
echo ""

echo "=== Setup Complete ==="
echo "Activate environment: source venv/bin/activate"
echo "Run tests: ./run_phase1_tests.sh"
