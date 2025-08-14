from pyubx2 import UBXReader
from pyubx2 import UBXMessage
import os

def map_signal(system, signal): # mapping signals
    mapping = {
        "BeiDou": {
            0: "B1I",
            1: "B1Q",
            2: "B1C",
            3: "B2I",
            4: "B2Q",
            5: "B2aI",
            6: "B2aQ",
            7: "B2bI",
            8: "B2bQ",
            9: "B3I",
            10: "B3Q"
        },
        "GLONASS": {
            0: "L1OF",
            1: "L1OC",
            2: "L2OF",
            3: "L2OC",
            4: "L3OF",
            5: "L3OC"
        },
        "GPS": {
            0: "L1C/A",
            1: "L1C",
            2: "L2C",
            3: "L2P",
            4: "L5I",
            5: "L5Q",
            6: "L5X"
        },
        "Galileo": {
            0: "E1B",
            1: "E1C",
            2: "E5aI",
            3: "E5aQ",
            4: "E5bI",
            5: "E5bQ",
            6: "E5I",
            7: "E5Q",
            8: "E6B",
            9: "E6C"
        },
        "QZSS": {
            0: "L1C/A",
            1: "L1C",
            2: "L2C",
            3: "L5I",
            4: "L5Q",
            5: "L5X",
            6: "L6D",
            7: "L6E"
        },
        "SBAS": {
            0: "L1C/A",
            1: "L5I",
            2: "L5Q"
        }
    }
    return mapping.get(system, {}).get(signal, "Unknown")

class Signal:
    def __init__(self, gnssId):
        self.gnssId = gnssId
        self.svId = None
        self.sigId = 0
        self.cno = None
        
frame = []
data = []
GNSSIDs = ["BeiDou", "GLONASS", "GPS", "Galileo", "QZSS", "SBAS"]


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
            sigsat = 0
            print(f"Processing {file}...")
            ubr = UBXReader(stream , protfilter = 2)
            data = []
            for raw_data, parsed_data in ubr:
                print(parsed_data)
                print(parsed_data.identity)
                frame = []
                try:
                    parsed_data.identity
                except AttributeError:
                    continue
                if parsed_data.identity == "NAV-SIG":
                    sigsat = 1
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
                if parsed_data.identity == "NAV-SAT" and sigsat <= 0:
                    sigsat = -1
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
                if signal.gnssId not in GNSSIDs:
                    continue
                signal_name = map_signal(signal.gnssId, int(signal.sigId))
                f.write(f"{signal.gnssId}, {signal.svId}, {signal_name}, {signal.cno}\n")
