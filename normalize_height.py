import pickle
import numpy as np
import os
from glob import glob

src_dir = 'assets/TWIST2_full/eastworlds'
dst_dir = 'assets/TWIST2_full/eastworlds_fixed'
os.makedirs(dst_dir, exist_ok=True)

# Get reference z from existing good recording
with open('assets/TWIST2_full/v1_v2_v3_g1/0807_yanjie_walk_001.pkl', 'rb') as f:
    ref = pickle.load(f)
ref_z_min = ref['root_pos'][:, 2].min()
print(f'Reference z min: {ref_z_min:.4f}m')

# Process all pkl files in source dir
pkl_files = glob(os.path.join(src_dir, '*.pkl'))
print(f'Found {len(pkl_files)} pkl files')

for pkl_path in sorted(pkl_files):
    filename = os.path.basename(pkl_path)
    
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    
    # Calculate and apply z offset
    z_offset = data['root_pos'][:, 2].min() - ref_z_min
    data['root_pos'][:, 2] -= z_offset
    
    # Save to new location
    dst_path = os.path.join(dst_dir, filename)
    with open(dst_path, 'wb') as f:
        pickle.dump(data, f)
    
    print(f'  {filename}: z_offset={z_offset:.4f}m -> {dst_path}')

print(f'\nDone! Fixed files saved to: {dst_dir}')