# Architecture

This document covers the technical decisions, data flow, and tradeoffs for the Match Flow Analyzer.

## Tech Stack
* **Streamlit:** Selected for rapid prototyping. It handles routing and state management natively, letting me focus entirely on data transformation and geospatial logic instead of frontend boilerplate.
* **Plotly:** Provides native interactivity (zooming, panning, hover tooltips) and layered vector graphics. It allowed me to stack heatmaps and event markers on a single axis.
* **PyArrow / Pandas:** Used for memory-efficient loading of Parquet files. Parquet's columnar compression is crucial here since Streamlit Cloud has strict 1GB memory limits.

## Data Flow
1. `data_loader.py` scans `player_data/` and reads the parquet files.
2. Fragmented telemetry is aggregated by `match_id`. Matches are sorted by total player count so the UI surfaces the most active 100-player lobbies first.
3. Raw world coordinates (x, y, z) are mapped to the 1024x1024 2D image grid.
4. `app.py` filters the dataset temporally based on the timeline scrubber. The subset is passed to `visualizations.py`, which compiles Plotly traces.

## Coordinate Mapping
I used standard UV mapping to translate 3D world coordinates to the 2D minimap grid:
```python
u = (world_x - origin_x) / scale
v = (world_z - origin_z) / scale

pixel_x = u * 1024
pixel_y = (1 - v) * 1024 # Y-axis inverted for top-left image origin alignment
```

## Assumptions
* **Timestamps:** The Parquet metadata listed `ts` in milliseconds, but the raw values were actually Unix epochs in seconds. I cast them to seconds to prevent the timeline logic from projecting matches as 1000x too long.
* **Data Completeness:** If a `match_id` is missing some player data, I assume a disconnect or shard crash. The tool handles incomplete data gracefully.
* **Elevation:** Verticality (Z-axis) is flattened for this 2D diagnostic tool. The focus is on horizontal flow and pacing for the MVP.

## Tradeoffs
* **Streamlit vs Custom React Frontend:** Streamlit is incredibly fast for building data apps, but it lacks client-side 60FPS animation loops.
* **Manual Scrubbing vs Autoplay:** I opted for a manual timeline scrubber rather than an automated playback feature, as automated loops in Streamlit require heavy `st.rerun` hacks that can degrade performance.
* **Lazy Loading:** Loading selected matches into RAM prevents Out-Of-Memory crashes, but introduces a small read latency when switching maps.
