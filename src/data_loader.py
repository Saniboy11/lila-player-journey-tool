import os
import pandas as pd
import pyarrow.parquet as pq
import streamlit as st
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Cap files read per day to keep cold-start under Streamlit Cloud's 60s timeout.
# 80 files at ~9KB each = ~720KB raw, which parses in ~5-8s on free tier.
MAX_FILES_PER_DAY = 80


def _read_one(filepath: str) -> pd.DataFrame | None:
    """Read a single parquet file. Returns None on failure."""
    try:
        return pq.read_table(filepath).to_pandas()
    except Exception as e:
        logger.warning(f"Skipping {os.path.basename(filepath)}: {e}")
        return None


@st.cache_data(show_spinner="Loading match data…")
def load_day_data(folder_path: str) -> pd.DataFrame:
    """
    Loads up to MAX_FILES_PER_DAY parquet files from a day folder in parallel.
    Returns a cleaned, sorted DataFrame ready for match reconstruction.
    """
    if not os.path.exists(folder_path):
        return pd.DataFrame()

    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if not os.path.isdir(os.path.join(folder_path, f))
    ]

    # Limit to cap; sort by name for reproducibility
    all_files = sorted(all_files)[:MAX_FILES_PER_DAY]

    if not all_files:
        return pd.DataFrame()

    frames = []
    # Parallel read — dramatically faster than sequential on Streamlit Cloud
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(_read_one, fp): fp for fp in all_files}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                frames.append(result)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)

    # --- Event decoding ---
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

    # --- Human vs Bot classification ---
    if 'user_id' in df.columns:
        df['player_type'] = df['user_id'].apply(
            lambda x: 'Human' if pd.notna(x) and len(str(x)) > 15 else 'Bot'
        )

    # --- Timestamp parsing ---
    # Raw integers in the parquet files are Unix epoch seconds regardless of
    # what the schema metadata claims.
    if 'ts' in df.columns:
        if pd.api.types.is_numeric_dtype(df['ts']):
            df['ts'] = pd.to_datetime(df['ts'], unit='s', errors='coerce')
        elif pd.api.types.is_datetime64_any_dtype(df['ts']):
            # Already a datetime but may have been parsed with wrong unit.
            # In pandas >= 2.0, the column is datetime64[ms]. astype('int64') returns the
            # exact raw integer from the parquet file (which actually represented seconds).
            raw = df['ts'].astype('int64')
            df['ts'] = pd.to_datetime(raw, unit='s', errors='coerce')
        df = df.dropna(subset=['ts'])

    # --- Sort for match reconstruction ---
    if 'match_id' in df.columns and 'ts' in df.columns:
        df = df.sort_values(by=['match_id', 'ts']).reset_index(drop=True)

    # --- Memory optimisation ---
    for col in ['event', 'map_id', 'match_id', 'player_type']:
        if col in df.columns:
            df[col] = df[col].astype('category')

    return df


@st.cache_data(show_spinner=False)
def get_match_data(df: pd.DataFrame, match_id: str) -> pd.DataFrame:
    if df.empty or 'match_id' not in df.columns:
        return pd.DataFrame()
    return df[df['match_id'] == match_id].copy()


def get_available_matches(df: pd.DataFrame) -> list:
    if df.empty or 'match_id' not in df.columns:
        return []
    
    # Calculate human counts per match
    human_mask = df['player_type'] == 'Human'
    human_counts = df[human_mask].groupby('match_id', observed=True)['user_id'].nunique()
    
    # Calculate total counts per match
    total_counts = df.groupby('match_id', observed=True)['user_id'].nunique()
    
    # Combine and score (1000 points per human + 1 point per bot)
    scores = (human_counts.reindex(total_counts.index).fillna(0) * 1000) + total_counts
    
    return scores.sort_values(ascending=False).index.tolist()


def audit_data_sanity(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"status": "Empty DataFrame"}
    metrics = {
        "total_events": len(df),
        "unique_matches": df['match_id'].nunique() if 'match_id' in df.columns else 0,
        "unique_humans": df[df['player_type'] == 'Human']['user_id'].nunique() if 'player_type' in df.columns else 0,
        "unique_bots": df[df['player_type'] == 'Bot']['user_id'].nunique() if 'player_type' in df.columns else 0,
    }
    if 'event' in df.columns:
        metrics['decode_errors'] = (df['event'] == 'DecodeError').sum()
    return metrics
