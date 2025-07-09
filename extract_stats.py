import os
import pandas as pd
import re
from functools import reduce

# directory
base_dir = "/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_data/Freesurfer_data/subjects"

# stats files
stat_files = [
    "amygdalar-nuclei.lh.T1.v22.stats",
    "amygdalar-nuclei.rh.T1.v22.stats",
    "brainvol.stats",
    "hipposubfields.lh.T1.v22.stats",
    "hipposubfields.rh.T1.v22.stats"
]

# F parse one FreeSurfer stats file
def parse_stats_file(file_path, file_label, participant_id):
    data = {}
    if not os.path.exists(file_path):
        return None

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # CASE 1:  Measure" 
    for line in lines:
        match = re.match(r"# Measure [^,]+,\s*([^,]+),.*?,\s*([0-9eE.+-]+),", line)
        if match:
            label, value = match.groups()
            col_name = f"{file_label}_{label}"
            data[col_name] = float(value)

    # CASE 2: subfields
    for line in lines:
        if not line.startswith("#"):
            match = re.match(r"\s*\d+\s+\d+\s+\d+\s+([0-9eE.+-]+)\s+(.+)", line)
            if match:
                volume, label = match.groups()
                label = re.sub(r"\s+", "_", label.strip())
                col_name = f"{file_label}_{label}"
                data[col_name] = float(volume)

    # CASE 3: TableCol
    table_start = None
    for i, line in enumerate(lines):
        if not line.startswith("#") and table_start is None:
            # First non-comment line after header block = table start
            table_start = i
            break

    if table_start:
       
        try:
    # read table 
         df_table = pd.read_csv(file_path, comment="#", sep=r"\s+", engine='python')
    
         if 'StructName' in df_table.columns:
              for _, row in df_table.iterrows():
                  region = str(row['StructName']).strip()
                  for col in df_table.columns:
                     if col != 'StructName':
                        col_name = f"{file_label}_{region}_{col}"
                        data[col_name] = row[col]
        except Exception as e:
            print(f"Warning: Could not parse table in {file_path}: {e}")

    if data:
        df = pd.DataFrame([data])
        df.insert(0, "Participant", participant_id)
        return df
    return None

# loop through all participant folders
participants = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("MR")]

# loop through each participant and extract stats
all_dfs = []

for participant in participants:
    participant_dfs = []
    for file in stat_files:
        file_path = os.path.join(base_dir, participant, "stats", file)
        file_label = os.path.splitext(file)[0]
        df = parse_stats_file(file_path, file_label, participant)
        if df is not None:
            participant_dfs.append(df)

    if participant_dfs:
        combined = reduce(lambda left, right: pd.merge(left, right, on="Participant", how="outer"), participant_dfs)
        all_dfs.append(combined)

# merge all participant data into a single wide-format dataframe
if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    output_path = "/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_data/Freesurfer_data/wholebrain_subregions.csv"
    final_df.to_csv(output_path, index=False)
    print(f"✅ Done! Data saved to {output_path}")
else:
    print("⚠️ No data extracted.")
