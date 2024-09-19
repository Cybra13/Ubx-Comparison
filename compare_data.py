import os
import pandas as pd
import xlsxwriter

source_dir = 'processed_data/'
target_dir = 'compared_data/'

def map_signal(system, signal): # mapping signals
    mapping = {
        "BeiDou": {
            0: "B1D1",
            7: "B2Ap"
        },
        "GLONASS": {
            0: "L1OF"
        },
        "GPS": {
            0: "L1C/A",
            7: "L5Q"
        },
        "Galileo": {
            0: "E1C",
            4: "E5AQ"
        },
        "QZSS": {
            0: "L1C/A",
            9: "L5Q"
        },
        "SBAS": {
            0: "L1C/A"
        }
    }
    return mapping.get(system, {}).get(signal, "Unknown")

# Get a list of all files in the source directory
files = os.listdir(source_dir)
files.sort()

# Create a dictionary to store data for each prefix
data_dict = {}

# Iterate through files to group them by prefix
for file in files:
    prefix = file.split('-')[0]
    if prefix not in data_dict:
        data_dict[prefix] = []
    data_dict[prefix].append(file)

# Iterate through each prefix and compare the files
for prefix, files in data_dict.items():
    if len(files) < 2:
        print(f"Skipping {prefix}...")
        continue
    # check if excel file already exists
    if prefix + "comparison.xlsx" in os.listdir(target_dir) or prefix + "_comparison.xlsx" in os.listdir(target_dir):
        print(f"Skipping {prefix}...")
        continue
    print(f"Comparing files with prefix {prefix}...")
    # Create a list to store comparison results
    group_files = []
    table = []
    # Iterate through files for the current prefix in groups
    group_size = len(files)
    for i in range(0, group_size):
        group_files.append({files[i].split("-")[1].split("_")[0]: pd.read_csv(source_dir + files[i], header=None)})
    for file in group_files:
        for key, value in file.items():
            for index, row in value.iterrows():
                check = False
                for data in table:
                    if data[0] == (row[0], row[1], row[2]):
                        # get index of the current file
                        index = group_files.index(file)
                        data[index * 2 + 1] = f"{row[3]}-{row[4]}"
                        data[index * 2 + 2] = row[5]
                        check = True
                        break
                if not check:
                    data = [(row[0], row[1], row[2])]
                    for i in range(group_size):
                        if i == group_files.index(file):
                            data.append(f"{row[3]}-{row[4]}")
                            data.append(row[5])
                        else:
                            data.append(-1)
                            data.append(-1)
                    table.append(data)
    # sort table by gnssId, svId, sigId
    table.sort(key=lambda x: (x[0][0], x[0][1], x[0][2]))

    # Create a new workbook and write comparison to excel
    with xlsxwriter.Workbook(target_dir + prefix + "_comparison.xlsx") as workbook:
        RED = workbook.add_format({'font_color': 'red'})
        GREEN = workbook.add_format({'font_color': 'green'})
        BLUE = workbook.add_format({'font_color': 'blue'})
        YELLOW = workbook.add_format({'font_color': 'yellow'})
        RED22 = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
        GREEN22 = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})
        BLUE22 = workbook.add_format({"bg_color": "#C9DAF8", "font_color": "#000080"})

        print("Creating excel file...")
        worksheet = workbook.add_worksheet()
        worksheet.write("A1", "gnssId")
        worksheet.write("B1", "svId")
        worksheet.write("C1", "sigId")
        for i in range(group_size):
            key = list(group_files[i].keys())[0]
            worksheet.write(0, 3 + 2 * i, f"MIN/MAX{key}")
            worksheet.write(0, 4 + 2 * i, f"MEAN{key}")
        for i, data in enumerate(table):
            for j, item in enumerate(data):
                if j == 0:
                    worksheet.write(i + 1, j, item[0])
                    worksheet.write(i + 1, j + 1, item[1])
                    worksheet.write(i + 1, j + 2, item[2])
                    worksheet.write(i + 1, j + 2, map_signal(item[0], item[2]))

                else:
                    if item == -1:
                        # worksheet.write(i + 1, j + 2, 0)
                        # worksheet.write(i + 1, j + 2, 0, RED22)
                        worksheet.write(i + 1, j + 2, "=NA()", RED22)
                    else:
                        worksheet.write(i + 1, j + 2, item)
                        # worksheet.write(i + 1, j + 2, item, GREEN22)
        if group_size == 2:
            worksheet.conditional_format(f'A2:G{len(table) + 1}', {'type': 'formula',
                                        'criteria': '=MAX(IFERROR($E2,0), IFERROR($G2,0)) = $E2', 
                                        'format':   RED22})
            worksheet.conditional_format(f'A2:G{len(table) + 1}', {'type': 'formula',
                                        'criteria': '=MAX(IFERROR($E2,0), IFERROR($G2,0)) = $G2', 
                                        'format':   GREEN22})
        if group_size == 3:
            worksheet.conditional_format(f'A2:I{len(table) + 1}', {'type': 'formula',
                                        'criteria': '=MAX(IFERROR($E2,0), IFERROR($G2,0), IFERROR($I2,0)) = $E2',
                                        'format':   RED22})
            worksheet.conditional_format(f'A2:I{len(table) + 1}', {'type': 'formula',
                                        'criteria': '==MAX(IFERROR($E2,0), IFERROR($G2,0), IFERROR($I2,0)) = $G2',
                                        'format':   GREEN22})
            worksheet.conditional_format(f'A2:I{len(table) + 1}', {'type': 'formula',
                                        'criteria': '==MAX(IFERROR($E2,0), IFERROR($G2,0), IFERROR($I2,0)) = $I2',
                                        'format':   BLUE22})
