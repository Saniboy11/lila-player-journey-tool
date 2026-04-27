import plotly.graph_objects as go
import pandas as pd
from PIL import Image
import numpy as np

from src.config import MINIMAP_PIXELS, COLORS

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
        title=f"Player Journey Intelligence - {map_name}",
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=40, b=0),
        template="plotly_dark",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)"
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
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color=COLORS['Human'], width=2, dash='solid'), name='Human Paths', legendgroup='Human Paths'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color=COLORS['Bot'], width=2, dash='dot'), name='Bot Paths', legendgroup='Bot Paths'))
    
    return fig

def add_event_markers(fig: go.Figure, df: pd.DataFrame):
    """
    Adds specific combat and item events as scatter markers.
    """
    if df.empty:
        return fig
        
    # Separate event types for layer toggling
    kills = df[df['event'].isin(['Kill', 'BotKill'])]
    deaths = df[df['event'].isin(['Killed', 'BotKilled'])]
    storm_deaths = df[df['event'] == 'KilledByStorm']
    loot = df[df['event'] == 'Loot']
    
    if not kills.empty:
        fig.add_trace(go.Scatter(
            x=kills['pixel_x'], y=kills['pixel_y'],
            mode='markers',
            marker=dict(symbol='cross', size=12, color='#FF5555', line=dict(width=1, color='black')),
            name='Kills',
            hovertext=kills.apply(lambda r: f"ID: {r['user_id']}<br>Event: {r['event']}<br>Time: {r.get('elapsed_str', 'N/A')}<br>Pos: ({r.get('x', 0):.0f}, {r.get('z', 0):.0f})", axis=1),
            hoverinfo='text',
            legendgroup="Events"
        ))
        
    if not deaths.empty:
        fig.add_trace(go.Scatter(
            x=deaths['pixel_x'], y=deaths['pixel_y'],
            mode='markers',
            marker=dict(symbol='x', size=12, color='#FFB86C', line=dict(width=1, color='black')),
            name='Deaths',
            hovertext=deaths.apply(lambda r: f"ID: {r['user_id']}<br>Event: {r['event']}<br>Time: {r.get('elapsed_str', 'N/A')}<br>Pos: ({r.get('x', 0):.0f}, {r.get('z', 0):.0f})", axis=1),
            hoverinfo='text',
            legendgroup="Events"
        ))
        
    if not storm_deaths.empty:
        fig.add_trace(go.Scatter(
            x=storm_deaths['pixel_x'], y=storm_deaths['pixel_y'],
            mode='markers',
            marker=dict(symbol='diamond', size=14, color='#BD93F9', line=dict(width=1, color='black')),
            name='Storm Deaths',
            hovertext=storm_deaths.apply(lambda r: f"ID: {r['user_id']}<br>Event: {r['event']}<br>Time: {r.get('elapsed_str', 'N/A')}<br>Pos: ({r.get('x', 0):.0f}, {r.get('z', 0):.0f})", axis=1),
            hoverinfo='text',
            legendgroup="Events"
        ))
        
    if not loot.empty:
        fig.add_trace(go.Scatter(
            x=loot['pixel_x'], y=loot['pixel_y'],
            mode='markers',
            marker=dict(symbol='circle', size=6, color='#8BE9FD', opacity=0.7),
            name='Loot',
            hovertext=loot.apply(lambda r: f"ID: {r['user_id']}<br>Event: Loot<br>Time: {r.get('elapsed_str', 'N/A')}<br>Pos: ({r.get('x', 0):.0f}, {r.get('z', 0):.0f})", axis=1),
            hoverinfo='text',
            legendgroup="Events",
            visible='legendonly' 
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
            [0.2, 'rgba(241,250,140,0.3)'],
            [0.6, 'rgba(255,184,108,0.5)'],
            [1.0, 'rgba(255,85,85,0.7)']
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
                [0.3, 'rgba(255,85,85,0.4)'],
                [1.0, 'rgba(255,0,0,0.9)']
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
