import os
import pandas as pd

source_dir = 'transfered_data/'
target_dir = 'processed_data/'

for file in os.listdir(source_dir):
    if file.endswith(".txt"):
        if file[:-4] + "_done.txt" in os.listdir(target_dir):
            print(f"Skipping {file}...")
            continue
        data = pd.read_csv(source_dir + file, header=None)
        # ignore 0 in cno (col 3)
        data = data[data[3] != 0]
        # group by gnssId, svId, sigId
        data = data.groupby([0, 1, 2]).agg(["min", "max", "mean"])
        data[3, "mean"] = data[3, "mean"].round(2)
        data.to_csv(target_dir + file[:-4] + "_done.txt", header=None)