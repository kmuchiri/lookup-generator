import os
import re
import csv
import subprocess


# Variables
pdf_path = "pdf/WA_Score_Table_2025.pdf"
txt_path = "data/raw_tables_temp.txt"
out_dir = "data/table_subdatasets"


def time_to_seconds(s):
    """Converts MM:SS or HH:MM:SS to total seconds. """
    if not s or s == '-': return None
    s = s.replace(',', '.')
    
    if ':' in s:
        parts = s.split(':')
        try:
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
        except ValueError:
            return None
            
    try:
        return float(s)
    except ValueError:
        return None

def is_field_event(sport_name):
    """Determine if an event is Track (T) or Field (F)."""
    field_events = {'HJ', 'PV', 'LJ', 'TJ', 'SP', 'DT', 'HT', 'JT', 'Hept', 'Dec', 'Pent'}
    for fe in field_events:
        if sport_name.startswith(fe):
            return True
    return False

def format_event_name(sport_name):
    """Apply specific formatting rules e.g. 'W' to 'Walk'."""
    name = sport_name
    
    # Handle Walk events
    if name.endswith('_W'):
        name = name[:-2] + "Walk"
    elif name.endswith('mW'):
        name = name[:-2] + "mWalk"
        
    return name

def main():
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find {pdf_path}")
        return

    print("Converting PDF to text...")
    # Use pdftotext to extract text while maintaining table layout
    subprocess.run(["pdftotext", "-layout", pdf_path, txt_path], check=True)

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_gender = "M" # Defaults to Men initially
    sports_data = {}
    
    # Pre-process columns that have spaces in them so they don't break split()
    replacements = {
        "1000m sh": "1000m_sh", "100 km": "100km", "10 km": "10km",
        "10km W": "10km_W", "10 Miles": "10Miles", "1500m sh": "1500m_sh",
        "15 km": "15km", "15km W": "15km_W", "2000m SC": "2000m_SC",
        "3000m SC": "3000m_SC", "2000m sh": "2000m_sh", "200m sh": "200m_sh",
        "20 km": "20km", "20km W": "20km_W", "25 km": "25km",
        "2 Miles sh": "2Miles_sh", "2 Miles": "2Miles", "3000m sh": "3000m_sh",
        "300m sh": "300m_sh", "30 km": "30km", "30km W": "30km_W",
        "35 km W": "35km_W", "35km W": "35km_W", "3km W": "3km_W",
        "400m sh": "400m_sh", "4x200m sh": "4x200m_sh", "4x400mix sh": "4x400mix_sh",
        "4x400m sh": "4x400m_sh", "5000m sh": "5000m_sh", "500m sh": "500m_sh",
        "50km W": "50km_W", "5 km": "5km", "5km W": "5km_W",
        "600m sh": "600m_sh", "800m sh": "800m_sh", "Hept. sh": "Hept_sh",
        "Pent. sh": "Pent_sh", "Mile sh": "Mile_sh", "Half Marathon": "HalfMarathon",
        "Hept.": "Hept", "Pent.": "Pent", "Dec.": "Dec",
        "20,000mW": "20000mW", "30,000mW": "30000mW", "35,000mW": "35000mW",
        "50,000mW": "50000mW", "10,000mW": "10000mW", "15,000mW": "15000mW"
    }
    
    in_table = False
    current_columns = []
    points_idx = -1
    
    for line in lines:
        # Detect Gender sections
        upper_line = line.upper()
        if "WOMEN" in upper_line:
            current_gender = "W"
        elif "MEN" in upper_line:
            current_gender = "M"
            
        line_clean = line
        for k, v in replacements.items():
            line_clean = line_clean.replace(k, v)
        
        tokens = line_clean.split()
        if not tokens:
            continue
            
        # Detect Header Row
        if "Points" in tokens:
            if tokens[0] == "Points" or tokens[-1] == "Points":
                in_table = True
                current_columns = tokens
                points_idx = current_columns.index("Points")
                continue
                
        # Process Data Row
        if in_table:
            # End of table if column counts don't match
            if len(tokens) != len(current_columns):
                in_table = False
                continue
                
            try:
                points_val = int(tokens[points_idx])
                for i, col in enumerate(current_columns):
                    if i == points_idx: 
                        continue
                        
                    sport = format_event_name(col)
                    event_type = "F" if is_field_event(sport) else "T"
                    
                    # Construct file name
                    key = f"{sport}-{current_gender}{event_type}"
                    val = time_to_seconds(tokens[i])
                    
                    if val is not None:
                        if key not in sports_data:
                            sports_data[key] = []
                        sports_data[key].append({
                            'result_score': points_val,
                            'mark': val
                        })
            except ValueError:
                # if the Points column is empty or non-integer
                in_table = False
                
    # Clean up the intermediate txt file
    if os.path.exists(txt_path):
        os.remove(txt_path)
    
    # Save the files
    for sport, data in sports_data.items():
        # Writing all unique pairs to avoid data loss.
        unique_data = {}
        for row in data:
            if row['result_score'] not in unique_data:
                unique_data[row['result_score']] = row['mark']
        
        sorted_scores = sorted(unique_data.keys(), reverse=True)
        
        filename = os.path.join(out_dir, f"{sport}.csv")
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['result_score', 'mark'])
            writer.writeheader()
            for score in sorted_scores:
                writer.writerow({'result_score': score, 'mark': unique_data[score]})
                
    print(f"Successfully parsed and created {len(sports_data)} CSV files in '{out_dir}/' directory.")

if __name__ == '__main__':
    main()
