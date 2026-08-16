# Sherlocked

A Python-based digital forensics investigation toolkit for evidence scanning, integrity hashing, file-signature analysis, browser artifact extraction, disk image inspection, and forensic reporting.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-pytest-informational)
![Lint](https://img.shields.io/badge/lint-ruff-informational)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)

---

## Overview

Sherlocked is a learning-oriented digital forensics framework built to understand how forensic tools such as Autopsy, The Sleuth Kit, or FTK Imager work internally, by implementing the core techniques from scratch rather than wrapping an existing suite.

Digital investigations rely on being able to answer a consistent set of questions about a piece of evidence: what is this file, has it been altered, does it match what it claims to be, when did things happen, and what did a user do on a system. Sherlocked implements a working pipeline around those questions — evidence scanning, metadata extraction, cryptographic hashing, magic-byte signature detection, extension/signature mismatch flagging, Chrome browser artifact extraction, raw disk image and ISO9660 inspection, and Markdown/JSON report generation — all driven from a case-based command-line workflow.

The project is deliberately built without high-level forensic libraries for its core logic (hashing is done with `hashlib`, disk structures are parsed manually with `struct`, MFT records are parsed byte-by-byte) so that the underlying filesystem and forensic concepts remain visible in the code rather than hidden behind an abstraction.

## Key Features

| Feature | Status |
|---|---|
| Case management (create / open / save, JSON-backed) | Implemented |
| Recursive evidence directory scanning | Implemented |
| File metadata extraction (name, size, MIME type, MAC timestamps) | Implemented |
| Cryptographic hashing (MD5, SHA-1, SHA-256) | Implemented |
| File signature / magic-byte detection | Implemented |
| Extension vs. signature mismatch detection | Implemented |
| Chrome browser history extraction | Implemented |
| Chrome download history extraction | Implemented |
| ISO9660 (`.iso`) offline image analysis | Implemented |
| Raw disk image analysis (`.img` / `.dd` / `.raw`) — boot signature, MBR/GPT detection, partition table parsing | Implemented |
| NTFS boot sector / BIOS Parameter Block parsing | Implemented |
| Timeline generation from file metadata | Implemented, not yet persisted into the case/report (see [Limitations](#limitations)) |
| Master File Table (MFT) record and attribute parsing | Implemented as a standalone module, not yet wired into the CLI |
| Markdown + JSON forensic report generation | Implemented |
| Rich-based CLI interface | Implemented |
| Deleted file recovery / file carving | Not implemented |
| Windows Registry / Event Log / Recycle Bin analysis | Not implemented |
| Firefox / Edge browser support | Not implemented |

## Architecture

Sherlocked is organized as an installable Python package (`src/sherlocked`) with narrowly-scoped modules. The CLI is the single entry point that coordinates three largely independent analysis paths: file-based evidence, Chrome browser artifacts, and disk image analysis.

```
                              User
                               │
                               ▼
                        sherlocked.cli.main
                               │
        ┌──────────────────────┼───────────────────────┐
        │                      │                        │
        ▼                      ▼                        ▼
 core.case_manager     core.evidence_analyzer     artifacts.chrome /
 (Case persistence)    (analysis pipeline)      filesystem.image_analysis
        │                      │                        │
        ▼                      ▼                        ▼
   core.case          scanner.evidence_scanner    ChromeArtifacts /
  (data model)         metadata.metadata_extractor  ISOAnalyzer /
                        hashing.hash_calculator      RawImageAnalyzer
                        recovery.signatures
                        hashing.mismatch_detector
                               │
                               ▼
                        case.metadata (list)
                               │
                  ┌────────────┴────────────┐
                  ▼                          ▼
     reporting.timeline_generator   reporting.report_generator
        (forensic timeline)          (Markdown + JSON report)
```

**Package responsibilities:**

- `core/` — the `Case` data model, case persistence (`CaseManager`), and the evidence analysis orchestrator (`EvidenceAnalyzer`).
- `scanner/` — recursive evidence directory traversal.
- `metadata/` — filesystem metadata extraction (`os.stat`, MIME type guessing).
- `hashing/` — streamed MD5/SHA-1/SHA-256 hashing and extension-mismatch detection.
- `recovery/` — magic-byte signature detection against a known-header table.
- `artifacts/` — browser artifact extraction (currently Chrome only).
- `filesystem/` — ISO9660 and raw disk image analysis, MBR/partition parsing, NTFS boot sector and MFT record parsing.
- `reporting/` — timeline construction and Markdown/JSON report generation.
- `cli/` — the interactive menu, orchestration between packages, and Rich-based table rendering.

## Investigation Workflow

```
Evidence directory
        │
        ▼
     Case (created/opened)
        │
        ▼
  EvidenceScanner.scan()          → list of file paths
        │
        ▼
  MetadataExtractor.extract()     → name, size, MIME type, MAC times
        │
        ▼
  HashCalculator.calculate_all()  → MD5 / SHA-1 / SHA-256
        │
        ▼
  SignatureAnalyzer.analyze()     → magic-byte based file type
        │
        ▼
  MismatchDetector.detect()       → extension/signature mismatch flag
        │
        ▼
  case.metadata (per-file record)
        │
        ├──▶ TimelineGenerator.build()   → chronological event list
        └──▶ ReportGenerator.generate()  → Markdown + JSON report
```

Browser artifact extraction (Chrome) and disk image analysis (ISO/raw) are exposed from the same CLI, but currently run as separate, standalone operations — their results are displayed in the terminal and are not merged into the active `Case` object or into the generated report.

## Project Structure

```
Sherlocked/
├── src/
│   └── sherlocked/
│       ├── cli/                  # Interactive menu and Rich table renderers
│       │   ├── main.py           # Application entry point
│       │   ├── ui.py
│       │   ├── table.py
│       │   ├── timeline_table.py
│       │   ├── browser_table.py
│       │   └── download_table.py
│       ├── core/                 # Case model, persistence, analysis orchestration
│       │   ├── case.py
│       │   ├── case_manager.py
│       │   ├── evidence_analyzer.py
│       │   └── logger.py
│       ├── scanner/              # Evidence directory scanning
│       │   └── evidence_scanner.py
│       ├── metadata/             # Filesystem metadata extraction
│       │   └── metadata_extractor.py
│       ├── hashing/              # Cryptographic hashing and mismatch detection
│       │   ├── hash_calculator.py
│       │   └── mismatch_detector.py
│       ├── recovery/             # File signature (magic-byte) analysis
│       │   └── signatures.py
│       ├── filesystem/           # ISO / raw disk image / MFT parsing
│       │   ├── image_analysis.py
│       │   └── mft_parser.py
│       ├── artifacts/            # Browser artifact extraction
│       │   └── chrome.py
│       ├── reporting/            # Timeline and report generation
│       │   ├── timeline_generator.py
│       │   └── report_generator.py
│       └── utils/                # Shared paths and timestamp conversion helpers
│           ├── paths.py
│           └── time_utils.py
├── tests/                        # Pytest test suite and evidence fixtures
│   └── fixtures/
├── .github/workflows/            # CI pipeline (lint + test)
├── pyproject.toml
├── requirements.txt
└── README.md
```

Runtime-generated directories (`cases/`, `evidence/`, `reports/`, `logs/`) are created automatically on first run and are excluded from version control.

## Installation

Requires Python 3.10 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/Sherlocked.git
cd Sherlocked

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install the project (registers the `sherlocked` command)
pip install -e .

# 6. Run
sherlocked
```

Alternatively, without installing the console script:

```bash
python -m sherlocked
```

## Usage

Launching `sherlocked` opens an interactive menu:

```
1. Create New Case
2. Open Existing Case
3. View Case Information   (analyzes evidence, displays inventory + timeline)
4. Analyze Evidence         (analyzes evidence, saves to case)
5. Extract Browser History
6. Extract Browser Downloads
7. Scan Disk Image
8. Generate Report
9. Exit
```

A typical investigation:

1. Create a case, providing a case ID, investigator name, description, and evidence path.
2. Analyze evidence to scan the evidence directory, compute hashes, and detect file signatures.
3. Review the generated evidence inventory and timeline in the terminal.
4. Optionally extract Chrome browsing history and download history.
5. Optionally scan a raw disk image placed at `evidence/windows_disk.dd`.
6. Generate a report, which is written to disk and opened automatically.

## Evidence Analysis

### Metadata Extraction

For every scanned file, `MetadataExtractor` collects the file name, extension, MIME type (guessed from the file extension), size in bytes, and creation/modification/access timestamps (`os.stat` MAC times).

### Hashing

`HashCalculator` streams each file in 4 KB chunks and computes MD5, SHA-1, and SHA-256 digests simultaneously. Cryptographic hashes give a fixed-size fingerprint of a file's contents — if the file changes by even a single bit, the hash changes completely, which is what makes hashing useful for verifying evidence integrity between the point of collection and the point of analysis.

### File Signatures

`SignatureAnalyzer` reads the first 32 bytes of each file and compares them against a table of known magic-byte headers (PNG, JPEG, GIF, PDF, ZIP/Office, RAR, 7-Zip, GZIP, SQLite, RIFF, MP3). File extensions are metadata supplied by whoever created or renamed the file and can be trivially changed; the actual file header is a much stronger indicator of true file type.

### Mismatch Detection

`MismatchDetector` compares a file's extension against the type reported by `SignatureAnalyzer`. If a file's extension implies one format (e.g. `.pdf`) but its magic bytes indicate another, it is flagged as suspicious — a common indicator of disguised or renamed files.

## Browser Forensics

`ChromeArtifacts` extracts data directly from Chrome's `History` SQLite database (locating it under the current user's default Chrome profile). It copies the database before reading it, since Chrome locks the file while running, then queries:

- Browsing history — URL, page title, and last visit time (`urls` table)
- Download history — target path, source URL, size, and start time (`downloads` table)

Chrome stores timestamps as microseconds since `1601-01-01 00:00:00 UTC` (the WebKit/Chrome epoch). `time_utils.chrome_time()` converts these raw integer values into timezone-aware Python `datetime` objects. Only Chrome is currently supported; Firefox and Edge are not implemented.

## Disk & Filesystem Analysis

`filesystem/image_analysis.py` implements two independent analyzers:

- **`ISOAnalyzer`** — walks an ISO9660 image using `pycdlib` without mounting it, enumerating files and directories, flagging executables, hidden files, and suspicious filenames (by keyword), and SHA-256 hashing every file it can read.
- **`RawImageAnalyzer`** — operates on raw `.img`/`.dd`/`.raw` disk images. It reads the first 512-byte boot sector, validates the `55 AA` boot signature, distinguishes MBR from GPT (by checking for the `EFI PART` header), parses the four-entry MBR partition table (boot flag, partition type, starting LBA, sector count), and, when the volume is NTFS, parses the BIOS Parameter Block (bytes per sector, sectors per cluster, cluster size, total sectors, MFT cluster number).

`filesystem/mft_parser.py` additionally implements `MFTParser`, which reads individual 1024-byte MFT records directly from a disk image, decodes record flags (in-use / directory), and parses the `$STANDARD_INFORMATION` (0x10) and `$FILE_NAME` (0x30) attributes, including their embedded FILETIME timestamps. This module is functionally complete but is **not yet invoked from the CLI** — it currently has no menu entry point.

## Timeline Analysis

`TimelineGenerator.build()` takes the metadata collected during evidence analysis and produces a chronological list of `Created` / `Modified` / `Accessed` events per file, sorted by timestamp. Reconstructing a timeline of file activity is one of the most common techniques in an investigation, since it lets an analyst correlate otherwise-unrelated files and events by when they occurred rather than where they were found.

The CLI currently displays this timeline in the terminal (menu option 3) but does not persist it back onto the active `Case` object, so it is not yet included in generated reports — see [Limitations](#limitations).

## Reporting

`ReportGenerator.generate()` builds a case report from the current `Case` object's case metadata, description, evidence hashes, per-file metadata, timeline, and any recovered files. It writes both a human-readable Markdown report and a machine-readable JSON report to `reports/<case_id>/investigation_report_<timestamp>.{md,json}`. From the CLI, the generated report is opened in the system's default web browser after generation.

## Testing

The test suite uses `pytest` and covers the core evidence-processing pipeline: case creation/serialization, evidence scanning, metadata extraction, hashing, signature detection, mismatch detection, timestamp conversion, and the end-to-end `EvidenceAnalyzer` flow. Test fixtures include scripts to generate a synthetic MBR disk image and a synthetic ISO9660 image for exercising the filesystem analyzers.

Run the tests:

```bash
pytest -v
```

With coverage (matching the CI configuration):

```bash
pytest --cov=sherlocked --cov-report=term-missing
```

Note: dedicated test files exist for disk image analysis, MFT parsing, and registry analysis, but are currently empty — these areas are implemented (or, in the case of registry parsing, not implemented) without automated test coverage yet.

## Code Quality / CI

A GitHub Actions workflow (`.github/workflows/python-tests.yml`) runs on every push and pull request to `main` and `develop`. It:

1. Sets up Python 3.11
2. Installs dependencies from `requirements.txt` and installs Sherlocked in editable mode
3. Runs static analysis with `ruff check src tests`
4. Runs the full test suite with `pytest --cov=sherlocked --cov-report=term-missing --cov-report=xml`
5. Uploads the coverage report as a build artifact

## Forensic Design Principles

### Evidence Integrity
MD5/SHA-1/SHA-256 hashes give every scanned file a fixed fingerprint, making it possible to detect whether a file has changed since it was first collected.

### File Identification
Magic-byte signature analysis checks a file's actual header instead of trusting its extension, and mismatch detection flags files where the two disagree.

### Artifact Correlation
Filesystem metadata, hashes, signatures, and (where available) browser artifacts are collected into a single case record, laying the groundwork for cross-referencing what happened, when, and with which files.

### Reproducibility
The analysis pipeline is deterministic and covered by automated tests for its core stages, so re-running the same evidence set through Sherlocked produces consistent results.

## Limitations

Sherlocked is an evolving learning project, not a production-grade forensic suite. Current, verified limitations:

- The evidence-analysis, Chrome artifact, and disk-image analysis workflows are **not integrated** — browser and disk-image results are printed to the console and are not stored on the `Case` object or included in generated reports.
- The forensic timeline built by `TimelineGenerator` is displayed in the CLI but is **not persisted** back onto the case, so generated reports currently show no timeline data.
- `MFTParser` is implemented but has **no CLI entry point** — MFT parsing cannot currently be triggered from the running application.
- No deleted-file recovery or file carving is implemented (`recovery/file_carver.py` is an empty stub).
- No Windows Registry, Event Log, or Recycle Bin analysis is implemented (empty stubs in `artifacts/`).
- Only Google Chrome is supported for browser forensics; Firefox and Edge are not implemented.
- Disk image support is limited to raw `.img`/`.dd`/`.raw` images and ISO9660; there is no support for forensic container formats such as E01/EWF.
- There is no formal evidence acquisition or chain-of-custody tracking — Sherlocked analyzes evidence that already exists on disk.
- The disk image scan (menu option 7) currently reads from a single hardcoded path (`evidence/windows_disk.dd`) rather than a user-supplied path.
- The application is CLI-only, with behavior for Chrome artifact extraction that assumes a Windows-style Chrome profile path.

## Roadmap

### Completed
- Case management and JSON persistence
- Evidence scanning, metadata extraction, hashing, signature analysis, mismatch detection
- Chrome history and download extraction
- ISO9660 and raw disk image analysis, MBR partition table parsing
- NTFS boot sector parsing
- Markdown/JSON report generation
- CI pipeline with linting and test coverage

### In Progress
- Master File Table (MFT) parsing (implemented, awaiting CLI integration)
- Integrating timeline output into the persisted case and reports

### Planned
- Deleted file recovery and signature-based file carving
- Windows Registry analysis
- Windows Event Log analysis
- Additional browser support (Firefox, Edge)
- Unified case model covering browser and disk-image findings
- Expanded automated test coverage for filesystem/image analysis

## Contributing

1. Fork the repository and create a feature branch.
2. Make your changes, keeping new modules consistent with the existing package structure under `src/sherlocked/`.
3. Run the test suite (`pytest -v`) and linter (`ruff check src tests`) before submitting.
4. Add or update tests for any new functionality.
5. Open a pull request describing the change and its motivation.

## Security / Responsible Use

Sherlocked is intended for educational use and for the analysis of evidence and systems you are explicitly authorized to examine. Do not use this toolkit against systems, accounts, or data without proper authorization. The maintainers assume no responsibility for misuse.

