import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# ──────────────────────────────────────────────────────────────────
# Page Configuration — must be first Streamlit command
# ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LILA BLACK | Tactical Match Flow Analyzer",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────────
# Professional CSS — Orange / White / Dark Theme, Responsive
# ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ─────────────────────────── */
    html, body,
    .stMarkdown, .stText, .stAlert,
    p, span, div, label, li, td, th,
    input, textarea, select, button {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    /* Protect Streamlit's internal icon fonts from being overridden */
    [data-testid="collapsedControl"] *,
    [data-testid="stToolbar"] *,
    [data-testid="stStatusWidget"] *,
    .stIcon, svg, i,
    [class*="icon"], [class*="Icon"] {
        font-family: inherit !important;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    h1, h2, h3, h4 { font-family: 'Inter', sans-serif; }

    /* ── Sidebar ────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111111 0%, #1A1A1A 100%);
        border-right: 1px solid rgba(255,140,0,0.15);
    }
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #FF8C00 !important;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.4rem;
    }

    /* ── Header Banner ──────────────────── */
    .lila-header {
        background: linear-gradient(135deg, #1A1A1A 0%, #111111 50%, #1A1A1A 100%);
        border: 1px solid rgba(255,140,0,0.2);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
    }
    .lila-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #FF8C00 50%, transparent 100%);
    }
    .lila-header h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF8C00, #FFB347);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    .lila-header p {
        margin: 4px 0 0 0;
        font-size: 0.78rem;
        color: #888;
        letter-spacing: 0.5px;
    }

    /* ── Metric Cards ───────────────────── */
    .metric-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: linear-gradient(145deg, #1A1A1A, #141414);
        border: 1px solid rgba(255,140,0,0.12);
        border-radius: 10px;
        padding: 16px 18px;
        text-align: center;
        transition: border-color 0.3s ease, transform 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(255,140,0,0.4);
        transform: translateY(-2px);
    }
    .metric-card .mc-icon {
        font-size: 1.3rem;
        margin-bottom: 4px;
    }
    .metric-card .mc-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
    }
    .metric-card .mc-label {
        font-size: 0.7rem;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 2px;
    }

    /* ── Event Tracker Strip ────────────── */
    .event-tracker {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 1.2rem;
    }
    .event-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #1A1A1A;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.75rem;
        color: #CCC;
        transition: border-color 0.3s ease;
    }
    .event-badge:hover {
        border-color: rgba(255,140,0,0.4);
    }
    .event-badge .eb-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .event-badge .eb-count {
        font-weight: 700;
        color: #FF8C00;
    }
    .event-badge.active {
        border-color: rgba(255,140,0,0.35);
        background: rgba(255,140,0,0.06);
    }

    /* ── Section Headers ────────────────── */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    /* ── Timeline Display ───────────────── */
    .time-readout {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #141414;
        border: 1px solid rgba(255,140,0,0.15);
        border-radius: 8px;
        padding: 8px 16px;
        font-family: 'Inter', monospace;
        font-size: 0.85rem;
        font-weight: 600;
        color: #FF8C00;
        margin-top: 6px;
        margin-bottom: 12px;
    }
    .time-readout .tr-total {
        color: #666;
        font-weight: 400;
    }

    /* ── Insights Panel ─────────────────── */
    .insights-panel {
        background: linear-gradient(145deg, #1A1A1A, #141414);
        border: 1px solid rgba(255,140,0,0.12);
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 16px;
        position: relative;
        overflow: hidden;
    }
    .insights-panel::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #FF8C00, #FF6B35);
        border-radius: 3px 0 0 3px;
    }
    .insights-panel h4 {
        margin: 0 0 14px 0;
        font-size: 0.85rem;
        font-weight: 700;
        color: #FF8C00;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
    }
    .insight-item {
        background: rgba(255,255,255,0.02);
        border-radius: 8px;
        padding: 12px 14px;
    }
    .insight-item .ii-label {
        font-size: 0.65rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
    }
    .insight-item .ii-value {
        font-size: 1.05rem;
        font-weight: 600;
        color: #E0E0E0;
    }

    /* ── Welcome Screen ─────────────────── */
    .welcome-card {
        background: linear-gradient(145deg, #1A1A1A, #111111);
        border: 1px solid rgba(255,140,0,0.15);
        border-radius: 16px;
        padding: 48px 40px;
        text-align: center;
        max-width: 580px;
        margin: 60px auto;
    }
    .welcome-card .wc-icon { font-size: 2.8rem; margin-bottom: 12px; }
    .welcome-card h2 {
        color: #FFF;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .welcome-card p {
        color: #888;
        font-size: 0.82rem;
        line-height: 1.6;
        margin: 0;
    }

    /* ── Responsive fixes ───────────────── */
    @media (max-width: 768px) {
        .main .block-container { padding-left: 1rem; padding-right: 1rem; }
        .lila-header { padding: 14px 16px; }
        .lila-header h1 { font-size: 1.15rem; }
        .metric-row { grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .metric-card { padding: 12px 10px; }
        .metric-card .mc-value { font-size: 1.15rem; }
        .event-tracker { gap: 6px; }
        .event-badge { padding: 5px 10px; font-size: 0.68rem; }
        .insights-grid { grid-template-columns: 1fr; }
        .insight-item { padding: 10px 12px; }
        .welcome-card { padding: 32px 20px; margin: 30px auto; }
    }

    /* ── Hide default Streamlit footer ──── */
    footer { visibility: hidden; }

    /* ── Plotly chart responsive container ─ */
    .stPlotlyChart > div { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────────────
from src.data_loader import load_day_data, get_match_data, get_available_matches, audit_data_sanity
from src.map_utils import add_pixel_coordinates, load_minimap_image, get_coordinate_sanity_stats
from src.visualizations import render_full_minimap

DATA_DIR = os.path.join("player_data", "player_data")


# ──────────────────────────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────────────────────────
def main():
    # ── Header Banner ──
    st.markdown("""
        <div class="lila-header">
            <h1>🔥 LILA BLACK — Tactical Match Flow Analyzer</h1>
            <p>Real-time telemetry diagnostics for level designers  ·  Player Journey Intelligence System</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ── Sidebar: Data Selection ──
    st.sidebar.markdown("### 🎯 Match Selection")
    
    available_dates = ["February_10", "February_11", "February_12", "February_13", "February_14"]
    selected_date = st.sidebar.selectbox("Date", available_dates, label_visibility="collapsed")

    load_btn = st.sidebar.button("⚡ Load Match Data", type="primary", use_container_width=True)

    if not load_btn and "day_df" not in st.session_state:
        st.markdown("""
            <div class="welcome-card">
                <div class="wc-icon">🗺️</div>
                <h2>Welcome to LILA BLACK</h2>
                <p>Select a date from the sidebar and click <strong>⚡ Load Match Data</strong> to begin analyzing player telemetry flows, combat chokepoints, and navigation patterns.</p>
            </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Load data (cached after first load)
    folder_path = os.path.join(DATA_DIR, selected_date)
    if load_btn or "loaded_date" not in st.session_state or st.session_state.get("loaded_date") != selected_date:
        with st.spinner(f"Loading {selected_date}…"):
            st.session_state["day_df"] = load_day_data(folder_path)
            st.session_state["loaded_date"] = selected_date

    day_df = st.session_state["day_df"]

    if day_df.empty:
        st.warning(f"No data found for {selected_date}.")
        st.stop()

    # ── Map Filter ──
    if 'map_id' in day_df.columns:
        available_maps = sorted(day_df['map_id'].dropna().unique().tolist())
    else:
        available_maps = []

    if not available_maps:
        st.warning("No map data found in dataset.")
        return

    selected_map = st.sidebar.selectbox("Map", available_maps, label_visibility="collapsed")

    # Filter to specific map
    map_df = day_df[day_df['map_id'] == selected_map]

    # ── Match Selector ──
    available_matches = get_available_matches(map_df)
    if not available_matches:
        st.warning("No matches found for this map.")
        return
        
    selected_match = st.sidebar.selectbox("Match ID", available_matches, label_visibility="collapsed")
    
    # Fetch specific match data
    match_df = get_match_data(map_df, selected_match)
    
    # Apply coordinate bounding box
    match_df = add_pixel_coordinates(match_df, clip_out_of_bounds=True)
    
    # ── Sidebar: Layer Toggles ──
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👁️ Visibility Layers")
    
    show_routes = st.sidebar.checkbox("Player Routes", value=True)
    show_events = st.sidebar.checkbox("Kill/Death Events", value=True)
    show_traffic = st.sidebar.checkbox("NavMesh Utilization", value=False)
    show_combat = st.sidebar.checkbox("Engagement Chokepoints", value=False)
    show_underused = st.sidebar.checkbox("Dead Space (Cold Zones)", value=False)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👥 Player Filters")
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
    
    # ──────────────────────────────────────────────────────────
    # TOP METRICS STRIP
    # ──────────────────────────────────────────────────────────
    if not match_df.empty:
        humans_count = match_df[match_df['player_type'] == 'Human']['user_id'].nunique()
        bots_count = match_df[match_df['player_type'] == 'Bot']['user_id'].nunique()
        total_players = humans_count + bots_count
        
        total_duration = match_df['ts'].max() - match_df['ts'].min() if 'ts' in match_df.columns else pd.Timedelta(0)
        minutes, seconds = divmod(total_duration.total_seconds(), 60)
        duration_str = f"{int(minutes)}m {int(seconds)}s"
        
        # Combat counts on the FULL match (not time-filtered)
        full_kills = len(match_df[match_df['event'].isin(['BotKill'])])
        full_deaths = len(match_df[match_df['event'].isin(['BotKilled'])])
        full_storm = len(match_df[match_df['event'] == 'KilledByStorm'])
        full_loot = len(match_df[match_df['event'] == 'Loot'])
        
        st.markdown('<div class="section-label">Match Overview</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card">
                    <div class="mc-icon">⏱️</div>
                    <div class="mc-value">{duration_str}</div>
                    <div class="mc-label">Match Duration</div>
                </div>
                <div class="metric-card">
                    <div class="mc-icon">👥</div>
                    <div class="mc-value">{total_players}</div>
                    <div class="mc-label">Total Players</div>
                </div>
                <div class="metric-card">
                    <div class="mc-icon">🧑</div>
                    <div class="mc-value">{humans_count}</div>
                    <div class="mc-label">Humans</div>
                </div>
                <div class="metric-card">
                    <div class="mc-icon">🤖</div>
                    <div class="mc-value">{bots_count}</div>
                    <div class="mc-label">Bots</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ── Event Tracker Strip — always shows ALL event types ──
        st.markdown('<div class="section-label">Event Tracker</div>', unsafe_allow_html=True)
        
        kill_cls = "active" if full_kills > 0 else ""
        death_cls = "active" if full_deaths > 0 else ""
        storm_cls = "active" if full_storm > 0 else ""
        loot_cls = "active" if full_loot > 0 else ""

        st.markdown(f"""
            <div class="event-tracker">
                <div class="event-badge {kill_cls}">
                    <span class="eb-dot" style="background:#FF6B35;"></span>
                    ⚔ Kills
                    <span class="eb-count">{full_kills}</span>
                </div>
                <div class="event-badge {death_cls}">
                    <span class="eb-dot" style="background:#FFFFFF;"></span>
                    ☠ Deaths
                    <span class="eb-count">{full_deaths}</span>
                </div>
                <div class="event-badge {storm_cls}">
                    <span class="eb-dot" style="background:#A855F7;"></span>
                    🌀 Storm Deaths
                    <span class="eb-count">{full_storm}</span>
                </div>
                <div class="event-badge {loot_cls}">
                    <span class="eb-dot" style="background:#38BDF8;"></span>
                    💎 Loot Pickups
                    <span class="eb-count">{full_loot}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # TIMELINE FILTERING
    # ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Match Timeline</div>', unsafe_allow_html=True)

    if not match_df.empty and 'ts' in match_df.columns:
        match_min_ts = match_df['ts'].min()
        match_max_ts = match_df['ts'].max()
        
        if pd.notna(match_min_ts) and pd.notna(match_max_ts) and match_min_ts < match_max_ts:
            total_seconds = int((match_max_ts - match_min_ts).total_seconds())
            
            base_time = datetime(2000, 1, 1, 0, 0, 0)
            max_time = base_time + timedelta(seconds=total_seconds)
            
            slider_format = "HH:mm:ss" if total_seconds >= 3600 else "mm:ss"
            
            selected_dummy_ts = st.slider(
                "Match Playback", 
                min_value=base_time, 
                max_value=max_time, 
                value=max_time, 
                format=slider_format,
                step=timedelta(seconds=5),
                label_visibility="collapsed"
            )
            
            # Map the dummy slider value back to the actual dataset timestamp
            elapsed_seconds = (selected_dummy_ts - base_time).total_seconds()
            selected_ts = match_min_ts + timedelta(seconds=elapsed_seconds)
            
            cur_m, cur_s = divmod(elapsed_seconds, 60)
            tot_m, tot_s = divmod(total_seconds, 60)
            st.markdown(f"""
                <div class="time-readout">
                    ⏱ {int(cur_m):02d}:{int(cur_s):02d}
                    <span class="tr-total">/ {int(tot_m):02d}:{int(tot_s):02d}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Filter current entity data up to the selected timestamp
            if not current_df.empty:
                current_df = current_df[current_df['ts'] <= selected_ts]
        else:
            st.info("Timeline too short to scrub. Showing full match.")
            
        # Add an elapsed time string so tooltips match the timeline slider format
        if not current_df.empty and 'ts' in match_df.columns:
            global_min = match_df['ts'].min()
            elapsed_seconds_s = (current_df['ts'] - global_min).dt.total_seconds()
            current_df = current_df.copy()
            current_df['elapsed_str'] = elapsed_seconds_s.apply(lambda s: f"{int(s//60):02d}:{int(s%60):02d}")

    # ──────────────────────────────────────────────────────────
    # MAIN MAP VISUALIZATION
    # ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Tactical Map</div>', unsafe_allow_html=True)
    
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

    # ──────────────────────────────────────────────────────────
    # DESIGNER INSIGHTS PANEL
    # ──────────────────────────────────────────────────────────
    if not match_df.empty:
        # Recalculate based on current (time-filtered) data
        kills_df = current_df[current_df['event'].isin(['BotKill', 'BotKilled'])] if not current_df.empty else pd.DataFrame()
        
        if not kills_df.empty and 'elapsed_str' in kills_df.columns:
            first_combat_str = kills_df.sort_values('ts').iloc[0]['elapsed_str']
        else:
            first_combat_str = "—"
        
        if not kills_df.empty and 'pixel_x' in kills_df.columns:
            sec_x = kills_df['pixel_x'] // 100
            sec_y = kills_df['pixel_y'] // 100
            hotspot = kills_df.groupby([sec_x, sec_y]).size().idxmax()
            hotspot_str = f"Sector {int(hotspot[0])}-{int(hotspot[1])}"
        else:
            hotspot_str = "No data"
            
        positions = current_df[current_df['event'].isin(['Position', 'BotPosition'])] if not current_df.empty else pd.DataFrame()
        if not positions.empty and 'pixel_x' in positions.columns:
            sec_x = positions['pixel_x'] // 100
            sec_y = positions['pixel_y'] // 100
            coldspot = positions.groupby([sec_x, sec_y]).size().idxmin()
            coldspot_str = f"Sector {int(coldspot[0])}-{int(coldspot[1])}"
        else:
            coldspot_str = "No data"

        storm_count = len(current_df[current_df['event'] == 'KilledByStorm']) if not current_df.empty else 0

        st.markdown(f"""
            <div class="insights-panel">
                <h4>💡 Level Design Diagnostics</h4>
                <div class="insights-grid">
                    <div class="insight-item">
                        <div class="ii-label">Time to First Engagement</div>
                        <div class="ii-value" style="color:#FF8C00;">{first_combat_str}</div>
                    </div>
                    <div class="insight-item">
                        <div class="ii-label">Highest Engagement Chokepoint</div>
                        <div class="ii-value" style="color:#FF6B35;">{hotspot_str}</div>
                    </div>
                    <div class="insight-item">
                        <div class="ii-label">Primary Dead Space</div>
                        <div class="ii-value" style="color:#AAAAAA;">{coldspot_str}</div>
                    </div>
                    <div class="insight-item">
                        <div class="ii-label">Storm Casualties</div>
                        <div class="ii-value" style="color:#A855F7;">{storm_count}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ── Footer ──
    st.markdown("""
        <div style="text-align:center; padding:24px 0 8px 0; border-top:1px solid rgba(255,255,255,0.04); margin-top:32px;">
            <span style="font-size:0.65rem; color:#555; letter-spacing:1px;">LILA BLACK  ·  PLAYER JOURNEY INTELLIGENCE  ·  INTERNAL TOOL</span>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
