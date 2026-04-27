# Match Flow Insights

This document outlines key map design and pacing issues identified using the analyzer tool, along with proposed fixes.

### 1. Early-Game Storm Deaths on GrandRift
When filtering for `KilledByStorm` events on GrandRift, there's a recurring cluster of storm deaths in the extreme top-right quadrant happening around the 4-minute mark. 

The NavMesh Utilization heatmap shows high early-game traffic here, meaning players are dropping for high-tier loot but failing to rotate out before the first circle closes. 
**Proposed Fix:** Add mobility mechanics (jump-pads or ziplines) near this POI, or shift the loot spawns slightly closer to the map's center to prevent early-game frustration churn.

### 2. Dead Space in the Lockdown Courtyard
Lockdown features a large central courtyard, but the spatial analysis flags it as primary "Dead Space". 

The Engagement Chokepoints heatmap shows a "donut effect"—kills are heavily concentrated in the surrounding buildings, while the open courtyard has almost zero traffic. Players are actively avoiding the direct line of sight.
**Proposed Fix:** Add structural cover (crates, dropships, or trenches) to the center. This will break up sniper sightlines and incentivize players to utilize the center map geometry, balancing the chokepoint congestion in the peripheral buildings.

### 3. Off-Spawn Clumping on AmbroseValley
In highly populated matches on AmbroseValley, the "Time-to-First-Engagement" metric frequently triggers under 15 seconds.

Scrubbing the timeline to 00:30 reveals massive clusters of kills directly overlapping with the initial drop zones. Players are forced into 50/50 RNG gunfights immediately upon landing, which breaks the intended looting phase pacing.
**Proposed Fix:** Expand the radius of the initial drop zones or increase the distance between spawn clusters. This gives players time to arm themselves and leads to higher-quality tactical engagements in the mid-game.
