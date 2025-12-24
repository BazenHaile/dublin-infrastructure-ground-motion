#!/usr/bin/env python3
"""
Create Professional Maps for Infrastructure Analysis
Generates 3 separate maps (Railways, Roads, Harbour) using Matplotlib

Author: Bazen Haile
Date: December 2024
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import contextily as ctx
import numpy as np
import os

print("="*70)
print("CREATING INFRASTRUCTURE ANALYSIS MAPS")
print("="*70)

#=============================================================================
# CONFIGURATION
#=============================================================================

BASE_PATH = "/Users/BazenHaile/SNAP_2025/Dublin_EGMS_Ground_velocity/Dublin_EGMS_Infrastructure"

# Input files
RAILWAYS_POINTS = f"{BASE_PATH}/results/spatial_analysis/railways_points.gpkg"
ROADS_POINTS = f"{BASE_PATH}/results/spatial_analysis/roads_points.gpkg"
HARBOUR_POINTS = f"{BASE_PATH}/results/spatial_analysis/harbour_points.gpkg"

RAILWAYS_BUFFER = f"{BASE_PATH}/results/buffers/railways_buffer_dissolved.gpkg"
ROADS_BUFFER = f"{BASE_PATH}/results/buffers/roads_buffer_dissolved.gpkg"
HARBOUR_BUFFER = f"{BASE_PATH}/results/buffers/harbour_boundary_dissolved.gpkg"

RAILWAYS_LINE = f"{BASE_PATH}/data/infrastructure/clipped infrastructure/Dublin_rails_clipped.gpkg"
ROADS_LINE = f"{BASE_PATH}/data/infrastructure/clipped infrastructure/Dublin_roads_clipped.gpkg"
HARBOUR_POLY = f"{BASE_PATH}/data/infrastructure/clipped infrastructure/Dublin_Hourbor_Clipped.gpkg"

# Output directory
OUTPUT_DIR = f"{BASE_PATH}/results/figures/python_maps"

# Map settings
DPI = 300
FIGSIZE = (12, 10)

#=============================================================================
# LOAD DATA
#=============================================================================

print("\n📂 Loading data...")
print("-" * 70)

# Load points
railways_pts = gpd.read_file(RAILWAYS_POINTS)
roads_pts = gpd.read_file(ROADS_POINTS)
harbour_pts = gpd.read_file(HARBOUR_POINTS)

# Load buffers
railways_buf = gpd.read_file(RAILWAYS_BUFFER)
roads_buf = gpd.read_file(ROADS_BUFFER)
harbour_buf = gpd.read_file(HARBOUR_BUFFER)

# Load infrastructure
railways_line = gpd.read_file(RAILWAYS_LINE)
roads_line = gpd.read_file(ROADS_LINE)
harbour_poly = gpd.read_file(HARBOUR_POLY)

print(f"✅ Railways: {len(railways_pts):,} points")
print(f"✅ Roads: {len(roads_pts):,} points")
print(f"✅ Harbour: {len(harbour_pts):,} points")

# Convert all to Web Mercator (EPSG:3857) for basemap
print("\n🗺️  Converting to Web Mercator for basemap...")
railways_pts = railways_pts.to_crs(epsg=3857)
roads_pts = roads_pts.to_crs(epsg=3857)
harbour_pts = harbour_pts.to_crs(epsg=3857)

railways_buf = railways_buf.to_crs(epsg=3857)
roads_buf = roads_buf.to_crs(epsg=3857)
harbour_buf = harbour_buf.to_crs(epsg=3857)

railways_line = railways_line.to_crs(epsg=3857)
roads_line = roads_line.to_crs(epsg=3857)
harbour_poly = harbour_poly.to_crs(epsg=3857)

print("✅ All data converted to EPSG:3857")

#=============================================================================
# CREATE COLOR MAP (Red-Yellow-Green)
#=============================================================================

# Create custom colormap: Red (subsidence) → Yellow → Green (uplift)
colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850']
n_bins = 100
cmap = LinearSegmentedColormap.from_list('RdYlGn', colors, N=n_bins)

#=============================================================================
# MAPPING FUNCTION
#=============================================================================

def create_infrastructure_map(points_gdf, buffer_gdf, infra_gdf, 
                              title, filename, infra_type):
    """
    Create a professional map for one infrastructure type
    
    Parameters:
    - points_gdf: GeoDataFrame with EGMS points
    - buffer_gdf: GeoDataFrame with buffer zone
    - infra_gdf: GeoDataFrame with infrastructure (line or polygon)
    - title: Map title
    - filename: Output filename
    - infra_type: 'line' or 'polygon'
    """
    print(f"\n🗺️  Creating {title}...")
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE)
    
    # Plot buffer zone (light gray, dashed outline)
    buffer_gdf.boundary.plot(ax=ax, color='black', linewidth=1.5, 
                             linestyle='--', alpha=0.7, label='Analysis Buffer Zone')
    
    # Plot infrastructure
    if infra_type == 'line':
        infra_gdf.plot(ax=ax, color='red', linewidth=2, 
                       alpha=0.8, label='Infrastructure')
    else:  # polygon
        infra_gdf.plot(ax=ax, facecolor='lightblue', edgecolor='darkblue', 
                       linewidth=1.5, alpha=0.3, label='Infrastructure')
    
    # Plot EGMS points colored by velocity
    points_gdf.plot(ax=ax, column='velocity', cmap=cmap,
                    markersize=30, alpha=0.8, 
                    edgecolor='black', linewidth=0.3,
                    legend=True,
                    legend_kwds={'label': 'Velocity (mm/yr)',
                                'orientation': 'horizontal',
                                'shrink': 0.8,
                                'pad': 0.05})
    
    # Add basemap
    try:
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, 
                       alpha=0.6, attribution=False)
        print("  ✅ Basemap added")
    except Exception as e:
        print(f"  ⚠️  Could not add basemap: {e}")
    
    # Set title and labels
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    
    # Add statistics text box
    n_points = len(points_gdf)
    mean_vel = points_gdf['velocity'].mean()
    median_vel = points_gdf['velocity'].median()
    pct_stable = ((points_gdf['velocity'] >= -2) & 
                  (points_gdf['velocity'] <= 2)).sum() / n_points * 100
    
    stats_text = f"""Analysis Results:
    Points: {n_points:,}
    Mean: {mean_vel:.2f} mm/yr
    Median: {median_vel:.2f} mm/yr
    Stable (±2mm/yr): {pct_stable:.1f}%"""
    
    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add north arrow
    x, y, arrow_length = 0.95, 0.95, 0.05
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                arrowprops=dict(facecolor='black', width=3, headwidth=10),
                ha='center', va='center', fontsize=14, fontweight='bold',
                xycoords=ax.transAxes)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    
    print(f"  ✅ Saved: {output_path}")
    
    return output_path

#=============================================================================
# CREATE ALL THREE MAPS
#=============================================================================

print("\n" + "="*70)
print("GENERATING MAPS")
print("="*70)

# Map 1: Railways
map1 = create_infrastructure_map(
    railways_pts, railways_buf, railways_line,
    title="Dublin Railways - Ground Motion Analysis (2019-2023)\n719 EGMS Measurement Points",
    filename="map_01_railways_analysis.png",
    infra_type='line'
)

# Map 2: Roads
map2 = create_infrastructure_map(
    roads_pts, roads_buf, roads_line,
    title="Dublin Roads - Ground Motion Analysis (2019-2023)\n3,964 EGMS Measurement Points",
    filename="map_02_roads_analysis.png",
    infra_type='line'
)

# Map 3: Harbour
map3 = create_infrastructure_map(
    harbour_pts, harbour_buf, harbour_poly,
    title="Dublin Port - Ground Motion Analysis (2019-2023)\n128 EGMS Measurement Points",
    filename="map_03_harbour_analysis.png",
    infra_type='polygon'
)

#=============================================================================
# SUMMARY
#=============================================================================

print("\n" + "="*70)
print("✅ ALL MAPS CREATED SUCCESSFULLY!")
print("="*70)

print(f"\n📁 Maps saved in:")
print(f"   {OUTPUT_DIR}/")
print(f"\n📊 Created 3 maps:")
print(f"   1. Railways Analysis (719 points)")
print(f"   2. Roads Analysis (3,964 points)")
print(f"   3. Harbour Analysis (128 points)")
print(f"\n🎨 Map specifications:")
print(f"   - Resolution: {DPI} DPI")
print(f"   - Format: PNG")
print(f"   - Basemap: OpenStreetMap")
print(f"   - Color scheme: Red-Yellow-Green (velocity)")

print("\n" + "="*70)