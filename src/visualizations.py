import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import numpy as np

from src.config import MINIMAP_PIXELS, COLORS, EVENT_STYLES


def create_base_minimap_figure(img: Image.Image, map_name: str) -> go.Figure:
    """
    Creates a base Plotly figure with the minimap image as the background.
    Sets up the coordinate axes from 0 to 1024 (MINIMAP_PIXELS).
    """
    fig = go.Figure()

    if img is not None:
        # Add the image as a layout image background
        fig.add_layout_image(
            dict(
                source=img,
                xref="x",
                yref="y",
                x=0,
                y=MINIMAP_PIXELS,  # Top-left corner origin in Plotly layout image
                sizex=MINIMAP_PIXELS,
                sizey=MINIMAP_PIXELS,
                sizing="stretch",
                opacity=1.0,
                layer="below"
            )
        )

    # Configure axes to strictly match the 1024x1024 pixel grid
    fig.update_xaxes(showgrid=False, range=[0, MINIMAP_PIXELS], zeroline=False, visible=False)
    # Y-axis is NOT flipped here because Plotly places y=0 at the bottom.
    # We flipped it during the UV transform: `pixel_y = (1 - v) * 1024`.
    # Therefore, (0, 0) in Plotly matches the bottom-left of the image.
    fig.update_yaxes(showgrid=False, range=[0, MINIMAP_PIXELS], zeroline=False, visible=False)

    fig.update_layout(
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=10, b=0),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(20,20,20,0.85)",
            bordercolor="rgba(255,140,0,0.3)",
            borderwidth=1,
            font=dict(color="#E0E0E0", size=11),
        )
    )
    
    return fig


def add_player_trajectories(fig: go.Figure, df: pd.DataFrame):
    """
    Adds player movement paths to the figure.
    - Humans: Solid lines
    - Bots: Dotted lines
    Uses groupby to draw lines for each unique player.
    """
    if df.empty:
        return fig
        
    pos_events = df[df['event'].isin(['Position', 'BotPosition'])]
    
    for player_id, p_data in pos_events.groupby('user_id'):
        p_type = p_data['player_type'].iloc[0]
        color = COLORS.get(p_type, "#FFFFFF")
        dash_style = "solid" if p_type == "Human" else "dot"
        
        hover_text = p_data.apply(
            lambda r: f"ID: {r['user_id']}<br>Type: {p_type}<br>Event: {r['event']}<br>Time: {r.get('elapsed_str', 'N/A')}<br>Pos: ({r.get('x', 0):.0f}, {r.get('z', 0):.0f})", axis=1
        )
        
        fig.add_trace(go.Scatter(
            x=p_data['pixel_x'],
            y=p_data['pixel_y'],
            mode='lines+markers',
            line=dict(color=color, width=2, dash=dash_style),
            marker=dict(size=4, opacity=0.3, color=color),
            opacity=0.8,
            name=f"{p_type} Path",
            legendgroup=f"{p_type} Paths",
            showlegend=False, 
            hovertext=hover_text,
            hoverinfo='text'
        ))
        
    # Add dummy legend entries for the toggles
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='lines',
        line=dict(color=COLORS['Human'], width=3, dash='solid'),
        name='⬤  Human Paths',
        legendgroup='Human Paths'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='lines',
        line=dict(color=COLORS['Bot'], width=3, dash='dot'),
        name='◌  Bot Paths',
        legendgroup='Bot Paths'
    ))
    
    return fig


def add_event_markers(fig: go.Figure, df: pd.DataFrame):
    """
    Adds specific combat and item events as scatter markers.
    ALWAYS adds legend entries for every event type even when no data exists,
    so the legend always shows a complete professional tracker.
    """
    # Define the event groups we track and their mapping to raw event names
    event_groups = [
        {
            "key": "kills",
            "raw_events": ["BotKill"],
            "style_key": "BotKill",
            "legend_name": "⚔  Kills",
        },
        {
            "key": "deaths",
            "raw_events": ["BotKilled"],
            "style_key": "BotKilled",
            "legend_name": "☠  Deaths",
        },
        {
            "key": "storm_deaths",
            "raw_events": ["KilledByStorm"],
            "style_key": "KilledByStorm",
            "legend_name": "🌀  Storm Deaths",
        },
        {
            "key": "loot",
            "raw_events": ["Loot"],
            "style_key": "Loot",
            "legend_name": "💎  Loot Pickups",
        },
    ]
    
    for group in event_groups:
        style = EVENT_STYLES[group["style_key"]]
        subset = df[df['event'].isin(group["raw_events"])] if not df.empty else pd.DataFrame()
        
        if not subset.empty and 'pixel_x' in subset.columns:
            hover_text = subset.apply(
                lambda r: (
                    f"ID: {r['user_id']}<br>"
                    f"Event: {r['event']}<br>"
                    f"Time: {r.get('elapsed_str', 'N/A')}<br>"
                    f"Pos: ({r.get('x', 0):.0f}, {r.get('z', 0):.0f})"
                ), axis=1
            )
            fig.add_trace(go.Scatter(
                x=subset['pixel_x'],
                y=subset['pixel_y'],
                mode='markers',
                marker=dict(
                    symbol=style["symbol"],
                    size=style["size"],
                    color=style["color"],
                    line=dict(width=1, color='rgba(0,0,0,0.6)')
                ),
                name=group["legend_name"],
                hovertext=hover_text,
                hoverinfo='text',
                legendgroup="Events"
            ))
        else:
            # Always add a dummy trace so the legend entry is ALWAYS visible
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(
                    symbol=style["symbol"],
                    size=style["size"],
                    color=style["color"],
                    line=dict(width=1, color='rgba(0,0,0,0.6)')
                ),
                name=f"{group['legend_name']} (0)",
                legendgroup="Events",
                showlegend=True,
            ))
        
    return fig


def add_heatmaps(fig: go.Figure, df: pd.DataFrame, show_traffic: bool = True, show_combat: bool = True, show_underused: bool = True):
    """
    Generates three heatmap layers (Traffic, Combat, Underused).
    They are added as contour layers.
    """
    if df.empty:
        return fig
        
    # 1. General Traffic (Positions)
    if show_traffic or show_underused:
        positions = df[df['event'].isin(['Position', 'BotPosition'])]
    
    if show_traffic and not positions.empty:
        traffic_colors = [
            [0.0, 'rgba(0,0,0,0)'],
            [0.2, 'rgba(255,200,100,0.25)'],
            [0.6, 'rgba(255,140,0,0.45)'],
            [1.0, 'rgba(255,85,0,0.7)']
        ]
        fig.add_trace(go.Histogram2dContour(
            x=positions['pixel_x'], y=positions['pixel_y'],
            colorscale=traffic_colors,
            name='NavMesh Utilization',
            showscale=False,
            visible=True,
            legendgroup="Heatmaps",
            contours=dict(coloring='heatmap', showlines=False)
        ))
        
    # 2. Combat Heatmap (Kills + Deaths)
    if show_combat:
        combat = df[df['event'].isin(['Kill', 'Killed', 'BotKill', 'BotKilled'])]
        if not combat.empty:
            combat_colors = [
                [0.0, 'rgba(0,0,0,0)'],
                [0.3, 'rgba(255,100,50,0.4)'],
                [1.0, 'rgba(255,50,0,0.9)']
            ]
            fig.add_trace(go.Histogram2dContour(
                x=combat['pixel_x'], y=combat['pixel_y'],
                colorscale=combat_colors,
                name='Engagement Chokepoints',
                showscale=False,
                visible=True,
                legendgroup="Heatmaps",
                contours=dict(coloring='heatmap', showlines=False)
            ))

    # 3. Underused Areas Overlay
    if show_underused and not positions.empty:
        underused_colors = [
            [0.0, 'rgba(98,114,164,0.6)'],   # Cold/Empty areas are purpleish-blue
            [0.1, 'rgba(98,114,164,0.0)'],   # Fades to transparent quickly where there is traffic
            [1.0, 'rgba(0,0,0,0)']
        ]
        fig.add_trace(go.Histogram2dContour(
            x=positions['pixel_x'], y=positions['pixel_y'],
            colorscale=underused_colors,
            name='Dead Space (Cold Zones)',
            showscale=False,
            visible=True,
            legendgroup="Heatmaps",
            contours=dict(coloring='heatmap', showlines=False)
        ))
        
    return fig


def render_full_minimap(
    img: Image.Image, 
    map_name: str, 
    df_filtered: pd.DataFrame, 
    show_routes: bool = True, 
    show_events: bool = True, 
    show_traffic: bool = False, 
    show_combat: bool = False, 
    show_underused: bool = False
) -> go.Figure:
    """
    Orchestrates the entire rendering pipeline, optimized to only build traces if toggled on.
    """
    fig = create_base_minimap_figure(img, map_name)
    fig = add_heatmaps(fig, df_filtered, show_traffic, show_combat, show_underused)
    
    if show_routes:
        fig = add_player_trajectories(fig, df_filtered)
        
    if show_events:
        fig = add_event_markers(fig, df_filtered)
        
    return fig
