import os
import pandas as pd
from pyais import decode
from pyais.exceptions import AISBaseException

# ---------------- CONFIG ----------------
INPUT_CSV = "../data/AIS_Klaipeda_From20250908_To20251008.csv"
OUTPUT_CSV = "../data/decoded_ais.csv"
NMEA_COLUMN = "nmea_message"

# AIS message types that contain SOG & COG
DYNAMIC_MESSAGE_TYPES = {1, 2, 3, 18, 19}
# ----------------------------------------


def extract_ais_sentence(raw):
    """
    Remove NMEA tag block and return pure AIS sentence.
    """
    if not isinstance(raw, str):
        return None

    idx = raw.find("!AIVDM")
    if idx == -1:
        idx = raw.find("!AIVDO")

    if idx == -1:
        return None

    return raw[idx:]


def decode_nmea_sentence(raw_sentence):
    """
    Decode AIS sentence after removing tag block.
    """
    try:
        clean_sentence = extract_ais_sentence(raw_sentence)
        if clean_sentence is None:
            return None

        msg = decode(clean_sentence)
        return msg.asdict()

    except AISBaseException:
        return None
    except Exception:
        return None


def main():
    os.makedirs("../data", exist_ok=True)

    df = pd.read_csv(INPUT_CSV)

    # -------- Counters --------
    total_messages = 0
    decode_failed = 0
    missing_coordinates = 0
    cleaned_messages = 0
    # --------------------------

    cleaned_rows = []
    message_type_counts = {}

    for _, row in df.iterrows():
        total_messages += 1

        raw_nmea = row.get(NMEA_COLUMN)
        decoded = decode_nmea_sentence(raw_nmea)

        if decoded is None:
            decode_failed += 1
            continue

        msg_type = decoded.get("msg_type")

        # Count all decoded message types
        if msg_type is not None:
            message_type_counts[msg_type] = message_type_counts.get(msg_type, 0) + 1

        lat = decoded.get("lat")
        lon = decoded.get("lon")

        if lat is None or lon is None:
            missing_coordinates += 1
            continue

        # Only keep dynamic messages with motion data
        if msg_type not in DYNAMIC_MESSAGE_TYPES:
            continue

        cleaned_messages += 1

        cleaned_rows.append({
            "mmsi": decoded.get("mmsi"),
            "latitude": lat,
            "longitude": lon,
            "speed_over_ground": decoded.get("sog"),
            "course_over_ground": decoded.get("cog"),
            "message_type": msg_type,
        })

    # Save cleaned data
    cleaned_df = pd.DataFrame(cleaned_rows)
    cleaned_df.to_csv(OUTPUT_CSV, index=False)

    # -------- Cleaning Report --------
    print("\n====== AIS CLEANING REPORT ======")
    print(f"Total messages read        : {total_messages}")
    print(f"Decoding failed            : {decode_failed}")
    print(f"Missing coordinates        : {missing_coordinates}")
    print(f"Cleaned (usable) messages  : {cleaned_messages}")
    print("--------------------------------")
    if total_messages > 0:
        print(f"Cleaning success rate      : {cleaned_messages / total_messages:.2%}")
    print(f"Output file saved to       : {OUTPUT_CSV}")
    print("================================\n")

    # -------- Message Type Counts --------
    print("AIS MESSAGE TYPE COUNTS\n")

    total_decoded = sum(message_type_counts.values())

    for msg_type in sorted(message_type_counts.keys()):
        print(f"type{msg_type:<3} {message_type_counts[msg_type]}")

    print(f"\nTotal decoded AIS messages: {total_decoded}\n")


if __name__ == "__main__":
    main()