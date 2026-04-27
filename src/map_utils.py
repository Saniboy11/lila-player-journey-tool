import os
from PIL import Image
import pandas as pd
import streamlit as st
from src.config import MAP_CONFIG, MINIMAP_PIXELS

def world_to_minimap(x: float, z: float, map_id: str):
    """
    Converts 3D world coordinates (x, z) to 2D minimap pixel coordinates.
    Follows UV mapping formula from LILA BLACK documentation.
    """
    if map_id not in MAP_CONFIG:
        return None, None
        
    config = MAP_CONFIG[map_id]
    
    # Step 1: Convert world coords to UV (0-1 range)
    u = (x - config['origin_x']) / config['scale']
    v = (z - config['origin_z']) / config['scale']
    
    # Step 2: Convert UV to pixel coords (1024x1024 image)
    pixel_x = u * MINIMAP_PIXELS
    pixel_y = (1 - v) * MINIMAP_PIXELS  # Y is flipped (image origin is top-left)
    
    return pixel_x, pixel_y

def add_pixel_coordinates(df: pd.DataFrame, clip_out_of_bounds: bool = True) -> pd.DataFrame:
    """
    Applies the world_to_minimap conversion to an entire DataFrame.
    Adds 'pixel_x' and 'pixel_y' columns to the dataframe.
    
    If clip_out_of_bounds is True, coordinates outside the [0, 1024] range 
    will be clamped to the borders. A boolean column 'is_out_of_bounds' 
    is also added for filtering/debugging.
    """
    if df.empty or 'x' not in df.columns or 'z' not in df.columns or 'map_id' not in df.columns:
        return df
        
    map_configs = pd.DataFrame.from_dict(MAP_CONFIG, orient='index')
    merged = df.merge(map_configs, left_on='map_id', right_index=True, how='left')
    
    # Mathematical transform
    df['pixel_x'] = ((merged['x'] - merged['origin_x']) / merged['scale']) * MINIMAP_PIXELS
    df['pixel_y'] = (1 - ((merged['z'] - merged['origin_z']) / merged['scale'])) * MINIMAP_PIXELS
    
    # Validation & Sanity Check Flagging
    df['is_out_of_bounds'] = (
        (df['pixel_x'] < 0) | (df['pixel_x'] > MINIMAP_PIXELS) |
        (df['pixel_y'] < 0) | (df['pixel_y'] > MINIMAP_PIXELS)
    )
    
    # Handle Out-of-bounds (Clamping)
    if clip_out_of_bounds:
        df['pixel_x'] = df['pixel_x'].clip(0, MINIMAP_PIXELS)
        df['pixel_y'] = df['pixel_y'].clip(0, MINIMAP_PIXELS)
        
    return df

def get_coordinate_sanity_stats(df: pd.DataFrame) -> dict:
    """
    Returns metrics about coordinate transforms for debug overlays.
    """
    if 'is_out_of_bounds' not in df.columns:
        return {}
    
    oob_count = df['is_out_of_bounds'].sum()
    total = len(df)
    
    stats = {
        "out_of_bounds_count": oob_count,
        "out_of_bounds_pct": round((oob_count / total * 100) if total > 0 else 0, 2),
        "min_pixel_x": df['pixel_x'].min(),
        "max_pixel_x": df['pixel_x'].max(),
        "min_pixel_y": df['pixel_y'].min(),
        "max_pixel_y": df['pixel_y'].max()
    }
    return stats

@st.cache_data(show_spinner=False)
def load_minimap_image(map_id: str):
    """
    Loads and caches the minimap image using Pillow.
    Returns None if image not found or map_id invalid.
    """
    if map_id not in MAP_CONFIG:
        return None
        
    image_path = MAP_CONFIG[map_id]['image_path']
    if not os.path.exists(image_path):
        st.error(f"Minimap image not found at: {image_path}")
        return None
        
    try:
        img = Image.open(image_path)
        return img
    except Exception as e:
        st.error(f"Failed to load image: {e}")
        return None
