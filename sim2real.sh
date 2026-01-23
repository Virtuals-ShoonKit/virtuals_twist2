

# source ~/miniconda3/bin/activate twist2
source /home/ubuntu/Desktop/VP/TWIST2/.venv/bin/activate

SCRIPT_DIR=$(dirname $(realpath $0))
ckpt_path=${SCRIPT_DIR}/assets/ckpts/twist2_1017_20k.onnx

# change the network interface name to your own that connects to the robot
# net=enp0s31f6
net=enp58s0

# Fix DDS library path conflict - prioritize Unitree SDK libraries
export LD_LIBRARY_PATH=${SCRIPT_DIR}/unitree_sdk2/thirdparty/lib/x86_64:$LD_LIBRARY_PATH

cd deploy_real

python server_low_level_g1_real.py \
    --policy ${ckpt_path} \
    --net ${net} \
    --device cuda \
    --smooth_body 0.5
    # --use_hand \
    # --record_proprio \
