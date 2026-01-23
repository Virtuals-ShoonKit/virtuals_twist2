#!/bin/bash
# TWIST2 & GMR UV Setup Script

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "TWIST2 & GMR UV Setup"
echo "========================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✓ UV found: $(uv --version)"

# ========================================
# TWIST2 Environment (Python 3.8)
# ========================================
echo ""
echo "========================================"
echo "Setting up TWIST2 environment (Python 3.8)..."
echo "========================================"

cd "$SCRIPT_DIR"
uv venv --python 3.8
echo "✓ TWIST2 virtual environment created at $SCRIPT_DIR/.venv/"

# ========================================
# GMR Environment (Python 3.10)
# ========================================
echo ""
echo "========================================"
echo "Setting up GMR environment (Python 3.10)..."
echo "========================================"

cd "$SCRIPT_DIR/GMR"
uv venv --python 3.10
echo "✓ GMR virtual environment created at $SCRIPT_DIR/GMR/.venv/"

# ========================================
# Next Steps
# ========================================
echo ""
echo "========================================"
echo "Setup Complete! Next Steps:"
echo "========================================"
echo ""
echo "=== TWIST2 (for training, sim2sim, sim2real) ==="
echo "  1. Activate:  source $SCRIPT_DIR/.venv/bin/activate"
echo "  2. Install IsaacGym:"
echo "       cd /path/to/isaacgym/python"
echo "       uv pip install -e ."
echo "  3. Install TWIST2:"
echo "       cd $SCRIPT_DIR"
echo "       uv sync"
echo ""
echo "=== GMR (for motion retargeting) ==="
echo "  1. Activate:  source $SCRIPT_DIR/GMR/.venv/bin/activate"
echo "  2. Install GMR:"
echo "       cd $SCRIPT_DIR/GMR"
echo "       uv pip install -e ."
echo ""
echo "=== Quick Aliases (add to ~/.bashrc) ==="
echo "  alias twist2='cd $SCRIPT_DIR && source .venv/bin/activate'"
echo "  alias gmr='cd $SCRIPT_DIR/GMR && source .venv/bin/activate'"
echo ""
echo "========================================"
