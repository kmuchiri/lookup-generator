import json
from pathlib import Path
import pandas as pd

# Event name mapping for clean display titles
EVENT_NAMES = {
    "HJ": "High Jump", "PV": "Pole Vault", "LJ": "Long Jump", "TJ": "Triple Jump",
    "SP": "Shot Put", "DT": "Discus Throw", "HT": "Hammer Throw", "JT": "Javelin Throw",
    "Hept": "Heptathlon", "Dec": "Decathlon", "Pent": "Pentathlon",
    "HM": "Half Marathon", "HMW": "Half Marathon Walk", "Marathon": "Marathon",
    "MarW": "Marathon Walk"
}

subdatasets_dir = Path("data/table_subdatasets")
output_dir = Path("data/lookup")
output_dir.mkdir(exist_ok=True)

metadata = {}
merged_series = {}

# Full official range: 1 to 1400 points
all_points = pd.Index(range(1,1401), name="points")

for csv_file in sorted(subdatasets_dir.glob("*.csv")):
    code = csv_file.stem
    
    # Parse codes: e.g. "PV" and "MF" or "100m" and "WT"
    parts = code.rsplit("-", 1)
    event_raw = parts[0]
    tag = parts[1]
    
    gender = "Men" if tag[0] == "M" else "Women"
    is_field = (tag[1] == "F")
    category = "Field" if is_field else "Track"
    
    display_name = EVENT_NAMES.get(event_raw, event_raw.replace("_", " "))
    
    metadata[code] = {
        "discipline": display_name,
        "code": code,
        "gender": gender,
        "category": category,
        "unit": "m" if is_field else "s",
        "higher_is_better": is_field
    }
    
    # Read the parsed table
    df = pd.read_csv(csv_file).dropna()
    df = df.drop_duplicates(subset=["result_score"]).set_index("result_score")["mark"]
    
    series = df.reindex(all_points)
    
    merged_series[code] = series

# Combine into single DataFrame and sort 1400 down to 1
lookup_df = pd.DataFrame(merged_series, index=all_points).sort_index(ascending=False)

# Save lookup table and disciplines dictionary
csv_path = output_dir / "lookup_table.csv"
json_path = output_dir / "disciplines.json"

lookup_df.to_csv(csv_path)
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"Generated {csv_path} ({lookup_df.shape[0]} rows, {lookup_df.shape[1]} columns)")
print(f"Generated {json_path} ({len(metadata)} disciplines)")
