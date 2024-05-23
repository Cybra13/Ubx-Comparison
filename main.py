import os
os.makedirs("transfered_data", exist_ok=True)
os.makedirs("processed_data", exist_ok=True)
os.makedirs("compared_data", exist_ok=True)

exec(open("transfer_data.py").read())
exec(open("process_data.py").read())
exec(open("compare_data.py").read())
