#!/usr/bin/env python3
"""
Detailed comparison of joint offsets, inertial properties, and sensor placements
between unitree_g1 (old) and unitree_g1_new (new) models.
"""

import xml.etree.ElementTree as ET
import numpy as np
import os
import sys

def parse_vector(attr_str):
    """Parse space-separated vector string to list of floats."""
    if attr_str is None:
        return None
    return [float(x) for x in attr_str.split()]

def parse_quat(attr_str):
    """Parse quaternion string (w x y z) to list."""
    if attr_str is None:
        return None
    return parse_vector(attr_str)

def format_vector(vec, precision=6):
    """Format vector for display."""
    if vec is None:
        return "None"
    return " ".join([f"{x:.{precision}f}" for x in vec])

def compare_vectors(v1, v2, name, tolerance=1e-6):
    """Compare two vectors and return if they differ."""
    if v1 is None and v2 is None:
        return False, "Both None"
    if v1 is None or v2 is None:
        return True, f"One is None: {v1} vs {v2}"
    if len(v1) != len(v2):
        return True, f"Different lengths: {len(v1)} vs {len(v2)}"
    diff = np.array(v1) - np.array(v2)
    max_diff = np.max(np.abs(diff))
    if max_diff > tolerance:
        return True, f"Max diff: {max_diff:.6e}"
    return False, f"Match (diff: {max_diff:.6e})"

def extract_body_info(body_elem, parent_path=""):
    """Recursively extract body information from XML."""
    bodies = []
    body_name = body_elem.get("name", "")
    full_path = f"{parent_path}/{body_name}" if parent_path else body_name
    
    # Extract body position and orientation
    pos = parse_vector(body_elem.get("pos"))
    quat = parse_quat(body_elem.get("quat"))
    
    # Extract inertial properties
    inertial = body_elem.find("inertial")
    inertial_info = None
    if inertial is not None:
        inertial_info = {
            "pos": parse_vector(inertial.get("pos")),
            "quat": parse_quat(inertial.get("quat")),
            "mass": float(inertial.get("mass")) if inertial.get("mass") else None,
            "diaginertia": parse_vector(inertial.get("diaginertia")),
        }
    
    # Extract joint information
    joint = body_elem.find("joint")
    joint_info = None
    if joint is not None:
        joint_info = {
            "name": joint.get("name"),
            "pos": parse_vector(joint.get("pos")),
            "axis": parse_vector(joint.get("axis")),
            "range": parse_vector(joint.get("range")),
        }
    
    # Extract sites (sensors)
    sites = []
    for site in body_elem.findall("site"):
        sites.append({
            "name": site.get("name"),
            "pos": parse_vector(site.get("pos")),
            "size": float(site.get("size")) if site.get("size") else None,
        })
    
    body_info = {
        "name": body_name,
        "path": full_path,
        "pos": pos,
        "quat": quat,
        "inertial": inertial_info,
        "joint": joint_info,
        "sites": sites,
    }
    bodies.append(body_info)
    
    # Recursively process child bodies
    for child_body in body_elem.findall("body"):
        bodies.extend(extract_body_info(child_body, full_path))
    
    return bodies

def parse_xml_file(xml_path):
    """Parse MuJoCo XML file and extract all body information."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Find worldbody
    worldbody = root.find("worldbody")
    if worldbody is None:
        return []
    
    all_bodies = []
    for body in worldbody.findall("body"):
        all_bodies.extend(extract_body_info(body))
    
    return all_bodies

def compare_models(old_xml, new_xml, official_xml=None):
    """Compare MuJoCo XML models (2 or 3-way comparison)."""
    print("="*80)
    if official_xml:
        print("PHYSICS COMPARISON: unitree_g1 vs unitree_g1_new vs unitree_g1_new_official")
    else:
        print("PHYSICS COMPARISON: unitree_g1 vs unitree_g1_new")
    print("="*80)
    
    print(f"\nLoading OLD model: {old_xml}")
    old_bodies = parse_xml_file(old_xml)
    print(f"  Found {len(old_bodies)} bodies")
    
    print(f"\nLoading NEW model: {new_xml}")
    new_bodies = parse_xml_file(new_xml)
    print(f"  Found {len(new_bodies)} bodies")
    
    # Create lookup dictionaries by body name
    old_dict = {b["name"]: b for b in old_bodies if b["name"]}
    new_dict = {b["name"]: b for b in new_bodies if b["name"]}
    
    official_dict = {}
    if official_xml:
        print(f"\nLoading OFFICIAL model: {official_xml}")
        official_bodies = parse_xml_file(official_xml)
        print(f"  Found {len(official_bodies)} bodies")
        official_dict = {b["name"]: b for b in official_bodies if b["name"]}
    
    # Get all unique body names (excluding hands)
    all_names = set(old_dict.keys()) | set(new_dict.keys())
    if official_dict:
        all_names |= set(official_dict.keys())
    all_names = {n for n in all_names if "hand" not in n.lower() and "thumb" not in n.lower() 
                 and "index" not in n.lower() and "middle" not in n.lower() and "palm" not in n.lower()}
    
    # Sort for consistent output
    all_names = sorted(all_names)
    
    print(f"\n{'='*80}")
    print("JOINT OFFSET COMPARISON (body positions)")
    print(f"{'='*80}")
    
    joint_diffs = []
    for name in all_names:
        old_body = old_dict.get(name)
        new_body = new_dict.get(name)
        official_body = official_dict.get(name) if official_dict else None
        
        if not old_body or not new_body:
            continue
        
        old_pos = old_body["pos"] or [0, 0, 0]
        new_pos = new_body["pos"] or [0, 0, 0]
        official_pos = (official_body["pos"] or [0, 0, 0]) if official_body else None
        
        is_diff, msg = compare_vectors(old_pos, new_pos, name)
        if is_diff or (official_body and official_pos):
            joint_diffs.append((name, old_pos, new_pos, official_pos, msg))
            print(f"\n{name}:")
            print(f"  OLD:     {format_vector(old_pos)}")
            print(f"  NEW:     {format_vector(new_pos)}")
            if official_pos:
                print(f"  OFFICIAL: {format_vector(official_pos)}")
                is_diff_off, msg_off = compare_vectors(new_pos, official_pos, name)
                if is_diff_off:
                    print(f"  NEW vs OFFICIAL: {msg_off}")
            if is_diff:
                print(f"  OLD vs NEW: {msg}")
    
    if not joint_diffs:
        print("\n✓ All joint offsets match!")
    
    print(f"\n{'='*80}")
    print("INERTIAL PROPERTIES COMPARISON")
    print(f"{'='*80}")
    
    inertial_diffs = []
    for name in all_names:
        old_body = old_dict.get(name)
        new_body = new_dict.get(name)
        
        if not old_body or not new_body:
            continue
        
        old_inertial = old_body["inertial"]
        new_inertial = new_body["inertial"]
        
        if not old_inertial and not new_inertial:
            continue
        
        if not old_inertial or not new_inertial:
            inertial_diffs.append((name, "One missing inertial"))
            print(f"\n{name}:")
            print(f"  OLD inertial: {old_inertial is not None}")
            print(f"  NEW inertial: {new_inertial is not None}")
            continue
        
        # Compare mass
        if old_inertial["mass"] != new_inertial["mass"]:
            inertial_diffs.append((name, "mass"))
            print(f"\n{name} - MASS:")
            print(f"  OLD: {old_inertial['mass']}")
            print(f"  NEW: {new_inertial['mass']}")
            print(f"  DIFF: {abs(old_inertial['mass'] - new_inertial['mass']):.6e}")
        
        # Compare center of mass position
        is_diff, msg = compare_vectors(old_inertial["pos"], new_inertial["pos"], name)
        if is_diff:
            inertial_diffs.append((name, "com_pos"))
            print(f"\n{name} - COM POSITION:")
            print(f"  OLD: {format_vector(old_inertial['pos'])}")
            print(f"  NEW: {format_vector(new_inertial['pos'])}")
            print(f"  DIFF: {msg}")
        
        # Compare inertia tensor
        is_diff, msg = compare_vectors(old_inertial["diaginertia"], new_inertial["diaginertia"], name)
        if is_diff:
            inertial_diffs.append((name, "inertia"))
            print(f"\n{name} - INERTIA TENSOR:")
            print(f"  OLD: {format_vector(old_inertial['diaginertia'])}")
            print(f"  NEW: {format_vector(new_inertial['diaginertia'])}")
            print(f"  DIFF: {msg}")
        
        # Compare quaternion (orientation of inertia)
        is_diff, msg = compare_vectors(old_inertial["quat"], new_inertial["quat"], name)
        if is_diff:
            inertial_diffs.append((name, "inertia_quat"))
            print(f"\n{name} - INERTIA ORIENTATION:")
            print(f"  OLD: {format_vector(old_inertial['quat'])}")
            print(f"  NEW: {format_vector(new_inertial['quat'])}")
            print(f"  DIFF: {msg}")
    
    if not inertial_diffs:
        print("\n✓ All inertial properties match!")
    
    print(f"\n{'='*80}")
    print("SENSOR PLACEMENT COMPARISON (sites)")
    print(f"{'='*80}")
    
    # Collect all sites
    old_sites = {}
    new_sites = {}
    official_sites = {}
    
    for name in all_names:
        old_body = old_dict.get(name)
        new_body = new_dict.get(name)
        official_body = official_dict.get(name) if official_dict else None
        
        if old_body and old_body["sites"]:
            for site in old_body["sites"]:
                old_sites[site["name"]] = {
                    "body": name,
                    "pos": site["pos"],
                    "size": site["size"],
                }
        
        if new_body and new_body["sites"]:
            for site in new_body["sites"]:
                new_sites[site["name"]] = {
                    "body": name,
                    "pos": site["pos"],
                    "size": site["size"],
                }
        
        if official_body and official_body["sites"]:
            for site in official_body["sites"]:
                official_sites[site["name"]] = {
                    "body": name,
                    "pos": site["pos"],
                    "size": site["size"],
                }
    
    all_site_names = set(old_sites.keys()) | set(new_sites.keys())
    if official_sites:
        all_site_names |= set(official_sites.keys())
    all_site_names = sorted(all_site_names)
    
    sensor_diffs = []
    for site_name in all_site_names:
        old_site = old_sites.get(site_name)
        new_site = new_sites.get(site_name)
        official_site = official_sites.get(site_name) if official_sites else None
        
        if not old_site and not new_site and not official_site:
            continue
        
        # Check if missing in any model
        missing = []
        if not old_site:
            missing.append("OLD")
        if not new_site:
            missing.append("NEW")
        if official_sites and not official_site:
            missing.append("OFFICIAL")
        
        if missing:
            sensor_diffs.append((site_name, f"Missing in {', '.join(missing)}"))
            print(f"\n{site_name}:")
            print(f"  OLD:     {old_site is not None} (body: {old_site['body'] if old_site else 'N/A'})")
            print(f"  NEW:     {new_site is not None} (body: {new_site['body'] if new_site else 'N/A'})")
            if official_sites:
                print(f"  OFFICIAL: {official_site is not None} (body: {official_site['body'] if official_site else 'N/A'})")
            continue
        
        # Compare positions
        positions_differ = False
        print(f"\n{site_name}:")
        print(f"  Body: OLD={old_site['body']}, NEW={new_site['body']}", end="")
        if official_site:
            print(f", OFFICIAL={official_site['body']}")
        else:
            print()
        
        if old_site and new_site:
            is_diff, msg = compare_vectors(old_site["pos"], new_site["pos"], site_name)
            if is_diff:
                positions_differ = True
                sensor_diffs.append((site_name, "position"))
                print(f"  OLD pos:     {format_vector(old_site['pos'])}")
                print(f"  NEW pos:     {format_vector(new_site['pos'])}")
                print(f"  OLD vs NEW:  {msg}")
        
        if official_site:
            if new_site:
                is_diff, msg = compare_vectors(new_site["pos"], official_site["pos"], site_name)
                if is_diff:
                    positions_differ = True
                    print(f"  NEW pos:     {format_vector(new_site['pos'])}")
                    print(f"  OFFICIAL pos: {format_vector(official_site['pos'])}")
                    print(f"  NEW vs OFFICIAL: {msg}")
            if old_site:
                is_diff, msg = compare_vectors(old_site["pos"], official_site["pos"], site_name)
                if is_diff and not positions_differ:
                    positions_differ = True
                    print(f"  OLD pos:     {format_vector(old_site['pos'])}")
                    print(f"  OFFICIAL pos: {format_vector(official_site['pos'])}")
                    print(f"  OLD vs OFFICIAL: {msg}")
    
    if not sensor_diffs:
        print("\n✓ All sensor placements match!")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Joint offset differences: {len(joint_diffs)}")
    print(f"Inertial property differences: {len(inertial_diffs)}")
    print(f"Sensor placement differences: {len(sensor_diffs)}")
    
    if not joint_diffs and not inertial_diffs and not sensor_diffs:
        print("\n✓ ALL PROPERTIES MATCH!")
    else:
        print(f"\n⚠ Found {len(joint_diffs) + len(inertial_diffs) + len(sensor_diffs)} total differences")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    old_xml = os.path.join(script_dir, "../assets/unitree_g1/g1_mocap_29dof.xml")
    new_xml = os.path.join(script_dir, "../assets/unitree_g1_new/g1_29dof_freebase.xml")
    official_xml = os.path.join(script_dir, "../assets/unitree_g1_new_official/g1_29dof.xml")
    
    if not os.path.exists(old_xml):
        print(f"ERROR: Old model not found at {old_xml}")
        sys.exit(1)
    
    if not os.path.exists(new_xml):
        print(f"ERROR: New model not found at {new_xml}")
        sys.exit(1)
    
    # Check if official model exists
    official_xml_path = None
    if os.path.exists(official_xml):
        official_xml_path = official_xml
        print(f"Found official model, will include in comparison")
    else:
        print(f"Official model not found at {official_xml}, doing 2-way comparison")
    
    compare_models(old_xml, new_xml, official_xml_path)

