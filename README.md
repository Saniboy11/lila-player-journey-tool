# LILA BLACK Match Flow Analyzer

A tactical telemetry visualization tool built for level designers. Instead of generic analytics (DAU, ARPU), this tool focuses on spatial awareness, map pacing, and geometry utilization to help designers validate map flow using production gameplay data.

## Features
* **Progressive Match Timeline:** Scrub through matches using an elapsed-time timeline to watch engagements unfold chronologically.
* **Level Design Diagnostics:** Extracts pacing metrics like Time-to-First-Engagement and identifies dead space.
* **Spatial Heatmaps:** Toggleable layers for NavMesh Utilization, Engagement Chokepoints, and Cold Zones.
* **Event Rendering:** Differentiates Humans vs Bots, and plots distinct markers for Kills, Deaths, Storm Eliminations, and Loot.
* **Match Reconstruction:** Groups fragmented player telemetry to stitch together full 100-player lobbies.

## Setup
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Extract the sample dataset into the `player_data/` directory.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment
Live deployment: [Streamlit Cloud Link Placeholder]

## Walkthrough
1. **Select a Match:** Use the sidebar filters. Matches are sorted by player count to surface the most action-packed data first.
2. **Observe Flow:** Toggle "Player Routes" to see dispersion from spawns.
3. **Analyze Pacing:** Check "Time to First Engagement" in the diagnostics panel to see if players clash too early.
4. **Scrub Timeline:** Drag the playback slider to watch trajectories and combat events reveal progressively.
5. **Diagnose Geometry:** Use the NavMesh and Chokepoint heatmaps to identify forced combat zones and ignored dead space.

## Future Improvements
* Migrate from Plotly to WebGL (Deck.gl/Kepler.gl) for smoother rendering of 10k+ coordinate points.
* Implement spline-based path interpolation for automated match playback.
* Add elevation filters to differentiate ground-level fights from rooftop combat.
