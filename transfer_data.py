from pyubx2 import UBXReader
from pyubx2 import UBXMessage
import os

class Signal:
    def __init__(self, gnssId):
        self.gnssId = gnssId
        self.svId = None
        self.sigId = 0
        self.cno = None
        
frame = []
data = []

source_dir = 'raw_data/'
target_dir = 'transfered_data/'

for file in os.listdir(source_dir):
    if file.startswith(".git"):
        continue
    if file.endswith('.ubx'):
        if file[:-4] + ".txt" in os.listdir(target_dir):
            print(f"Skipping {file}...")
            continue
        with open(source_dir + file, 'rb') as stream:
            print(f"Processing {file}...")
            ubr = UBXReader(stream , protfilter = 2)
            data = []
            i = 0
            for (raw_data, parsed_data) in ubr:
                i += 1
                frame = []
                try:
                    parsed_data.identity
                except AttributeError:
                    continue
                if parsed_data.identity == "NAV-SIG":
                    data_items = str(parsed_data).strip('<>').split(', ')
                    for item in data_items:
                        try:
                            tmp, val = item.split('=')
                        except ValueError:
                            continue
                        try:
                            key, index = tmp.split('_')
                        except ValueError:
                            continue
                        match key:
                            case 'gnssId':
                                signal = Signal(val)
                            case 'svId':
                                signal.svId = val
                            case 'sigId':
                                signal.sigId = val
                            case 'cno':
                                signal.cno = val
                                frame.append(signal)
                if parsed_data.identity == "NAV-SAT":
                    data_items = str(parsed_data).strip('<>').split(', ')
                    signal = None
                    if len(data_items) == 1:
                        continue
                    for item in data_items:
                        try:
                            tmp, val = item.split('=')
                        except ValueError:
                            continue
                        try:
                            key, index = tmp.split('_')
                        except ValueError:
                            continue
                        match key:
                            case 'gnssId':
                                signal = Signal(val)
                            case 'svId':
                                signal.svId = val
                            case 'cno':
                                signal.cno = val
                                frame.append(signal)
                data.append(frame)
    with open(target_dir + file[:-4] + ".txt", "w") as f:
    # write all the gnssId, svId, sigId, cno to file
        for frame in data:
            for signal in frame:
                f.write(f"{signal.gnssId}, {signal.svId}, {signal.sigId}, {signal.cno}\n")