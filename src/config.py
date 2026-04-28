# Map Configurations
MAP_CONFIG = {
    "AmbroseValley": {
        "scale": 900,
        "origin_x": -370,
        "origin_z": -473,
        "image_path": "player_data/player_data/minimaps/AmbroseValley_Minimap.png"
    },
    "GrandRift": {
        "scale": 581,
        "origin_x": -290,
        "origin_z": -290,
        "image_path": "player_data/player_data/minimaps/GrandRift_Minimap.png"
    },
    "Lockdown": {
        "scale": 1000,
        "origin_x": -500,
        "origin_z": -500,
        "image_path": "player_data/player_data/minimaps/Lockdown_Minimap.jpg"
    }
}

# Image Dimension
MINIMAP_PIXELS = 1024

# UI Configuration — Orange / White / Dark theme
COLORS = {
    "Human": "#FF8C00",   # Vivid Orange for Humans
    "Bot": "#AAAAAA",     # Neutral Gray for Bots
}

# Event layer visual definitions (symbol, color, size)
EVENT_STYLES = {
    "BotKill":        {"symbol": "cross",       "color": "#FF6B35", "size": 13, "label": "Kills"},
    "BotKilled":      {"symbol": "x",           "color": "#FFFFFF", "size": 12, "label": "Deaths"},
    "KilledByStorm":  {"symbol": "diamond",     "color": "#A855F7", "size": 14, "label": "Storm Deaths"},
    "Loot":           {"symbol": "circle",       "color": "#38BDF8", "size":  7, "label": "Loot Pickups"},
    "Position":       {"symbol": "circle-open",  "color": "#FF8C00", "size":  4, "label": "Human Positions"},
    "BotPosition":    {"symbol": "circle-open",  "color": "#888888", "size":  4, "label": "Bot Positions"},
}
