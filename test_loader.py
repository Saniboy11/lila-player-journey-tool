import sys
sys.path.append('.')
from src.data_loader import load_day_data
import os

folder = r"c:\Users\sania\OneDrive\Desktop\lila-player-journey-tool\player_data\player_data\February_10"
df = load_day_data(folder)

print("Data Shape:", df.shape)
print("Columns:", df.columns.tolist())
print("Event Types:", df['event'].unique().tolist())
print("Player Types:", df['player_type'].value_counts().to_dict())
print("Unique Matches:", df['match_id'].nunique())
print("Total Memory Usage (MB):", df.memory_usage(deep=True).sum() / 1e6)

# Sample one match
if not df.empty:
    sample_match = df['match_id'].iloc[0]
    match_df = df[df['match_id'] == sample_match]
    print(f"\nSample Match ({sample_match}) - {len(match_df)} events")
    print(match_df[['ts', 'user_id', 'player_type', 'event']].head(10))
