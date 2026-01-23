#!/usr/bin/env python3
"""
Generate TWIST2 dataset YAML config from motion folders.
Includes all motion data folders with configurable weights.
"""

import os
import yaml
from glob import glob

def generate_twist2_yaml(root_path, output_yaml_path, folder_weights=None):
    """
    Generate YAML config for TWIST2 training.
    
    Args:
        root_path: Root path containing motion folders
        output_yaml_path: Output yaml file path
        folder_weights: Dict mapping folder names to weights (default 1.0)
    """
    if folder_weights is None:
        folder_weights = {}
    
    config = {
        "root_path": root_path,
        "motions": []
    }
    
    # Find all pkl files recursively
    pkl_files = glob(os.path.join(root_path, "**/*.pkl"), recursive=True)
    pkl_files = sorted(pkl_files)
    
    print(f"Found {len(pkl_files)} pkl files in {root_path}")
    
    for pkl_path in pkl_files:
        # Get relative path from root
        rel_path = os.path.relpath(pkl_path, root_path)
        folder_name = os.path.dirname(rel_path)
        
        # Determine weight based on folder
        weight = folder_weights.get(folder_name, 1.0)
        
        # Skip folders with 0 weight
        if weight == 0:
            continue
        
        config["motions"].append({
            "file": rel_path,
            "weight": weight,
            "description": "general movement"
        })
    
    # Write YAML
    with open(output_yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    # Print summary
    folder_counts = {}
    for motion in config["motions"]:
        folder = os.path.dirname(motion["file"])
        folder_counts[folder] = folder_counts.get(folder, 0) + 1
    
    print(f"\nDataset summary:")
    for folder, count in sorted(folder_counts.items()):
        weight = folder_weights.get(folder, 1.0)
        print(f"  {folder}: {count} motions (weight={weight})")
    
    print(f"\nTotal: {len(config['motions'])} motions")
    print(f"Saved to: {output_yaml_path}")


if __name__ == "__main__":
    # Configuration
    root_path = "/home/robo/Desktop/VP/TWIST2/assets/TWIST2_full"
    output_yaml_path = "../../motion_data_configs/twist2_dataset_local.yaml"
    
    # Folder weights - higher weight = more sampling during training
    # Your recorded motions can have higher weight to focus training on them
    # Set weight to 0 to exclude a folder
    folder_weights = {
        # AMASS retargeted data
        "AMASS_g1_GMR8": 1.0,
        # OMOMO retargeted data  
        "OMOMO_g1_GMR": 1.0,
        # twist1 to twist2 converted data
        "twist1_to_twist2": 1.0,
        # Existing teleop recordings (higher weight)
        "v1_v2_v3_g1": 10.0,
        # Your new recordings (higher weight to focus on them)
        "eastworlds_fixed": 10.0,
        # Exclude unfixed eastworlds (use 0 weight)
        "eastworlds": 0.0,
    }
    
    generate_twist2_yaml(root_path, output_yaml_path, folder_weights)

