from legged_gym.envs.g1.g1_mimic_distill_config import G1MimicPrivCfg, G1MimicPrivCfgPPO, G1MimicStuCfg, G1MimicStuCfgDAgger
from legged_gym.envs.g1.g1_mimic_future_config import G1MimicStuFutureCfg, G1MimicStuFutureCfgDAgger
from legged_gym.envs.base.humanoid_mimic_config import HumanoidMimicCfgPPO
from legged_gym import LEGGED_GYM_ROOT_DIR
import torch


class G1MimicBfmZeroCfg(G1MimicPrivCfg):
    """Balanced configuration with kp/kd gains and per-joint action scaling.
    Compromise between stable walking and motion tracking."""
    
    class control(G1MimicPrivCfg.control):
        # Balanced PD gains - compromise between stable walking and motion tracking
        # Note: Using specific keys for waist joints to ensure correct mapping
        # waist_yaw uses hip_yaw value, waist_roll/pitch use ankle value
        stiffness = {
            'hip_yaw': 80.0,      # Increased from 40 for better tracking
            'hip_roll': 100.0,    # Kept high for stability
            'hip_pitch': 100.0,   # Kept high for stability
            'knee': 120.0,        # Increased from 99 for better tracking
            'ankle': 35.0,        # Increased from 28 for better tracking
            'waist_yaw': 150.0,   # Much higher than bfm (40) for better tracking
            'waist_roll': 120.0,  # Much higher than bfm (28) for better tracking
            'waist_pitch': 120.0, # Much higher than bfm (28) for better tracking
            'shoulder': 40.0,    # Increased from 14 for better tracking
            'elbow': 40.0,        # Increased from 14 for better tracking
            'wrist_roll': 20.0,   # Increased from 14-17 for better tracking
            'wrist_pitch': 20.0,  # Increased from 17 for better tracking
            'wrist_yaw': 20.0,    # Increased from 17 for better tracking
        }  # [N*m/rad]
        
        damping = {
            'hip_yaw': 2.0,       # Reduced from 2.5 for more responsive
            'hip_roll': 2.0,      # Reduced from 6.3 for more responsive
            'hip_pitch': 2.0,     # Reduced from 6.3 for more responsive
            'knee': 4.0,          # Reduced from 6.3 for more responsive
            'ankle': 2.0,         # Slightly increased from 1.8
            'waist_yaw': 4.0,     # Much higher than bfm (2.5) for stability
            'waist_roll': 3.5,    # Much higher than bfm (1.8) for stability
            'waist_pitch': 3.5,   # Much higher than bfm (1.8) for stability
            'shoulder': 5.0,      # Much higher than bfm (0.9) for stability
            'elbow': 5.0,         # Much higher than bfm (0.9) for stability
            'wrist_roll': 1.0,    # Similar to regular config
            'wrist_pitch': 1.0,   # Similar to regular config
            'wrist_yaw': 1.0,     # Similar to regular config
        }  # [N*m*s/rad]
        
        # Balanced action scaling
        action_scale = 0.5  # Base action scale
        action_rescale = 3.0  # Global multiplier (reduced from 5.0 for better stability)
        
        # Per-joint action scales (balanced values)
        # Order: left leg (6), right leg (6), waist (3), left arm (7), right arm (7) = 29 total
        action_scale_per_joint = [
            # Left leg: hip_yaw, hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll
            0.5, 0.5, 0.5, 0.5, 0.25, 0.25,
            # Right leg: hip_yaw, hip_roll, hip_pitch, knee, ankle_pitch, ankle_roll
            0.5, 0.5, 0.5, 0.5, 0.25, 0.25,
            # Waist: yaw, roll, pitch (increased from 0.22 for better tracking)
            0.5, 0.3, 0.3,
            # Left arm: shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll, wrist_pitch, wrist_yaw
            0.35, 0.35, 0.35, 0.35, 0.1, 0.1, 0.1,
            # Right arm: shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll, wrist_pitch, wrist_yaw
            0.35, 0.35, 0.35, 0.35, 0.1, 0.1, 0.1,
        ]
        
        decimation = 10
    
    class init_state(G1MimicPrivCfg.init_state):
        # BFM-Zero default joint angles (less aggressive)
        default_joint_angles = {
            'left_hip_pitch_joint': -0.1,  # Less bent than default -0.2
            'left_hip_roll_joint': 0.0,
            'left_hip_yaw_joint': 0.0,
            'left_knee_joint': 0.3,  # Less extended than default 0.4
            'left_ankle_pitch_joint': -0.2,
            'left_ankle_roll_joint': 0.0,
            
            'right_hip_pitch_joint': -0.1,  # Less bent than default -0.2
            'right_hip_roll_joint': 0.0,
            'right_hip_yaw_joint': 0.0,
            'right_knee_joint': 0.3,  # Less extended than default 0.4
            'right_ankle_pitch_joint': -0.2,
            'right_ankle_roll_joint': 0.0,
            
            'waist_yaw_joint': 0.0,
            'waist_roll_joint': 0.0,
            'waist_pitch_joint': 0.0,
            
            'left_shoulder_pitch_joint': 0.0,
            'left_shoulder_roll_joint': 0.4,
            'left_shoulder_yaw_joint': 0.0,
            'left_elbow_joint': 1.2,
            'left_wrist_roll_joint': 0.0,
            'left_wrist_pitch_joint': 0.0,
            'left_wrist_yaw_joint': 0.0,
            
            'right_shoulder_pitch_joint': 0.0,
            'right_shoulder_roll_joint': -0.4,
            'right_shoulder_yaw_joint': 0.0,
            'right_elbow_joint': 1.2,
            'right_wrist_roll_joint': 0.0,
            'right_wrist_pitch_joint': 0.0,
            'right_wrist_yaw_joint': 0.0,
        }


class G1MimicBfmZeroCfgPPO(G1MimicPrivCfgPPO):
    """PPO training config for BFM-Zero privileged policy."""
    class runner(G1MimicPrivCfgPPO.runner):
        max_iterations = 12501  # number of policy updates


class G1MimicStuBfmZeroCfg(G1MimicStuCfg):
    """Student policy config with BFM-Zero gains."""
    class control(G1MimicBfmZeroCfg.control):
        pass
    
    class init_state(G1MimicBfmZeroCfg.init_state):
        pass


class G1MimicStuBfmZeroCfgDAgger(G1MimicStuCfgDAgger):
    """DAgger training config for BFM-Zero student policy."""
    class teachercfg(G1MimicBfmZeroCfgPPO):
        pass
    
    class runner(G1MimicStuCfgDAgger.runner):
        max_iterations = 12501
        teacher_experiment_name = 'teacher_kpkd_001'
        teacher_proj_name = 'g1_priv_mimic_bfm_zero'
        teacher_checkpoint = -1  # Use latest checkpoint


class G1MimicStuFutureBfmZeroCfg(G1MimicStuFutureCfg):
    """Future motion student policy config with BFM-Zero gains."""
    class control(G1MimicBfmZeroCfg.control):
        pass
    
    class init_state(G1MimicBfmZeroCfg.init_state):
        pass


class G1MimicStuFutureBfmZeroCfgDAgger(G1MimicStuFutureCfgDAgger):
    """DAgger training config for BFM-Zero future motion student policy."""
    class teachercfg(G1MimicBfmZeroCfgPPO):
        pass
    
    class runner(G1MimicStuFutureCfgDAgger.runner):
        max_iterations = 12501
        teacher_experiment_name = 'teacher_kpkd_001'
        teacher_proj_name = 'g1_priv_mimic_bfm_zero'
        teacher_checkpoint = -1  # Use latest checkpoint

