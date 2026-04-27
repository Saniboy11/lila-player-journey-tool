import streamlit as st
import pandas as pd
import os

# Set page config immediately
st.set_page_config(
    page_title="LILA BLACK | Player Journey Intelligence",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom sleek CSS for studio internal tool feel
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #E0E0E0;
        font-family: 'Inter', sans-serif;
    }
    .metric-container {
        background-color: #1E2127;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #333;
    }
    .designer-insights {
        background-color: #161A22;
        border-left: 4px solid #58A6FF;
        padding: 15px;
        border-radius: 4px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

from src.data_loader import load_day_data, get_match_data, get_available_matches, audit_data_sanity
from src.map_utils import add_pixel_coordinates, load_minimap_image, get_coordinate_sanity_stats
from src.visualizations import render_full_minimap

DATA_DIR = os.path.join("player_data", "player_data")

def main():
    st.title("LILA BLACK | Tactical Match Flow Analyzer")
    
    # --- SIDEBAR: Data Selection ---
    st.sidebar.header("🎯 Match Selection")
    
    # 1. Date Filter
    available_dates = ["February_10", "February_11", "February_12", "February_13", "February_14"]
    selected_date = st.sidebar.selectbox("Date", available_dates)
    
    # Load data for selected date
    folder_path = os.path.join(DATA_DIR, selected_date)
    day_df = load_day_data(folder_path)
    
    if day_df.empty:
        st.warning(f"No data available for {selected_date}.")
        return
        
    # 2. Map Filter
    if 'map_id' in day_df.columns:
        available_maps = sorted(day_df['map_id'].dropna().unique().tolist())
    else:
        available_maps = []
        
    if not available_maps:
        st.warning("No map data found in dataset.")
        return
        
    selected_map = st.sidebar.selectbox("Map", available_maps)
    
    # Filter to specific map
    map_df = day_df[day_df['map_id'] == selected_map]
    
    # 3. Match Selector
    available_matches = get_available_matches(map_df)
    if not available_matches:
        st.warning("No matches found for this map.")
        return
        
    selected_match = st.sidebar.selectbox("Match ID", available_matches)
    
    # Fetch specific match data
    match_df = get_match_data(map_df, selected_match)
    
    # Apply coordinate bounding box
    match_df = add_pixel_coordinates(match_df, clip_out_of_bounds=True)
    
    # --- SIDEBAR: Layer Toggles ---
    st.sidebar.markdown("---")
    st.sidebar.header("👁️ Visibility Layers")
    
    show_routes = st.sidebar.checkbox("Player Routes", value=True)
    show_events = st.sidebar.checkbox("Kill/Death Events", value=True)
    show_traffic = st.sidebar.checkbox("NavMesh Utilization (Traffic)", value=False)
    show_combat = st.sidebar.checkbox("Engagement Chokepoints (Combat)", value=False)
    show_underused = st.sidebar.checkbox("Dead Space (Cold Zones)", value=False)
    
    st.sidebar.markdown("---")
    st.sidebar.header("👥 Player Types")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        show_humans = st.checkbox("Humans", value=True)
    with col2:
        show_bots = st.checkbox("Bots", value=True)

    # Filtering logic for Entities
    allowed_types = []
    if show_humans: allowed_types.append("Human")
    if show_bots: allowed_types.append("Bot")
    current_df = match_df[match_df['player_type'].isin(allowed_types)]
    
    # --- TIMELINE FILTERING ---
    st.markdown("### Match Timeline")
    # Base slider bounds strictly on the unfiltered match_df to keep bounds constant
    if not match_df.empty and 'ts' in match_df.columns:
        match_min_ts = match_df['ts'].min()
        match_max_ts = match_df['ts'].max()
        
        if pd.notna(match_min_ts) and pd.notna(match_max_ts) and match_min_ts < match_max_ts:
            total_seconds = int((match_max_ts - match_min_ts).total_seconds())
            
            from datetime import datetime, timedelta
            # Use a dummy base time to trick the Streamlit slider into elegantly displaying mm:ss
            base_time = datetime(2000, 1, 1, 0, 0, 0)
            max_time = base_time + timedelta(seconds=total_seconds)
            
            slider_format = "HH:mm:ss" if total_seconds >= 3600 else "mm:ss"
            
            selected_dummy_ts = st.slider(
                "Match Playback", 
                min_value=base_time, 
                max_value=max_time, 
                value=max_time, 
                format=slider_format,
                step=timedelta(seconds=5)
            )
            
            # Map the dummy slider value back to the actual dataset timestamp
            elapsed_seconds = (selected_dummy_ts - base_time).total_seconds()
            selected_ts = match_min_ts + timedelta(seconds=elapsed_seconds)
            
            # Optional polish: explicit position read-out
            cur_m, cur_s = divmod(elapsed_seconds, 60)
            tot_m, tot_s = divmod(total_seconds, 60)
            st.markdown(f"**Elapsed Time:** `{int(cur_m):02d}:{int(cur_s):02d} / {int(tot_m):02d}:{int(tot_s):02d}`")
            
            # Filter current entity data up to the selected timestamp
            if not current_df.empty:
                current_df = current_df[current_df['ts'] <= selected_ts]
        else:
            st.info("Timeline too short to scrub. Showing full match.")
            
        # Add an elapsed time string so tooltips match the timeline slider format (e.g. 01:23)
        if not current_df.empty and 'ts' in match_df.columns:
            global_min = match_df['ts'].min()
            elapsed_seconds_s = (current_df['ts'] - global_min).dt.total_seconds()
            # Suppress warning for DataFrame slice mutation, since we overwrite the whole column
            current_df = current_df.copy()
            current_df['elapsed_str'] = elapsed_seconds_s.apply(lambda s: f"{int(s//60):02d}:{int(s%60):02d}")

    # --- TOP METRICS STRIP ---
    if not match_df.empty:
        # Calculate overall match stats
        humans_count = match_df[match_df['player_type'] == 'Human']['user_id'].nunique()
        bots_count = match_df[match_df['player_type'] == 'Bot']['user_id'].nunique()
        total_players = humans_count + bots_count
        
        total_duration = match_df['ts'].max() - match_df['ts'].min() if not match_df.empty and 'ts' in match_df.columns else pd.Timedelta(0)
        minutes, seconds = divmod(total_duration.total_seconds(), 60)
        duration_str = f"{int(minutes)}m {int(seconds)}s"
        
        # Calculate stats for the current timeframe
        kills_df = current_df[current_df['event'].isin(['Kill', 'Killed', 'BotKill', 'BotKilled'])]
        combat_events = len(kills_df)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Match Duration", duration_str)
        m2.metric("Total Players", total_players)
        m3.metric("Humans vs Bots", f"{humans_count} / {bots_count}")
        m4.metric("Combat Events", combat_events)
        
        # Calculate Designer Insights
        storm_deaths = len(current_df[current_df['event'] == 'KilledByStorm'])
        
        if not kills_df.empty and 'elapsed_str' in kills_df.columns:
            first_combat_str = kills_df.sort_values('ts').iloc[0]['elapsed_str']
        else:
            first_combat_str = "N/A"
        
        if not kills_df.empty and 'pixel_x' in kills_df.columns:
            sec_x = kills_df['pixel_x'] // 100
            sec_y = kills_df['pixel_y'] // 100
            hotspot = kills_df.groupby([sec_x, sec_y]).size().idxmax()
            hotspot_str = f"Sector {int(hotspot[0])}-{int(hotspot[1])}"
        else:
            hotspot_str = "None recorded"
            
        positions = current_df[current_df['event'].isin(['Position', 'BotPosition'])]
        if not positions.empty and 'pixel_x' in positions.columns:
            sec_x = positions['pixel_x'] // 100
            sec_y = positions['pixel_y'] // 100
            coldspot = positions.groupby([sec_x, sec_y]).size().idxmin()
            coldspot_str = f"Sector {int(coldspot[0])}-{int(coldspot[1])}"
        else:
            coldspot_str = "None recorded"

    # --- MAIN MAP VISUALIZATION ---
    st.markdown("---")
    
    img = load_minimap_image(selected_map)
    if img:
        with st.spinner("Rendering map layers..."):
            fig = render_full_minimap(
                img, 
                selected_map, 
                current_df,
                show_routes=show_routes,
                show_events=show_events,
                show_traffic=show_traffic,
                show_combat=show_combat,
                show_underused=show_underused
            )
            

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Minimap image could not be loaded. Please check player_data folder.")

    # --- DESIGNER INSIGHTS PANEL ---
    if not match_df.empty:
        st.markdown(f"""
            <div class="designer-insights">
                <h4>💡 Level Design Diagnostics</h4>
                <div style="display: flex; gap: 40px; margin-top: 10px;">
                    <div>
                        <strong>Time to First Engagement (Pacing):</strong> <span style="color:#FFB86C">{first_combat_str}</span>
                    </div>
                    <div>
                        <strong>Highest Engagement Chokepoint:</strong> <span style="color:#FF5555">{hotspot_str}</span>
                    </div>
                    <div>
                        <strong>Primary Dead Space:</strong> <span style="color:#50FA7B">{coldspot_str}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
