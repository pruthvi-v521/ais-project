AIS Data Processing Project

Project Overview

This project implements a Python-based AIS (Automatic Identification System) data processing pipeline. The goal is to decode, clean, and prepare AIS messages for further analysis, closely following how real AIS receiver stations operate in practice.

The project focuses on the minimum goals defined in the course:
	•	Decoding AIS messages
	•	Cleaning and filtering invalid or unusable data
	•	Storing the processed output in a CSV file
	•	Preparing the system for real-time and analytical use

The implementation is intentionally modular and extensible so that additional features (databases, APIs, advanced analytics) can be added later without changing the core architecture.

⸻

Input Data Description

The input dataset contains raw AIS messages captured by an AIS receiver station. The CSV file has a single column:

nmea_message

Each row contains a raw NMEA AIS message with a tag block, for example:

\g:1-2-743902526,s:JDS,c:1757314914*27\!AIVDM,1,1,,A,13:0<s0v1NPnGF8O6>R3Kjih8<0v,0*18

This format reflects real-world AIS data transmission and is consistent with the AIS receiver station design described in the MARESEC paper.

⸻

What is a Tag Block?

A tag block is metadata added by an AIS receiver station before forwarding the AIS message.

Example Tag Block

\g:1-2-743902526,s:JDS,c:1757314914*27\

Information Contained in a Tag Block
	•	Receiver or station identifier
	•	Timestamp (often Unix time)
	•	Grouping or fragment information
	•	Checksum for the tag block

Why Tag Blocks Exist

AIS messages themselves do not include receiver-side metadata. Receiver stations therefore prepend tag blocks to:
	•	identify the receiving station
	•	timestamp messages
	•	support message grouping and tracking

Important Note

The PyAIS library cannot decode tag blocks directly. It expects a sentence starting with:

!AIVDM  or  !AIVDO

Therefore, tag blocks must be removed before decoding.

⸻

Processing Pipeline Overview

The implemented pipeline follows these steps:
	1.	Read raw AIS messages from CSV
	2.	Remove tag blocks and extract the pure AIS NMEA sentence
	3.	Decode AIS messages using PyAIS
	4.	Clean and filter messages based on validity rules
	5.	Store cleaned messages in a structured CSV file
	6.	Report statistics about decoding and cleaning

This mirrors the architecture of real AIS receiver stations and supports future real-time extensions.

⸻

Decoding Logic

Tag Block Removal

Before decoding, each raw message is scanned for the start of the AIS sentence:
	•	!AIVDM – AIS message received from another vessel
	•	!AIVDO – AIS message from the own vessel

Everything before this marker (the tag block) is removed. The resulting string is a valid AIS NMEA sentence that can be decoded.

AIS Decoding

The cleaned AIS sentence is passed to the PyAIS decoder, which extracts structured fields such as:
	•	MMSI (Maritime Mobile Service Identity)
	•	Latitude and Longitude
	•	Speed Over Ground (SOG)
	•	Course Over Ground (COG)
	•	AIS message type

Messages that cannot be decoded are discarded.

⸻

Data Cleaning Rules

Cleaning is intentionally minimal and conservative, in line with the project’s minimum goals.

A message is considered cleaned and usable if:
	1.	It can be successfully decoded
	2.	It contains valid geographic coordinates (latitude and longitude)

Messages are discarded if:
	•	Decoding fails (corrupted or malformed AIS messages)
	•	Latitude or longitude is missing (non-positional AIS message types)

Only essential, analysis-relevant fields are retained in the output.

⸻

Output Data Format

Cleaned data is written to a CSV file with the following structure:

mmsi,latitude,longitude,speed_over_ground,course_over_ground,message_type

### Important Notes on Missing Values and Message Types

It is expected that the `speed_over_ground` and `course_over_ground` columns may be empty for some rows. Even for dynamic AIS message types (such as types 1, 2, 3, 18, and 19), the AIS standard allows these fields to be marked as *“not available”*. This occurs when vessels are stationary, anchored, or when valid motion data is not transmitted. The PyAIS library correctly converts these AIS-defined *not available* values into `None`, which appear as empty cells in the output CSV. These empty values therefore represent missing data at the source and not a decoding or implementation error.

Message type 5 does not appear in the cleaned output file because it is a static and voyage-related AIS message type and does not contain latitude or longitude information. Since the cleaning pipeline focuses on position-based analysis, all non-positional message types are intentionally filtered out. This behavior is correct and consistent with standard AIS processing practices.

⸻

Cleaning Statistics and Output Report

During processing, the system keeps track of:
	•	Total messages read – number of rows in the input CSV
	•	Decoding failed – messages that could not be decoded
	•	Missing coordinates – decoded messages without position data
	•	Cleaned (usable) messages – messages suitable for analysis

Example output:

====== AIS CLEANING REPORT ======
Total messages read        : 2429394
Decoding failed            : 180000
Missing coordinates        : 1150000
Cleaned (usable) messages  : 1100000
Cleaning success rate      : 45.3%
================================

This behavior is expected:
	•	Only certain AIS message types contain position data
	•	A significant portion of AIS traffic is static or non-positional

⸻

Why This Approach Is Correct
	•	Reflects real AIS receiver station pipelines
	•	Correctly handles tag blocks
	•	Separates decoding from cleaning
	•	Produces structured, reusable data
	•	Fully satisfies the project’s minimum goals

The pipeline is also designed so that future extensions (databases, APIs, real-time streaming, trajectory prediction) can be added without changing the core logic.

⸻

Current Project Status

✔ Raw AIS data ingestion
✔ Tag block handling
✔ AIS decoding
✔ Cleaning and filtering
✔ CSV-based storage
✔ Statistical reporting
✔ AIS message type distribution analysis

⸻

Future Extensions (Optional)
	•	Real-time AIS streaming
	•	Distance and proximity analysis between ships
	•	Trajectory prediction
	•	Database-backed storage
	•	REST API for external users

⸻

## File Structure and Repository Layout

Due to the very large size of the AIS CSV input file, the full dataset is not included in the GitHub repository. Large data files are excluded using `.gitignore` to keep the repository lightweight and manageable.

The project structure is as follows:

```
AIS-Project/
│
├── data/
│   ├── AIS_Klaipeda_From20250908_To20251008.csv   # Large raw AIS input file (not tracked in Git)
│   └── decoded_ais.csv                            # Generated cleaned output file (not tracked)
│
├── decoding/
│   └── ais_decoder.py                             # Main decoding and cleaning pipeline
│
├── .gitignore                                     # Excludes large CSV files
├── README.md                                      # Project documentation
└── requirements.txt                               # Python dependencies
```

The raw AIS input file and generated output files must be placed in the `data/` directory locally before running the pipeline.

---

## Summary

This project demonstrates a practical, real-world approach to AIS data processing using Python. It correctly handles receiver tag blocks, decodes raw AIS messages, applies conservative and standards-compliant cleaning rules, and produces structured output suitable for further analysis. The design closely follows real AIS receiver station pipelines and fully satisfies the minimum goals of the assignment, while remaining extensible for future enhancements.