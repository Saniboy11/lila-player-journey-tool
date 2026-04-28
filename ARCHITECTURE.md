# Technical Architecture

This document outlines the architectural decisions, data pipeline, and technical tradeoffs for the LILA BLACK Match Flow Analyzer.

## Tech Stack & Rationale

| Component | Technology | Rationale |
|---|---|---|
| **Frontend/Orchestration** | Streamlit | Rapid prototyping; native state management and Python integration. |
| **Visualization Engine** | Plotly | Interactive vector layers (zoom/pan/hover) with low-overhead heatmap support. |
| **Data Processing** | Pandas / PyArrow | Columnar performance and memory efficiency for high-frequency telemetry. |
| **Ingestion Engine** | Concurrent.futures | Parallelized I/O to handle 400+ files/day without blocking the UI. |

## Data Pipeline

1.  **Ingestion:** `data_loader.py` uses a `ThreadPoolExecutor` to perform parallel reads of daily Parquet shards.
2.  **Aggregation:** Fragmented player events are grouped by `match_id`. Lobbies are ranked by player count and "Human Density" to surface analytically valuable data.
3.  **Coordinate Projection:** 3D world coordinates (X, Z) are normalized into a 0-1 range (UV space) and projected onto a 1024x1024 pixel grid.
4.  **State Management:** Match data is cached in `st.session_state` to prevent redundant I/O, while temporal filtering is performed on-the-fly via the UI timeline scrubber.

## Coordinate Mapping Logic

The tool maps 3D game-engine coordinates to a 2D viewport. In this system, **X and Z represent the ground plane**, while **Y represents elevation (verticality)**.

```python
# UV Projection formula
u = (world_x - origin_x) / map_scale
v = (world_z - origin_z) / map_scale

pixel_x = u * 1024
pixel_y = (1 - v) * 1024  # Inverted for image origin alignment
```

*Note: For the current MVP, Y-axis data (elevation) is used for tooltips but flattened for 2D visualization.*

## Architectural Decision Table

| Decision | Selection | Tradeoff |
|---|---|---|
| **Frontend Framework** | Streamlit | **Pro:** 10x faster dev speed. **Con:** Limited to 1Hz UI refresh rate; no native WebGL animation loop. |
| **Data Handling** | On-Demand Loading | **Pro:** Prevents Out-Of-Memory (OOM) on Streamlit Cloud (1GB limit). **Con:** Small latency (1-2s) when switching days. |
| **Playback Logic** | Manual Scrubbing | **Pro:** Reliable performance and precision. **Con:** Lacks "Cinema-style" autoplay without complex `st.rerun` hacks. |
| **Telemetry Format** | Parquet | **Pro:** 80% smaller footprint than CSV; significantly faster columnar reads. **Con:** Requires specialized libraries (PyArrow) for ingestion. |

## Assumptions & Data Integrity

- **Time Fidelity:** Raw `ts` integers are treated as Unix seconds. A 1000x scaling factor was applied during normalization to fix a source-data unit discrepancy.
- **Entity Classification:** Entities with 4-digit IDs are flagged as "Bots" for noise reduction in tactical overlays.
- **Spatial Precision:** Coordinates are clipped to the map bounding box to prevent "Out-of-Bounds" artifacts caused by edge-case telemetry errors.
