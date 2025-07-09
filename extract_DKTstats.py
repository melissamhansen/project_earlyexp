import os
import pandas as pd
from functools import reduce

base_dir = "/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_data/Freesurfer_data/subjects"

dkt_files = [
    "lh.aparc.a2009s.stats",
    "lh.aparc.DKTatlas.stats",
    "rh.aparc.a2009s.stats",
    "rh.aparc.DKTatlas.stats"
]

def parse_aparc_stats(file_path, file_label, participant_id):
    data = {}
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        lines = f.readlines()

    table_start = next((i for i, line in enumerate(lines) if not line.startswith("#")), None)
    if table_start is None:
        return None

    try:
        df_table = pd.read_csv(
            file_path,
            comment="#",
            sep=r"\s+",
            skiprows=table_start,
            names=[
              "StructName", "NumVert", "SurfArea", "GrayVol", "ThickAvg",
                "ThickStd", "MeanCurv", "GausCurv", "FoldInd", "CurvInd"
            ],
            engine="python"
        )

        for _, row in df_table.iterrows():
            region = str(row['StructName']).strip()
            for col in df_table.columns:
                if col != "StructName":
                    data[f"{file_label}_{region}_{col}"] = row[col]
    except Exception as e:
        print(f"⚠️ Failed to parse {file_path}: {e}")
        return None

    if data:
        df = pd.DataFrame([data])
        df.insert(0, "Participant", participant_id)
        return df
    return None

participants = [d for d in os.listdir(base_dir)
                if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("MR")]

all_dfs = []

for participant in participants:
    participant_dfs = []
    for file in dkt_files:
        file_path = os.path.join(base_dir, participant, "stats", file)
        file_label = os.path.splitext(file)[0]
        df = parse_aparc_stats(file_path, file_label, participant)
        if df is not None:
            participant_dfs.append(df)
    if participant_dfs:
        combined = reduce(lambda left, right: pd.merge(left, right, on="Participant", how="outer"), participant_dfs)
        all_dfs.append(combined)

if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    output_path = os.path.join(base_dir, "/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_data/Freesurfer_data/aparc_DKT.csv")
    final_df.to_csv(output_path, index=False)
    print(f"✅ Script 2 complete. Data saved to:\n{output_path}")
else:
    print("⚠️ No data extracted.")
