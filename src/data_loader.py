import os
import pandas as pd
import pyarrow.parquet as pq
import streamlit as st
import logging

logger = logging.getLogger(__name__)

@st.cache_data(show_spinner="Loading day data...")
def load_day_data(folder_path: str) -> pd.DataFrame:
    """
    Loads all parquet files for a specific day folder and combines them.
    Includes memory optimization, robust type checking, and chronological sorting.
    """
    if not os.path.exists(folder_path):
        st.warning(f"Data folder not found: {folder_path}")
        return pd.DataFrame()
        
    frames = []
    # Read all parquet files in the folder
    for f in os.listdir(folder_path):
        filepath = os.path.join(folder_path, f)
        if os.path.isdir(filepath):
            continue
            
        try:
            t = pq.read_table(filepath)
            frames.append(t.to_pandas())
        except Exception as e:
            logger.warning(f"Failed to read file {f}: {e}")
            continue
            
    if not frames:
        return pd.DataFrame()
        
    df = pd.concat(frames, ignore_index=True)
    
    # 1. Event Decoding (Robustness)
    # Decode event column from bytes to string safely
    if 'event' in df.columns:
        def decode_event(x):
            if pd.isna(x):
                return 'Unknown'
            if isinstance(x, bytes):
                try:
                    return x.decode('utf-8')
                except UnicodeDecodeError:
                    return 'DecodeError'
            return str(x)
        df['event'] = df['event'].apply(decode_event)
        
    # 2. Human vs Bot classification (Robustness)
    # UUIDs are 36 chars. Bot IDs are short numeric strings.
    if 'user_id' in df.columns:
        df['player_type'] = df['user_id'].apply(
            lambda x: 'Human' if pd.notna(x) and len(str(x)) > 15 else 'Bot'
        )
        
    # 3. Timestamp formatting (Robustness)
    if 'ts' in df.columns:
        if pd.api.types.is_numeric_dtype(df['ts']):
            # Raw integers in the data are Unix seconds, not milliseconds
            # despite what the parquet schema metadata may claim
            df['ts'] = pd.to_datetime(df['ts'], unit='s')
        elif pd.api.types.is_datetime64_any_dtype(df['ts']):
            # If already parsed as datetime but as ms, reinterpret as seconds
            raw = df['ts'].astype('int64') // 1_000_000  # ns -> ms -> s
            df['ts'] = pd.to_datetime(raw, unit='s')
            
    # 4. Sort chronologically (Match Reconstruction)
    if 'match_id' in df.columns and 'ts' in df.columns:
        df = df.sort_values(by=['match_id', 'ts']).reset_index(drop=True)
        
    # 5. Memory Optimization (Performance on Streamlit Cloud)
    # Convert highly repetitive string columns to 'category' type
    categorical_cols = ['event', 'map_id', 'match_id', 'player_type']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df

@st.cache_data(show_spinner="Filtering match data...")
def get_match_data(df: pd.DataFrame, match_id: str) -> pd.DataFrame:
    """
    Filters the loaded day dataframe for a specific match_id.
    """
    if df.empty or 'match_id' not in df.columns:
        return pd.DataFrame()
        
    return df[df['match_id'] == match_id].copy()

def get_available_matches(df: pd.DataFrame) -> list:
    """
    Returns a sorted list of unique match IDs from the dataframe.
    Prioritizes matches with the highest number of players to ensure
    good initial visibility for analysis.
    """
    if df.empty or 'match_id' not in df.columns:
        return []
    
    # Sort matches by number of unique players (descending)
    match_counts = df.groupby('match_id', observed=True)['user_id'].nunique().sort_values(ascending=False)
    return match_counts.index.tolist()

def audit_data_sanity(df: pd.DataFrame) -> dict:
    """
    Lightweight validation check. Returns metrics dictionary for display or logging.
    """
    if df.empty:
        return {"status": "Empty DataFrame"}
        
    metrics = {
        "total_events": len(df),
        "unique_matches": df['match_id'].nunique() if 'match_id' in df.columns else 0,
        "unique_humans": df[df['player_type'] == 'Human']['user_id'].nunique() if 'player_type' in df.columns else 0,
        "unique_bots": df[df['player_type'] == 'Bot']['user_id'].nunique() if 'player_type' in df.columns else 0,
    }
    
    # Check for decode errors
    if 'event' in df.columns:
        metrics['decode_errors'] = (df['event'] == 'DecodeError').sum()
        
    return metrics
