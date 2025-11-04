# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bibliometric data processing tools for integrating Scopus and Web of Science (WOS) literature data. The toolkit converts Scopus CSV format to standard WOS plain text format and intelligently merges/deduplicates records from both databases.

**Primary Use Case**: Enable researchers to combine Scopus and WOS data for comprehensive bibliometric analysis using tools like CiteSpace, VOSviewer, and Bibliometrix.

## Core Architecture

### Two-Step Processing Pipeline

```
Input Files:
├── wos.txt          (WOS native format)
└── scopus.csv       (Scopus export with all fields)
         ↓
    [Step 1: Format Conversion]
    scopus_to_wos_converter.py
         ↓
    scopus_converted_to_wos.txt
         ↓
    [Step 2: Merge & Deduplicate]
    merge_deduplicate.py
         ↓
Output:
└── merged_deduplicated.txt  (Final merged dataset)
```

### Key Components

**1. scopus_to_wos_converter.py** - Format Converter
- **ScopusToWosConverter**: Main converter class
  - Converts 44 Scopus CSV fields to 30+ WOS fields
  - Handles author name abbreviations (removes Scopus IDs, normalizes initials)
  - Intelligent institution parsing and abbreviation
  - Reference citation parsing with journal abbreviation
  - C3 field generation (extracts top-level institutions for institutional analysis)

- **Critical Methods**:
  - `convert_authors()`: Processes author format from "Lastname, M.V." to "Lastname, MV"
  - `parse_affiliations()`: Converts Scopus author-grouped affiliations to WOS institution-grouped format
  - `reorder_institution_parts()`: Reorders institution hierarchy (primary institution first, then department)
  - `extract_primary_institutions()`: Extracts top-level institutions for C3 field
  - `parse_reference()`: Parses Scopus reference format and maps journals to abbreviations

- **Data Mappings**:
  - `JOURNAL_ABBREV`: 50+ common journal name to abbreviation mappings
  - `MONTH_ABBREV`: Month name/number to 3-letter abbreviation

**2. merge_deduplicate.py** - Merge & Deduplication Tool
- **WOSRecordParser**: Parses WOS plain text format into structured records
  - Handles multi-line field continuations (3-space indent)
  - Preserves field order and formatting

- **RecordMatcher**: Identifies duplicate records between WOS and Scopus
  - Primary strategy: DOI matching (100% accuracy)
  - Fallback strategy: Normalized title + year + first author matching

- **RecordMerger**: Merges WOS and Scopus records
  - WOS records take priority (more complete data)
  - Scopus supplements missing WOS fields
  - Citation count: takes maximum of both sources

- **MergeDeduplicateTool**: Orchestrates the merge workflow
  - Identifies WOS-Scopus duplicates
  - Merges duplicate pairs (WOS-priority)
  - Preserves Scopus-unique records

### Critical Format Requirements

**UTF-8 BOM Encoding**: Both output files MUST use UTF-8 with BOM (`utf-8-sig`) for VOSviewer compatibility.

**WOS File Structure**:
```
FN Clarivate Analytics Web of Science
VR 1.0

PT J
AU Author1, AB
   Author2, CD
TI Title text here
SO JOURNAL NAME
...
ER

PT J
...
ER

EF
```

**Field Continuation Format**: Multi-line fields use 3-space indentation for continuation lines.

## Common Development Commands

### Running the Full Pipeline
```bash
# One-command execution (recommended)
./run_all.sh

# Requires: wos.txt and scopus.csv in project root
# Produces: scopus_converted_to_wos.txt, merged_deduplicated.txt, merged_deduplicated_report.txt
```

### Individual Script Execution
```bash
# Step 1: Convert Scopus to WOS format only
python3 scopus_to_wos_converter.py
# or with custom paths:
python3 scopus_to_wos_converter.py input.csv output.txt

# Step 2: Merge and deduplicate
python3 merge_deduplicate.py
# or with custom paths:
python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt
```

### Testing
No formal test suite exists. Manual verification approach:
1. Compare conversion output with real WOS data samples
2. Verify field-by-field accuracy (see 转换质量对比报告.md)
3. Import into VOSviewer/CiteSpace to ensure format compatibility
4. Check deduplication report for accuracy

## Important Implementation Details

### C3 Field (Institution Analysis)
The C3 field is crucial for institutional collaboration analysis. The extraction logic:
1. Identifies primary institutions using keywords (University, Hospital, Institute, Foundation, etc.)
2. Filters out secondary units (Department, Division, Laboratory of X)
3. Standardizes institution names (e.g., "Università degli Studi di Pavia" → "University of Pavia")
4. Deduplicates and formats as semicolon-separated list

**Location**: `scopus_to_wos_converter.py:595-710` (`extract_primary_institutions()` and `clean_institution_name()`)

### Reference Citation Format Challenges
Scopus reference format differs significantly from WOS:
- Scopus: "Author, FirstName, Title, Journal, Volume, Issue, pp. Pages, (Year)"
- WOS: "Author Initials, Year, JOURNAL ABBREV, VVolume, PPage"

The parser uses heuristics to extract fields. **Known limitation**: Author initials may be incomplete, volume/page numbers may be imprecise. This affects citation network analysis accuracy.

**Location**: `scopus_to_wos_converter.py:225-332` (`parse_reference()` and `format_reference_wos()`)

### Institution Address Reordering
WOS format expects: `[Authors] Primary Institution, Department, City, Country.`
Scopus provides: `Author, Firstname, Department, University, City, Country`

The `reorder_institution_parts()` method intelligently reorders components by:
1. Classifying parts as primary/secondary/geographic
2. Detecting institution keywords in each segment
3. Reconstructing in WOS order

**Location**: `scopus_to_wos_converter.py:445-530`

### Deduplication Strategy
Merge logic prioritizes WOS records because:
- WOS data is more standardized for bibliometric analysis
- WOS citation networks are more accurate
- Many analysis tools are optimized for WOS format

The matcher uses a two-tier approach:
1. DOI matching (when available) - 100% reliable
2. Fuzzy title matching + exact year + first author - 95%+ reliable

**Location**: `merge_deduplicate.py:100-170` (`RecordMatcher`)

## Known Limitations

1. **Author Full Names (AF field)**: Scopus sometimes provides only abbreviated names, not full names
2. **Reference Citations (CR field)**: Author initials may be missing, volume/page numbers may be imprecise due to format differences
3. **Institution Address Format (C1 field)**: Scopus groups by author, WOS groups by institution - semantic equivalent but structurally different

These limitations are documented in 转换质量对比报告.md with detailed comparisons to real WOS data.

## File Encoding Requirements

All input/output files:
- **Encoding**: UTF-8 with BOM (`utf-8-sig` in Python)
- **Line endings**: Unix-style (`\n`)
- **CSV reading**: Must handle `utf-8-sig` to strip BOM automatically

## Extending the Toolkit

### Adding New Journal Abbreviations
Edit `scopus_to_wos_converter.py:24-84`, add to `JOURNAL_ABBREV` dictionary:
```python
JOURNAL_ABBREV = {
    "Your Journal Name": "YOUR ABBREV",
    # existing entries...
}
```

### Customizing Institution Abbreviations
Edit `scopus_to_wos_converter.py:541-593`, modify `abbrev_map` in `abbreviate_institution()`:
```python
abbrev_map = {
    'Your Institution': 'Your Abbrev',
    # existing mappings...
}
```

### Adding New Institution Keywords
For C3 field extraction, edit `scopus_to_wos_converter.py:612-622`, update `primary_keywords` list in `extract_primary_institutions()`.

## Python Version & Dependencies

- **Python**: 3.6+ required
- **Dependencies**: None (uses only standard library: csv, re, datetime, typing, textwrap, collections)
- **No virtual environment needed**
