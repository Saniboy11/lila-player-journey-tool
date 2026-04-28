# LILA BLACK — Tactical Match Flow Analyzer

A spatial telemetry diagnostic tool built for level designers working on battle-royale map geometry. Rather than surface-level product metrics (DAU, ARPU), this tool answers a specific design question: **"Is my map flowing the way I intended?"**

It reconstructs full match timelines from raw Nakama telemetry, maps 3D world coordinates onto 2D minimaps, and layers combat events, movement heatmaps, and pacing diagnostics into a single interactive view.

## Key Capabilities

| Capability | What It Does | Design Question It Answers |
|---|---|---|
| **Match Timeline Scrubber** | Progressively reveals player positions and events from spawn → endgame | *"Where are players at the 2-minute mark? Are they looting or fighting?"* |
| **Human vs Bot Separation** | Classifies entities by user ID format (UUID = Human, short ID = Bot) | *"Are humans behaving differently from AI fill? Where do real players go?"* |
| **Spatial Heatmaps** | Toggleable layers for traffic density, combat chokepoints, and dead space | *"Which geometry is being ignored? Where are forced engagements?"* |
| **Event Markers** | Plots Kills, Deaths, Storm Eliminations, and Loot pickups with distinct icons | *"Where are players dying? Is it to combat or to the storm?"* |
| **Pacing Diagnostics** | Computes Time-to-First-Engagement, hottest chokepoint sector, coldest dead space | *"Is the early game too chaotic? Is mid-game stale?"* |

## Setup

```bash
git clone https://github.com/Saniboy11/lila-player-journey-tool.git
cd lila-player-journey-tool
pip install -r requirements.txt
streamlit run app.py
```

Extract the sample dataset into `player_data/` before launching.

## 🚀 Live App Link

### **[https://lila-player-journey-tool-47vbennpdn5luuwq3xcfxe.streamlit.app/](https://lila-player-journey-tool-47vbennpdn5luuwq3xcfxe.streamlit.app/)**

---

## 📽️ Video Walkthrough

**[Loom Demo](https://www.loom.com/share/7f2452c4c2544c7c9cd7e3ebad232ba6)**


## Walkthrough

1. **Select a date & load data.** Click ⚡ Load Match Data. Matches are ranked by human player presence so the most analytically relevant lobbies surface first.
2. **Observe movement flow.** Toggle "Routes" to see player dispersion from spawns across the map.
3. **Analyze pacing.** Check Time-to-First-Engagement in the diagnostics panel — values under 15 seconds signal spawn-point congestion.
4. **Scrub the timeline.** Drag the playback slider to watch trajectories and combat events unfold chronologically.
5. **Diagnose geometry.** Enable Traffic and Chokepoint heatmaps to identify forced combat zones and ignored dead space.

## Data Pipeline

```
437 Parquet files/day → ThreadPoolExecutor (8 workers, ~2s) → Pandas DataFrame
    → match_id aggregation → UV coordinate transform → Plotly trace compilation
```

## Future Improvements

- Migrate from Plotly to WebGL (Deck.gl) for smoother rendering at 10k+ coordinate points.
- Add elevation-based filtering to separate ground-level fights from verticality engagements.
- Implement spline interpolation for automated match playback animations.
