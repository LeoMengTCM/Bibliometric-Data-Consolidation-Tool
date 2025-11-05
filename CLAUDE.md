# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bibliometric data processing tools for integrating Scopus and Web of Science (WOS) literature data. The toolkit converts Scopus CSV format to standard WOS plain text format, intelligently merges/deduplicates records from both databases, filters by language, and generates comprehensive statistical reports.

**Primary Use Case**: Enable researchers to combine Scopus and WOS data for comprehensive bibliometric analysis using tools like CiteSpace, VOSviewer, and Bibliometrix.

**Version**: v2.1 (2025-11-04)

**Key Features**:
- Format conversion (Scopus CSV → WOS plain text)
- Intelligent merge and deduplication
- Language filtering (e.g., English-only)
- Statistical analysis (country, institution, author distribution)
- Automated workflow with detailed reporting for paper writing

## Core Architecture

### Complete Processing Pipeline

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
    merged_deduplicated.txt
         ↓
    [Step 3: Language Filter (Optional)]
    filter_language.py
         ↓
    english_only.txt
         ↓
    [Step 4: Statistical Analysis (Optional)]
    analyze_records.py
         ↓
Output:
├── merged_deduplicated.txt       (Full merged dataset)
├── english_only.txt               (Language-filtered dataset)
└── *_analysis_report.txt          (Statistical reports)
```

**Automated Workflow** (v2.1+):
```
run_complete_workflow.py --data-dir "/path/to/data"
  → Executes all steps automatically
  → Generates comprehensive report with Article/Review statistics
  → Provides paper writing reference (Methods section)
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

**3. filter_language.py** - Language Filter Tool (v2.1+)
- **LanguageFilter**: Filters records by language
  - Parses WOS format and identifies LA (language) field
  - Filters records matching target language (English, Chinese, German, etc.)
  - Generates language distribution statistics
  - Preserves WOS format and UTF-8 BOM encoding

- **Key Methods**:
  - `parse_wos_file()`: Parses WOS file, preserves raw text
  - `filter_records()`: Filters by target language
  - `write_filtered_file()`: Writes filtered WOS file
  - `generate_report()`: Creates filtering report

**Location**: `filter_language.py`

**4. analyze_records.py** - Statistical Analysis Tool (v2.1+)
- **RecordAnalyzer**: Analyzes literature data distribution
  - Country/region distribution (46 country name standardization rules)
  - High-productivity institutions (Top 20)
  - Year distribution trends
  - International collaboration network
  - High-productivity authors (first authors)

- **Configuration System**:
  - `config/country_mapping.json`: Country name standardization
  - `config/biomedical_institutions.json`: Biomedical institutions

**Location**: `analyze_records.py`

**5. run_complete_workflow.py** - Automated Workflow (v2.1+) ⭐
- **CompleteWorkflow**: End-to-end automated processing
  - Executes all processing steps sequentially
  - Tracks Article/Review/Other counts at each stage
  - Generates comprehensive workflow report
  - Provides paper Methods section writing reference

- **Workflow Steps**:
  1. `check_files()`: Verify wos.txt and scopus.csv exist
  2. `step1_analyze_wos_original()`: Count WOS Article/Review
  3. `step2_convert_scopus()`: Convert Scopus, count Article/Review
  4. `step3_merge_and_deduplicate()`: Merge, calculate duplicates
  5. `step4_filter_language()`: Filter by language, count results
  6. `step5_generate_report()`: Generate comprehensive report

- **Key Features**:
  - Document type statistics at each stage (Article/Review/Other)
  - Language distribution analysis
  - Duplication rate calculation
  - Paper writing reference text generation

- **Output** (`workflow_complete_report.txt`):
  - WOS original statistics (total, Article, Review, other)
  - Scopus original statistics (total, Article, Review, other)
  - Merge results (duplicates removed, final counts)
  - Language distribution
  - English filtering results (final Article/Review counts)
  - Data flow summary
  - Paper Methods section reference text

**Location**: `run_complete_workflow.py`

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

### Running the Complete Workflow (Recommended, v2.1+)
```bash
# Automated workflow with comprehensive reporting
python3 run_complete_workflow.py --data-dir "/path/to/data"

# Example:
python3 run_complete_workflow.py --data-dir "/Users/xxx/文献计量学/Nano_NSCLC_Immune"

# Requires: wos.txt and scopus.csv in data directory
# Produces:
#   - scopus_converted_to_wos.txt (intermediate)
#   - merged_deduplicated.txt (full merged dataset)
#   - english_only.txt (English-only, recommended for analysis)
#   - workflow_complete_report.txt (comprehensive statistics)

# Optional parameters:
python3 run_complete_workflow.py \
  --data-dir "/path/to/data" \
  --language Chinese \
  --log-level WARNING
```

### Running the Traditional Pipeline
```bash
# One-command execution (traditional method)
./run_all.sh

# Requires: wos.txt and scopus.csv in project root
# Produces: scopus_converted_to_wos.txt, merged_deduplicated.txt
```

### Individual Script Execution
```bash
# Step 1: Convert Scopus to WOS format
python3 scopus_to_wos_converter.py input.csv output.txt

# Step 2: Merge and deduplicate
python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt

# Step 3: Filter by language (v2.1+)
python3 filter_language.py merged.txt english_only.txt --language English

# Step 4: Statistical analysis (v2.1+)
python3 analyze_records.py merged.txt --config-dir config
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

### Adding New Journal Abbreviations (v2.1+)
**Recommended**: Edit `config/journal_abbrev.json`:
```json
{
  "Your Journal Name": "YOUR ABBREV",
  "Another Journal": "ANOTHER ABBREV"
}
```

**Legacy method**: Edit `scopus_to_wos_converter.py:24-84`, add to `JOURNAL_ABBREV` dictionary.

### Customizing Institution Abbreviations (v2.1+)
Edit `config/institution_config.json`:
```json
{
  "abbreviations": {
    "Your Word": "Your Abbrev",
    "Department": "Dept"
  }
}
```

### Adding Independent Colleges/Schools (v2.1+)
Edit `config/institution_config.json`:
```json
{
  "independent_colleges": [
    "Imperial College London",
    "Your College Name"
  ],
  "independent_schools": [
    "Harvard Medical School",
    "Your School Name"
  ]
}
```

### Adding Country Name Mappings (v2.1+)
Edit `config/country_mapping.json`:
```json
{
  "country_mapping": {
    "USA": "United States",
    "UK": "United Kingdom",
    "Your Variant": "Standard Name"
  }
}
```

### Adding Biomedical Institutions (v2.1+)
Edit `config/biomedical_institutions.json`:
```json
{
  "independent_colleges": ["Your Medical College"],
  "medical_institution_keywords": ["Your Keyword"]
}
```

## Python Version & Dependencies

- **Python**: 3.6+ required
- **Dependencies**: None (uses only standard library: csv, re, datetime, typing, textwrap, collections, json, subprocess, argparse, logging)
- **No virtual environment needed**

## v2.1 New Features Summary

### 1. Complete Workflow Script (`run_complete_workflow.py`)
**Purpose**: One-command execution of entire processing pipeline with detailed reporting.

**Usage**:
```bash
python3 run_complete_workflow.py --data-dir "/path/to/data"
```

**Key Outputs**:
- Comprehensive statistics report (Article/Review counts at each stage)
- Paper Methods section writing reference
- All intermediate and final files

**Use Case**: Researcher has wos.txt and scopus.csv, wants to:
1. Convert Scopus to WOS format
2. Merge and deduplicate
3. Filter English-only literature
4. Get detailed statistics for paper writing

### 2. Language Filter (`filter_language.py`)
**Purpose**: Filter literature by language (e.g., English-only for international journal submission).

**Usage**:
```bash
python3 filter_language.py input.txt output.txt --language English
```

**Features**:
- Supports all WOS language values
- Generates language distribution report
- Preserves WOS format

### 3. Statistical Analysis (`analyze_records.py`)
**Purpose**: Analyze country, institution, author distribution.

**Features**:
- Country name standardization (46 mapping rules)
- High-productivity institution ranking
- International collaboration analysis
- Year distribution trends

### 4. Configuration System (`config/`)
**Purpose**: Externalize configuration for easy customization.

**Files**:
- `country_mapping.json`: Country name standardization
- `biomedical_institutions.json`: Biomedical institution recognition
- `institution_config.json`: Institution abbreviations and keywords
- `journal_abbrev.json`: Journal name abbreviations

**Advantage**: Users can customize without modifying source code.

### 5. Documentation
- `QUICK_START.md`: Quick start guide for beginners
- `UPGRADE_GUIDE.md`: v2.1 upgrade guide
- Updated `README.md`: Comprehensive user manual

## Common User Scenarios

### Scenario 1: Simple One-Command Execution
**User Need**: "I have wos.txt and scopus.csv, want to get merged English-only data and statistics."

**Solution**:
```bash
python3 run_complete_workflow.py --data-dir "/path/to/data"
```

**Output**:
- `english_only.txt` (ready for VOSviewer/CiteSpace)
- `workflow_complete_report.txt` (statistics for paper writing)

### Scenario 2: Custom Language Filtering
**User Need**: "I want to analyze only Chinese literature."

**Solution**:
```bash
python3 run_complete_workflow.py --data-dir "/path/to/data" --language Chinese
```

### Scenario 3: Step-by-Step Processing
**User Need**: "I want to control each step manually."

**Solution**:
```bash
python3 scopus_to_wos_converter.py scopus.csv scopus_converted.txt
python3 merge_deduplicate.py wos.txt scopus_converted.txt merged.txt
python3 filter_language.py merged.txt english_only.txt --language English
python3 analyze_records.py english_only.txt
```

### Scenario 4: Only Format Conversion
**User Need**: "I only have Scopus data, want to convert to WOS format."

**Solution**:
```bash
python3 scopus_to_wos_converter.py scopus.csv output.txt
```

## Important Notes for Claude Code

1. **File Paths**: User data files are often in cloud storage paths with spaces and Chinese characters. Always use quotes and handle paths correctly.

2. **Error Handling**: All scripts have comprehensive error handling with logging. Check logs when debugging.

3. **Encoding**: All WOS files MUST use UTF-8 with BOM (`utf-8-sig`) for VOSviewer compatibility.

4. **Document Types**: The workflow tracks three types: Article, Review, Other. This is critical for paper writing.

5. **Configuration Files**: v2.1+ uses JSON config files in `config/` directory. Check these first when customizing.

6. **Report Generation**: The complete workflow generates a detailed report specifically designed for paper Methods section writing.
