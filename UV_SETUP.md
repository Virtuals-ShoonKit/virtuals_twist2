# UV Setup Guide for TWIST2

This guide shows how to set up TWIST2 using `uv` for package management instead of conda.

## Prerequisites

- `uv` installed (already have it from GMR setup)
- Python 3.8 (handled by uv)

## Quick Start

### 1. Create and Activate Virtual Environment

```bash
cd /home/ubuntu/Desktop/VP/TWIST2

# Create virtual environment with Python 3.8
uv venv --python 3.8

# Activate the environment
source .venv/bin/activate
```

### 2. Install IsaacGym (Manual Step)

IsaacGym must be installed manually as it's not available on PyPI:

```bash
# Download IsaacGym from https://developer.nvidia.com/isaac-gym
# Then install it:
cd /path/to/isaacgym/python
uv pip install -e .
```

### 3. Install TWIST2 and All Dependencies

```bash
cd /home/ubuntu/Desktop/VP/TWIST2

# Install all dependencies including local packages
uv sync

# Or install in editable mode manually
uv pip install -e .
```

This will automatically install:
- All Python dependencies listed in `pyproject.toml`
- Local packages (`rsl_rl`, `legged_gym`, `pose`) in editable mode

### 4. Install Redis Server

```bash
sudo apt update
sudo apt install -y redis-server

sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Modify these lines:
# bind 0.0.0.0
# protected-mode no

# Restart Redis
sudo systemctl restart redis-server
```

### 5. (Optional) Install Unitree SDK for Sim2Real

If you want to deploy to the physical robot from your laptop:

```bash
cd /home/ubuntu/Desktop/VP
git clone https://github.com/YanjieZe/unitree_sdk2.git
cd unitree_sdk2

# Install system dependencies
sudo apt-get update
sudo apt-get install build-essential cmake python3-dev python3-pip pybind11-dev

# Install Python dependencies
uv pip install pybind11 pybind11-stubgen numpy

# Build and install
cd python_binding
export UNITREE_SDK2_PATH=$(pwd)/..
bash build.sh --sdk-path $UNITREE_SDK2_PATH

# Install to virtual environment
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
sudo cp build/lib/unitree_interface.cpython-*-linux-gnu.so $SITE_PACKAGES/unitree_interface.so

# Verify installation
python -c "import unitree_interface; print('✓ Unitree SDK installed')"
```

## Using UV Commands

### Add a New Dependency

```bash
# Add to main dependencies
uv add package-name

# Add to dev dependencies
uv add --dev package-name

# Add with specific version
uv add "package-name>=1.0.0"
```

### Sync Dependencies

```bash
# Install/update all dependencies from pyproject.toml
uv sync

# Sync only production dependencies (skip dev)
uv sync --no-dev
```

### Run Commands in Environment

```bash
# Run a command without activating
uv run python script.py

# Or activate and run normally
source .venv/bin/activate
python script.py
```

### Lock Dependencies

```bash
# Create/update uv.lock file
uv lock
```

## Comparison with Original Conda Setup

| Original Conda | UV Equivalent |
|----------------|---------------|
| `conda create -n twist2 python=3.8` | `uv venv --python 3.8` |
| `conda activate twist2` | `source .venv/bin/activate` |
| `pip install -e .` | `uv pip install -e .` or `uv sync` |
| `pip install package` | `uv add package` |

## Advantages of UV

1. **Faster**: UV is written in Rust and is 10-100x faster than pip
2. **Better dependency resolution**: More reliable than pip
3. **Lockfile support**: `uv.lock` ensures reproducible installs
4. **Simpler**: No need for separate conda environment
5. **Modern**: Uses `pyproject.toml` standard

## Training and Usage

After setup, use TWIST2 normally:

```bash
# Activate environment
source .venv/bin/activate

# Training
bash train.sh 1021_twist2 cuda:0

# Export to ONNX
bash to_onnx.sh $YOUR_POLICY_PATH

# Sim2Sim verification
bash run_motion_server.sh
bash sim2sim.sh

# Sim2Real deployment
bash sim2real.sh

# GUI
bash gui.sh
```

## Troubleshooting

### IsaacGym Installation Issues

If IsaacGym fails to install, make sure you:
1. Downloaded the correct version from NVIDIA
2. Have CUDA installed
3. Use Python 3.8 (IsaacGym requirement)

### Package Conflicts

```bash
# Clear cache and reinstall
uv cache clean
uv sync --reinstall
```

### Missing System Dependencies

Some packages may need system libraries:

```bash
sudo apt-get update
sudo apt-get install -y build-essential libgl1-mesa-glx libglib2.0-0
```

## Notes

- The virtual environment is located at `.venv/` in the TWIST2 directory
- `uv.lock` file locks exact versions for reproducibility
- You can still use regular `pip` commands after activating the venv, but `uv pip` is faster
- For GMR (online retargeting), continue using your existing GMR uv setup with Python 3.10+
