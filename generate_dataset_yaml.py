#!/usr/bin/env python3
"""
Generate a dataset yaml file with:
- virtuals_dataset files at weight 10.0
- TWIST2_full files at weight 1.0
"""

import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate dataset yaml for training')
    parser.add_argument('--output', '-o', default='legged_gym/motion_data_configs/virtuals_dataset.yaml',
                        help='Output yaml file path')
    parser.add_argument('--virtuals_weight', type=float, default=10.0,
                        help='Weight for virtuals_dataset files (default: 10.0)')
    parser.add_argument('--twist2_weight', type=float, default=1.0,
                        help='Weight for TWIST2_full files (default: 1.0)')
    args = parser.parse_args()

    # Get script directory as base
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, "assets")

    motions = []

    # Add virtuals_dataset files at high weight
    virtuals_dir = os.path.join(base_path, "virtuals_dataset")
    if os.path.exists(virtuals_dir):
        for root, dirs, files in os.walk(virtuals_dir):
            for f in sorted(files):
                if f.endswith('.pkl'):
                    rel_path = os.path.relpath(os.path.join(root, f), base_path)
                    motions.append({
                        'file': rel_path,
                        'weight': args.virtuals_weight,
                        'description': 'virtuals dataset (high priority)'
                    })
        print(f"Added {sum(1 for m in motions if m['weight'] == args.virtuals_weight)} files from virtuals_dataset (weight: {args.virtuals_weight})")
    else:
        print(f"Warning: {virtuals_dir} not found")

    # Add TWIST2_full files at normal weight
    twist2_dir = os.path.join(base_path, "TWIST2_full")
    twist2_count = 0
    if os.path.exists(twist2_dir):
        for root, dirs, files in os.walk(twist2_dir):
            for f in sorted(files):
                if f.endswith('.pkl'):
                    rel_path = os.path.relpath(os.path.join(root, f), base_path)
                    motions.append({
                        'file': rel_path,
                        'weight': args.twist2_weight,
                        'description': 'general movement'
                    })
                    twist2_count += 1
        print(f"Added {twist2_count} files from TWIST2_full (weight: {args.twist2_weight})")
    else:
        print(f"Warning: {twist2_dir} not found")

    # Write to file
    output_path = os.path.join(script_dir, args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(f"root_path: {base_path}\n")
        f.write("motions:\n")
        for m in motions:
            f.write(f"- file: {m['file']}\n")
            f.write(f"  weight: {m['weight']}\n")
            f.write(f"  description: {m['description']}\n")

    print(f"\nCreated: {output_path}")
    print(f"Total motions: {len(motions)}")

if __name__ == '__main__':
    main()

