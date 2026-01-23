# Start Recording Session
```
cd /home/robo/Desktop/VP/TWIST2
source GMR/.venv/bin/activate
bash record_motion.sh
```

# playback
```
cd /home/robo/Desktop/VP/TWIST2/GMR
source .venv/bin/activate
python scripts/vis_robot_motion.py \
    --robot unitree_g1 \
    --robot_motion_path ../assets/TWIST2_full/v1_v2_v3_g1/0807_yanjie_walk_001.pkl

python scripts/vis_robot_motion.py \
    --robot unitree_g1   \
    --robot_motion_path ../assets/TWIST2_full/eastworlds/sk_walk_004.pkl 

python scripts/vis_robot_motion.py \
    --robot unitree_g1   \
    --robot_motion_path ../assets/TWIST2_full/eastworlds_fixed/sk_walk_004.pkl 
```