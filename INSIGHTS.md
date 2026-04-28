# Match Flow Insights

Actionable level design findings derived from the February 10–14 telemetry dataset using the Tactical Match Flow Analyzer. Each insight is tied to a specific metric, a root cause diagnosis, and a proposed design intervention.

---

### 1. Early-Game Storm Attrition on GrandRift

| Metric | Value |
|---|---|
| `KilledByStorm` events (GrandRift, Feb 10–14) | 13 total, clustered in NE quadrant |
| Median storm death timestamp | ~04:10 elapsed |
| Traffic density in kill zone (NavMesh heatmap) | Top 15% — high early-game foot traffic |

**Observation:** Players drop into the northeast POI for high-tier loot but fail to rotate before the first circle closes. The NavMesh heatmap confirms heavy early traffic here, but the zone contracts faster than players can extract.

**Why designers should care:** Storm deaths in the first 5 minutes signal a pacing failure — players are punished for engaging with map content the designer intentionally placed. This creates early frustration churn and reduces mid-game lobby density.

**Proposed fix:** Add mobility mechanics (jump-pads or ziplines) near this POI, or shift loot spawns 15–20% closer to center to reduce extraction distance.

---

### 2. Dead Space in the Lockdown Courtyard

| Metric | Value |
|---|---|
| Traffic density in central courtyard | Bottom 5% — flagged as primary Dead Space |
| Kill density in surrounding buildings | Top 20% — "donut effect" engagement ring |
| Courtyard traversals per match (Position events) | < 3 average |

**Observation:** Lockdown's central courtyard is architecturally prominent but functionally dead. The Engagement Chokepoint heatmap reveals a donut pattern — kills concentrate in the surrounding buildings while the open courtyard is actively avoided. Players refuse to cross exposed sightlines.

**Why designers should care:** Underutilized geometry represents wasted development resources and compresses viable combat space. When 40% of the map is avoided, the remaining 60% becomes overcrowded, increasing RNG-driven encounters and reducing tactical depth.

**Proposed fix:** Add structural cover (crates, dropships, trenches) to the courtyard center to break sniper sightlines. This redistributes combat pressure and incentivizes use of the center geometry.

---

### 3. Spawn Clumping on AmbroseValley

| Metric | Value |
|---|---|
| Time-to-First-Engagement (AmbroseValley, high-pop matches) | < 15 seconds |
| Kill events at 00:00–00:30 | 35–50% of total match kills |
| Spawn-zone kill overlap | > 80% of first-30s kills occur within drop zones |

**Observation:** In populated AmbroseValley lobbies, scrubbing the timeline to 00:30 reveals massive kill clusters directly overlapping initial drop zones. Players are forced into 50/50 RNG gunfights before they can loot a weapon.

**Why designers should care:** Sub-15-second first engagements eliminate the looting phase entirely. This compresses the early game into a coin-flip survival check, punishes late-droppers disproportionately, and can degrade session-over-session retention when players perceive deaths as "unfair."

**Proposed fix:** Expand drop zone radius by 25–30% or increase minimum distance between spawn clusters. Goal: push median Time-to-First-Engagement above 30 seconds so players have time to arm before their first tactical decision.
