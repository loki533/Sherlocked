# 🔍 Sherlocked
### A Digital Forensics Investigation Toolkit built in Python

> **Sherlocked** is an educational and extensible digital forensics framework designed to demonstrate how modern forensic tools work internally. Rather than relying on existing forensic suites, the project focuses on implementing core forensic techniques from scratch to understand evidence acquisition, filesystem parsing, artifact extraction, and forensic reporting.

---

## 📌 Project Overview

Sherlocked aims to simulate the workflow of professional forensic tools such as:

- Autopsy
- The Sleuth Kit (TSK)
- FTK Imager
- Magnet AXIOM
- X-Ways Forensics

The objective is to understand **how forensic tools actually work**, including:

- Evidence collection
- File system parsing
- Metadata extraction
- Browser artifact analysis
- Disk image analysis
- Timeline generation
- NTFS internals
- Deleted file recovery (Upcoming)

---

# 🏗 Current Architecture

```
                    +--------------------+
                    |    Evidence Input  |
                    +--------------------+
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
          ▼                   ▼                    ▼
     File Scanner       Disk Image         Browser Artifacts
                           Analysis

          │
          ▼

    Metadata Extraction
          │
          ▼

      Hash Analysis
          │
          ▼

  Signature Verification
          │
          ▼

 Timeline Generation
          │
          ▼

  Report Generation
```

---

# 📂 Project Structure

```
Sherlocked/

├── core/
│   ├── case.py
│   ├── case_manager.py
│   ├── evidence_analyzer.py
│   ├── logger.py
│   ├── table.py
│   ├── timeline_table.py
│   └── ui.py
│
├── modules/
│   ├── scanner.py
│   ├── metadata.py
│   ├── hashing.py
│   ├── mismatch_detector.py
│   ├── signatures.py
│   ├── browser.py
│   ├── timeline.py
│   ├── recycle_bin.py
│   ├── image_analysis.py
│   └── report.py
│
├── reports/
├── evidence/
├── logs/
├── tests/
│
└── main.py
```

---

# ✅ Features Implemented

## 📁 Evidence Scanner

- Recursive directory scanning
- Evidence inventory generation
- File type identification
- Hidden file detection

---

## 📄 Metadata Extraction

Extracts:

- File Name
- Extension
- Size
- Creation Time
- Modification Time
- Access Time
- Owner Information (where available)

---

## 🔐 Hash Generation

Supports:

- MD5
- SHA1
- SHA256

Used for integrity verification and evidence authentication.

---

## 📑 File Signature Analysis

Detects:

- Magic numbers
- Header signatures
- File extension mismatches

Useful for identifying disguised or renamed files.

---

## 🗑 Deleted File Analysis

Current support:

- Windows Recycle Bin parsing

Future:

- NTFS deleted record recovery

---

## 🌐 Browser Artifact Analysis

Current support:

- Google Chrome

Extracts:

- Browsing History
- Downloads
- Cookies (planned)
- Login Data (planned)

---

## ⏱ Timeline Generation

Generates chronological forensic timelines using:

- File creation timestamps
- Last modified timestamps
- Last accessed timestamps

---

## 📊 Report Generation

Automatically generates structured forensic reports containing:

- Evidence summary
- Metadata
- Hash values
- Timeline
- Browser artifacts
- File statistics

---

# 💿 ISO Image Analysis (Implemented)

The ISO analyzer performs **offline analysis** of ISO9660 images without mounting them.

### Features

- Enumerates directories
- Enumerates files
- SHA256 hashing of every file
- Detects executable files
- Detects hidden files
- Detects suspicious filenames
- Lists largest files
- Generates structured forensic summaries

Example:

```
Windows.iso

Files: 423

Directories: 56

Executables:
    setup.exe
    bootmgr.exe

Largest Files:
    install.wim
    boot.wim
```

---

# 💽 Raw Disk Image Analysis (Implemented)

Supports:

- RAW (.img)
- DD (.dd)
- RAW (.raw)

Current capabilities:

### Boot Sector Validation

- Valid boot signature detection (55 AA)

### Partition Scheme Detection

- MBR
- GPT

### Filesystem Identification

Detects:

- NTFS
- FAT32
- exFAT

### Partition Table Analysis

Extracts:

- Bootable flag
- Partition type
- Starting LBA
- Number of sectors
- Partition size

Example:

```
Partition 1

Type:
NTFS

Bootable:
Yes

Start LBA:
2048

Size:
118.4 GB
```

---

# 🧩 NTFS Boot Sector Parsing (Implemented)

Sherlocked now parses the NTFS Boot Sector to extract low-level filesystem metadata.

Extracted fields include:

- NTFS Signature
- Bytes Per Sector
- Sectors Per Cluster
- Cluster Size
- Total Sectors
- MFT Cluster Number
- MFT Mirror Cluster
- Volume Serial Number
- Absolute MFT Offset

This forms the foundation for Master File Table (MFT) parsing and deleted file recovery.

---

# 🚧 Features Under Development

## Master File Table (MFT) Parser

Will extract:

- File records
- Directory records
- Deleted entries
- File attributes
- Resident / Non-resident data

---

## Deleted File Recovery

Planned support:

- NTFS deleted record recovery
- File carving
- Signature-based recovery
- MFT-based recovery

Supported file types:

- JPG
- PNG
- PDF
- DOCX
- ZIP
- MP4
- EXE

---

## Windows Registry Analysis

Planned extraction:

- Installed software
- USB device history
- Autorun entries
- User accounts
- Network profiles
- Timezone
- System information

---

## Windows Event Log Analysis

Planned support:

Security.evtx

System.evtx

Application.evtx

Interesting events:

- Successful logins
- Failed logins
- Account lockouts
- Service installations
- USB insertions
- System shutdowns

---

## Browser Support Expansion

Planned:

- Microsoft Edge
- Mozilla Firefox

---

# 🛠 Technologies Used

- Python 3.x
- pathlib
- hashlib
- pycdlib
- sqlite3
- Rich
- struct
- io

Upcoming:

- python-registry
- python-evtx
- pyfsntfs

---

# 🚀 Running the Project

Clone the repository

```bash
git clone https://github.com/<your-username>/Sherlocked.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python main.py
```

---

# 📈 Development Roadmap

- [x] Evidence Scanner
- [x] Metadata Extraction
- [x] Hash Generation
- [x] Signature Verification
- [x] Timeline Generation
- [x] Browser Artifact Analysis
- [x] Report Generation
- [x] ISO Image Analysis
- [x] Raw Disk Image Analysis
- [x] Partition Table Analysis
- [x] NTFS Boot Sector Parsing
- [ ] Master File Table Parser
- [ ] Deleted File Recovery
- [ ] Registry Analysis
- [ ] Event Log Analysis
- [ ] Memory Forensics
- [ ] YARA Rule Scanning
- [ ] Malware Artifact Detection
- [ ] GUI Dashboard

---

# 🎯 Educational Objective

Sherlocked is being developed as a learning-oriented digital forensics framework to understand the internal workings of forensic software rather than relying solely on existing tools. The project emphasizes filesystem structures, forensic artifact extraction, evidence integrity, and investigative workflows while maintaining an extensible architecture for future forensic capabilities.

---

# 📜 License

This project is intended for educational and research purposes.

```

## A suggestion

At this stage, your project has evolved well beyond a simple Python utility. I also recommend adding the following to the repository:

- **`docs/architecture.md`** – a detailed explanation of the framework architecture.
- **`docs/forensics-flow.md`** – diagrams showing evidence flow (Disk → MBR → Partition → NTFS → MFT → Deleted Files).
- **`docs/screenshots/`** – screenshots of the terminal output and generated reports.
- **GitHub Actions** – to automatically run tests on every commit.

These additions will make the repository look much more like a polished open-source forensic framework and stand out to recruiters and collaborators.