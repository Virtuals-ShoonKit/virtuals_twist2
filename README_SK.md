# UV Setup

## 1. Create Virtual Environments
```bash
cd /home/robo/Desktop/EW/virtuals_twist2
bash setup_uv.sh
```

## 2. Install TWIST2 Packages (Python 3.8)
```bash
cd /home/robo/Desktop/EW/virtuals_twist2
source .venv/bin/activate

# Install TWIST2 and dependencies
cd /home/robo/Desktop/EW/virtuals_twist2
uv sync

# Install local packages
uv pip install -e ./pose
uv pip install -e ./rsl_rl
uv pip install -e ./legged_gym
```

## 3. Install IsaacGym
```bash
cd /home/robo/Desktop/EW/virtuals_twist2/IsaacGym/isaacgym/python
uv pip install -e .
```

## 4. Install GMR (Python 3.10) - for motion retargeting
```bash
cd /home/robo/Desktop/EW/virtuals_twist2/GMR
source .venv/bin/activate
uv pip install -e .
```

---

# Generate Dataset YAML

Generate `virtuals_dataset.yaml` with custom weights:
- `assets/virtuals_dataset/*` → weight **10.0** (high priority)
- `assets/TWIST2_full/*` → weight **1.0**

```bash
cd /home/robo/Desktop/EW/virtuals_twist2
source .venv/bin/activate
python generate_dataset_yaml.py
```

Custom weights example:
```bash
python generate_dataset_yaml.py --virtuals_weight 10.0 --twist2_weight 1.0
```

---

# Training Teacher Policy

## Train Teacher (Motion Imitation)
```bash
cd /home/robo/Desktop/EW/virtuals_twist2
source .venv/bin/activate

cd legged_gym/legged_gym/scripts
python train.py --task g1_mimic \
                --proj_name g1_mimic \
                --exptid virtuals_teacher_001 \
                --device cuda:0
```

## Train Privileged Policy
```bash
cd /home/robo/Desktop/EW/virtuals_twist2
source .venv/bin/activate

cd legged_gym/legged_gym/scripts
python train.py --task g1_priv_mimic \
                --proj_name g1_priv_mimic \
                --exptid ew_teacher_domran_001 \
                --device cuda:0 \
                --num_envs 2048

python train.py --task g1_priv_mimic_bfm_zero \
                --proj_name g1_priv_mimic_bfm_zero \
                --exptid teacher_kpkd_001 \
                --device cuda:0
```

## Train Student Policy (after teacher is trained)
```bash
cd /home/robo/Desktop/EW/virtuals_twist2
source .venv/bin/activate

# Using the train.sh script
bash train.sh <experiment_id> <device>
# Example: bash train.sh virtuals_stu_001 cuda:0

# Or manually:
cd legged_gym/legged_gym/scripts
python train.py --task g1_stu_future \
                --proj_name g1_stu_future \
                --exptid virtuals_stu_001 \
                --device cuda:0

python train.py --task g1_stu_future_bfm_zero \
                --proj_name g1_stu_future_bfm_zero \
                --exptid student_bfm_zero_001 \
                --device cuda:0 \
                --teacher_exptid teacher_kpkd_001 \
                --teacher_checkpoint -1 \
                --num_envs 2048
```

# play

```bash
cd legged_gym/legged_gym/scripts
python play.py --task g1_priv_mimic_bfm_zero \
               --proj_name g1_priv_mimic_bfm_zero \
               --exptid teacher_kpkd_002 \
               --device cuda:0 \
               --checkpoint -1 \
               --env.motion.motion_file /home/robo/Desktop/EW/virtuals_twist2/assets/example_motions/sk_walk_050.pkl \
               --num_envs 1 \
               --record_video

python play.py --task g1_stu_future_bfm_zero \
               --proj_name g1_stu_future_bfm_zero \
               --exptid stu_kpkd_001 \
               --device cuda:0 \
               --checkpoint -1 \
               --env.motion.motion_file /home/robo/Desktop/EW/virtuals_twist2/assets/example_motions/sk_walk_050.pkl \
               --num_envs 1 \
               --eval_student \
               --record_video
```

# Export ,oonx
```bash
./to_onnx.sh /home/robo/Desktop/EW/virtuals_twist2/assets/ckpts/ew_kpkd_10k.pt
```

# Test
```bash
# Terminal 1:
./run_motion_server.sh

# Terminal 2:
./run_sim2sim.sh
```
---

# Start Recording Session
```bash
cd /home/robo/Desktop/EW/virtuals_twist2
source GMR/.venv/bin/activate
bash record_motion.sh
```

# Playback
```bash
cd /home/robo/Desktop/EW/virtuals_twist2/GMR
source .venv/bin/activate

python scripts/vis_robot_motion.py \
    --robot unitree_g1 \
    --robot_motion_path ../assets/TWIST2_full/v1_v2_v3_g1/0807_yanjie_walk_001.pkl

python scripts/vis_robot_motion.py \
    --robot unitree_g1 \
    --robot_motion_path ../assets/TWIST2_full/eastworlds/sk_walk_004.pkl 

python scripts/vis_robot_motion.py \
    --robot unitree_g1 \
    --robot_motion_path ../assets/TWIST2_full/eastworlds_fixed/sk_walk_004.pkl 
```