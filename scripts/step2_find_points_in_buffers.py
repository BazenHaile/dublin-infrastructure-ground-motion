#!/usr/bin/env python3
"""
Step 2: Find EGMS Points Inside Infrastructure Buffers
Performs spatial join to identify points within each buffer zone

Author: Bazen Haile
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import os

print("="*70)
print("STEP 2: FIND EGMS POINTS IN INFRASTRUCTURE BUFFERS")
print("="*70)

#=============================================================================
# FILE PATHS
#=============================================================================

BASE_PATH = "/Users/BazenHaile/SNAP_2025/Dublin_EGMS_Ground_velocity/Dublin_EGMS_Infrastructure"

# Input files
EGMS_FILE = f"{BASE_PATH}/data/processed/egms_dublin_clean.gpkg"
RAILWAYS_BUFFER = f"{BASE_PATH}/results/buffers/railways_buffer_dissolved.gpkg"
ROADS_BUFFER = f"{BASE_PATH}/results/buffers/roads_buffer_dissolved.gpkg"
HARBOUR_BUFFER = f"{BASE_PATH}/results/buffers/harbour_boundary_dissolved.gpkg"

# Output directory
OUTPUT_DIR = f"{BASE_PATH}/results/spatial_analysis"

#=============================================================================
# STEP 1: LOAD DATA
#=============================================================================

print("\n📂 Loading data...")
print("-" * 70)

# Load EGMS points
print("Loading EGMS points...")
egms = gpd.read_file(EGMS_FILE)
print(f"  ✅ Loaded {len(egms):,} EGMS points")
print(f"  📍 CRS: {egms.crs}")

# Load buffers
print("\nLoading buffer zones...")
railways_buffer = gpd.read_file(RAILWAYS_BUFFER)
roads_buffer = gpd.read_file(ROADS_BUFFER)
harbour_buffer = gpd.read_file(HARBOUR_BUFFER)
print(f"  ✅ Railways buffer loaded")
print(f"  ✅ Roads buffer loaded")
print(f"  ✅ Harbour buffer loaded")

#=============================================================================
# STEP 2: CONVERT EGMS TO ITM
#=============================================================================

print("\n🗺️  Converting EGMS points to ITM...")
print("-" * 70)

TARGET_CRS = "EPSG:2157"
egms_itm = egms.to_crs(TARGET_CRS)
print(f"✅ EGMS points converted to {TARGET_CRS}")

#=============================================================================
# STEP 3: SPATIAL JOIN - FIND POINTS IN EACH BUFFER
#=============================================================================

print("\n🔍 Finding EGMS points inside each buffer zone...")
print("-" * 70)
print("This is like asking: 'Which raindrops landed inside each target circle?'")

def find_points_in_buffer(egms_data, buffer_data, infrastructure_name):
    """
    Find EGMS points that fall WITHIN the buffer zone
    Returns: GeoDataFrame of points inside buffer
    """
    print(f"\n{infrastructure_name}:")
    
    # Spatial join: keep only points WHERE geometry is WITHIN buffer
    points_inside = gpd.sjoin(
        egms_data,           # Left: EGMS points
        buffer_data,         # Right: Buffer zone
        how='inner',         # Keep only matches
        predicate='within'   # Match if point is inside buffer
    )
    
    n_points = len(points_inside)
    print(f"  📍 Found {n_points:,} EGMS points inside buffer")
    
    if n_points > 0:
        # Add infrastructure label
        points_inside['infrastructure'] = infrastructure_name
        
        # Calculate velocity statistics
        mean_vel = points_inside['velocity'].mean()
        median_vel = points_inside['velocity'].median()
        min_vel = points_inside['velocity'].min()
        max_vel = points_inside['velocity'].max()
        
        print(f"  📊 Mean velocity: {mean_vel:.2f} mm/yr")
        print(f"  📊 Median velocity: {median_vel:.2f} mm/yr")
        print(f"  📊 Range: {min_vel:.2f} to {max_vel:.2f} mm/yr")
    else:
        print(f"  ⚠️  No points found in buffer!")
    
    return points_inside

# Find points in each infrastructure buffer
railways_points = find_points_in_buffer(egms_itm, railways_buffer, "Railways")
roads_points = find_points_in_buffer(egms_itm, roads_buffer, "Roads")
harbour_points = find_points_in_buffer(egms_itm, harbour_buffer, "Harbour")

#=============================================================================
# STEP 4: SAVE RESULTS
#=============================================================================

print("\n💾 Saving results...")
print("-" * 70)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save points for each infrastructure
if len(railways_points) > 0:
    railways_file = f"{OUTPUT_DIR}/railways_points.csv"
    railways_points.drop(columns=['geometry']).to_csv(railways_file, index=False)
    print(f"✅ Railways points: {railways_file}")

if len(roads_points) > 0:
    roads_file = f"{OUTPUT_DIR}/roads_points.csv"
    roads_points.drop(columns=['geometry']).to_csv(roads_file, index=False)
    print(f"✅ Roads points: {roads_file}")

if len(harbour_points) > 0:
    harbour_file = f"{OUTPUT_DIR}/harbour_points.csv"
    harbour_points.drop(columns=['geometry']).to_csv(harbour_file, index=False)
    print(f"✅ Harbour points: {harbour_file}")

# Also save as GeoPackage (keeps geometry for QGIS)
if len(railways_points) > 0:
    railways_points.to_file(f"{OUTPUT_DIR}/railways_points.gpkg", driver='GPKG')
    print(f"✅ Railways points (with geometry): railways_points.gpkg")

if len(roads_points) > 0:
    roads_points.to_file(f"{OUTPUT_DIR}/roads_points.gpkg", driver='GPKG')
    print(f"✅ Roads points (with geometry): roads_points.gpkg")

if len(harbour_points) > 0:
    harbour_points.to_file(f"{OUTPUT_DIR}/harbour_points.gpkg", driver='GPKG')
    print(f"✅ Harbour points (with geometry): harbour_points.gpkg")

#=============================================================================
# SUMMARY
#=============================================================================

print("\n" + "="*70)
print("✅ SPATIAL JOIN COMPLETE!")
print("="*70)

print("\n📊 SUMMARY:")
print("-" * 70)
print(f"Total EGMS points in Dublin: {len(egms):,}")
print(f"Points in Railways buffer: {len(railways_points):,}")
print(f"Points in Roads buffer: {len(roads_points):,}")
print(f"Points in Harbour buffer: {len(harbour_points):,}")

print("\n📁 Output files saved in:")
print(f"   {OUTPUT_DIR}/")

print("\n🎯 NEXT STEP:")
print("   Step 3: Calculate statistics for each infrastructure zone")

print("\n" + "="*70)