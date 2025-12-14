import csv
from pyais import NMEAMessage
import json

# Input CSV
input_csv = "/Users/pruthviv/Desktop/Notes/SEMESTER 4/AIS/AIS_Klaipeda_From20250908_To20251008.csv"

# Output files
output_csv = "/Users/pruthviv/Desktop/Notes/SEMESTER 4/AIS/decoded_ais.csv"
output_json = "/Users/pruthviv/Desktop/Notes/SEMESTER 4/AIS/decoded_ais.json"

decoded_messages = []

# Step 1: Read CSV and decode messages
with open(input_csv, "r") as f:
    reader = csv.reader(f)
    header = next(reader)  # skip header
    for row in reader:
        line = row[0].strip()
        # Remove tagblock if present
        if line.startswith("\\") and "!AIVDM" in line:
            line = line.split("!AIVDM", 1)[1]
            line = "!AIVDM" + line
        try:
            msg = NMEAMessage.from_string(line)
            decoded = msg.decode()
            decoded_dict = decoded.asdict()
            # Convert any bytes to string
            for k, v in decoded_dict.items():
                if isinstance(v, bytes):
                    decoded_dict[k] = v.decode(errors='ignore')
            decoded_messages.append(decoded_dict)
        except Exception as e:
            print(f"Skipping invalid line: {line}\nError: {e}")

# Step 2: Collect all keys across all messages
all_keys = set()
for msg in decoded_messages:
    all_keys.update(msg.keys())
all_keys = sorted(all_keys)

# Step 3: Ensure all rows have all keys
for msg in decoded_messages:
    for key in all_keys:
        if key not in msg:
            msg[key] = None

# Step 4: Write CSV
with open(output_csv, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(decoded_messages)

# Step 5: Write JSON
with open(output_json, "w") as f:
    json.dump(decoded_messages, f, indent=2)

print(f"Decoded {len(decoded_messages)} messages.")
print(f"CSV saved to: {output_csv}")
print(f"JSON saved to: {output_json}")
