#!/usr/bin/env python3
"""
Step 1: Create Buffers Around Real Infrastructure
Simple script - just creates buffer zones

Author: Bazen Haile
"""

import geopandas as gpd
import os

print("="*70)
print("STEP 1: CREATE BUFFERS AROUND INFRASTRUCTURE")
print("="*70)

#=============================================================================
# FILE PATHS
#=============================================================================

BASE_PATH = "/Users/BazenHaile/SNAP_2025/Dublin_EGMS_Ground_velocity/Dublin_EGMS_Infrastructure"

# Input files (your clipped infrastructure)
ROADS_FILE = f"{BASE_PATH}/data/infrastructure/clipped infrastructure/Dublin_roads_clipped.gpkg"
RAILS_FILE = f"{BASE_PATH}/data/infrastructure/clipped infrastructure/Dublin_rails_clipped.gpkg"
HARBOUR_FILE = f"{BASE_PATH}/data/infrastructure/clipped infrastructure/Dublin_Hourbor_Clipped.gpkg"

# Output directory
OUTPUT_DIR = f"{BASE_PATH}/results/buffers"

# Buffer distances (in meters)
BUFFER_RAILWAYS = 50  # 50 meters for railways
BUFFER_ROADS = 30     # 30 meters for roads
BUFFER_HARBOUR = 0    # No buffer for harbour (use boundary as-is)

#=============================================================================
# STEP 1: LOAD INFRASTRUCTURE
#=============================================================================

print("\n📂 Loading infrastructure files...")
print("-" * 70)

# Load roads
print("Loading roads...")
roads = gpd.read_file(ROADS_FILE)
print(f"  ✅ Loaded {len(roads):,} road features")
print(f"  📍 CRS: {roads.crs}")

# Load railways
print("\nLoading railways...")
railways = gpd.read_file(RAILS_FILE)
print(f"  ✅ Loaded {len(railways):,} railway features")
print(f"  📍 CRS: {railways.crs}")

# Load harbour
print("\nLoading harbour...")
harbour = gpd.read_file(HARBOUR_FILE)
print(f"  ✅ Loaded {len(harbour):,} harbour features")
print(f"  📍 CRS: {harbour.crs}")

#=============================================================================
# STEP 2: CONVERT TO ITM (Irish Transverse Mercator)
#=============================================================================

print("\n🗺️  Converting to ITM (EPSG:2157)...")
print("-" * 70)
print("Why? We need accurate METER-based buffers!")
print("ITM is the official Irish coordinate system - 1 meter = exactly 1 meter")

TARGET_CRS = "EPSG:2157"

roads_itm = roads.to_crs(TARGET_CRS)
railways_itm = railways.to_crs(TARGET_CRS)
harbour_itm = harbour.to_crs(TARGET_CRS)

print(f"✅ All layers converted to {TARGET_CRS}")

#=============================================================================
# STEP 3: CREATE BUFFERS
#=============================================================================

print("\n📏 Creating buffers...")
print("-" * 70)

# Railways buffer: 50 meters
print(f"\n1. Railways buffer ({BUFFER_RAILWAYS}m)...")
railways_buffer = railways_itm.copy()
railways_buffer['geometry'] = railways_itm.buffer(BUFFER_RAILWAYS)
railways_buffer['infra_type'] = 'Railways'
railways_buffer['buffer_m'] = BUFFER_RAILWAYS
print(f"   ✅ Created {BUFFER_RAILWAYS}m buffer around {len(railways_buffer)} railway features")

# Roads buffer: 30 meters
print(f"\n2. Roads buffer ({BUFFER_ROADS}m)...")
roads_buffer = roads_itm.copy()
roads_buffer['geometry'] = roads_itm.buffer(BUFFER_ROADS)
roads_buffer['infra_type'] = 'Roads'
roads_buffer['buffer_m'] = BUFFER_ROADS
print(f"   ✅ Created {BUFFER_ROADS}m buffer around {len(roads_buffer)} road features")

# Harbour: use boundary as-is (no buffer)
print(f"\n3. Harbour boundary (no buffer)...")
harbour_buffer = harbour_itm.copy()
harbour_buffer['infra_type'] = 'Harbour'
harbour_buffer['buffer_m'] = 0
print(f"   ✅ Using harbour boundary as-is (no additional buffer)")

#=============================================================================
# STEP 4: DISSOLVE BUFFERS (Optional - merge overlapping areas)
#=============================================================================

print("\n🔄 Dissolving buffers (merging overlaps)...")
print("-" * 70)
print("This combines all railway buffers into ONE zone, all road buffers into ONE zone, etc.")

railways_dissolved = railways_buffer.dissolve(by='infra_type')
roads_dissolved = roads_buffer.dissolve(by='infra_type')
harbour_dissolved = harbour_buffer.dissolve(by='infra_type')

print("✅ Buffers dissolved")
print(f"   Railways: {len(railways_buffer)} features → 1 dissolved zone")
print(f"   Roads: {len(roads_buffer)} features → 1 dissolved zone")
print(f"   Harbour: {len(harbour_buffer)} features → 1 dissolved zone")

#=============================================================================
# STEP 5: SAVE BUFFERS
#=============================================================================

print("\n💾 Saving buffer files...")
print("-" * 70)

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save individual buffers (NOT dissolved - keeps original features)
railways_file = f"{OUTPUT_DIR}/railways_buffer_50m.gpkg"
roads_file = f"{OUTPUT_DIR}/roads_buffer_30m.gpkg"
harbour_file = f"{OUTPUT_DIR}/harbour_boundary.gpkg"

railways_buffer.to_file(railways_file, driver='GPKG')
roads_buffer.to_file(roads_file, driver='GPKG')
harbour_buffer.to_file(harbour_file, driver='GPKG')

print(f"✅ Railways buffer: {railways_file}")
print(f"✅ Roads buffer: {roads_file}")
print(f"✅ Harbour boundary: {harbour_file}")

# Save dissolved buffers (merged into single zones)
railways_dissolved_file = f"{OUTPUT_DIR}/railways_buffer_dissolved.gpkg"
roads_dissolved_file = f"{OUTPUT_DIR}/roads_buffer_dissolved.gpkg"
harbour_dissolved_file = f"{OUTPUT_DIR}/harbour_boundary_dissolved.gpkg"

railways_dissolved.to_file(railways_dissolved_file, driver='GPKG')
roads_dissolved.to_file(roads_dissolved_file, driver='GPKG')
harbour_dissolved.to_file(harbour_dissolved_file, driver='GPKG')

print(f"\n✅ Railways dissolved: {railways_dissolved_file}")
print(f"✅ Roads dissolved: {roads_dissolved_file}")
print(f"✅ Harbour dissolved: {harbour_dissolved_file}")

#=============================================================================
# SUMMARY
#=============================================================================

print("\n" + "="*70)
print("✅ BUFFERS CREATED SUCCESSFULLY!")
print("="*70)

print("\n📁 Output files saved in:")
print(f"   {OUTPUT_DIR}/")
print("\n📂 Files created:")
print("   Individual buffers (keeps all features):")
print("   ├── railways_buffer_50m.gpkg")
print("   ├── roads_buffer_30m.gpkg")
print("   └── harbour_boundary.gpkg")
print("\n   Dissolved buffers (merged into single zones):")
print("   ├── railways_buffer_dissolved.gpkg")
print("   ├── roads_buffer_dissolved.gpkg")
print("   └── harbour_boundary_dissolved.gpkg")

print("\n🎯 NEXT STEP:")
print("   Load these buffer files in QGIS to visualize them!")
print("   Then we'll use them for spatial analysis with EGMS points")

print("\n" + "="*70)
