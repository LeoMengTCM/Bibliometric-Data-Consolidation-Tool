# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bibliometric data processing tools for integrating Scopus and Web of Science (WOS) literature data. The toolkit converts Scopus CSV format to standard WOS plain text format, intelligently merges/deduplicates records from both databases, filters by language, and generates comprehensive statistical reports.

**Primary Use Case**: Enable researchers to combine Scopus and WOS data for comprehensive bibliometric analysis using tools like CiteSpace, VOSviewer, and Bibliometrix.

**Version**: v5.0.0 (Stable Release) (2026-01-15)

**Key Features**:
- Format conversion (Scopus CSV → WOS plain text)
- **Batch concurrent processing** ⚡ v4.0.1 (optimized v4.5.2)
  - 5-thread concurrent processing (rate-limited to prevent 429 errors)
  - 3-5 minutes for 660 records vs 70-80 minutes
  - 297 API calls vs 7000+ (95% cost reduction)
  - Intelligent rate limiting with exponential backoff
- **WOS format standardization (AI-driven)** ⭐
  - Country name WOS standardization (China → Peoples R China)
  - Journal name WOS abbreviation (Journal of XXX → J XXX)
  - Author names use original algorithm (not AI, 97%+ accuracy)
  - Database memory for instant recall
- **AI-powered institution enrichment** ⭐
  - State/province code completion
  - ZIP/postal code completion
  - Department information enrichment
  - WOS-standard abbreviations
  - **C1 format fix (v4.5.1)**: Country always as last independent part
- **Year range filtering** ⭐ v4.3.0
  - Filter records by custom year range (e.g., 2015-2024)
  - Remove Early Access articles (2025-2026) and historical references (pre-2015)
  - Automatic anomaly detection and reporting
  - Integrated into one-click workflow
  - **Year filtering first architecture (v4.5.0)**: Filter at source for efficiency
- **WOS Format Alignment** ⭐ v4.4.0
  - Scopus-unique records automatically aligned to WOS standard formats
  - Institution, journal, country, author names use WOS format when available
  - Ensures format consistency across all records
  - C1 country extraction with strict validation (v4.4.1 fix)
- **Institution cleaning** ⭐ v4.3.0
  - Remove noise data and person names (v4.5.1 fix)
  - Merge parent-child institutions
  - Standardize name variants
  - 20% reduction in unique institutions
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
    [Step 1: Format Conversion + WOS Standardization] ⚡ v4.0.1
    enhanced_converter_batch_v2.py (recommended, 20 threads)
    - Country name WOS standardization (60 countries)
    - Journal name WOS abbreviation (237 journals)
    - Author names use original algorithm (not AI)
         ↓
    scopus_converted_to_wos.txt (WOS-standardized)
         ↓
    [Step 2: AI Institution Enrichment] ⭐ NEW
    institution_enricher_v2.py
    - State/province code completion
    - ZIP/postal code completion
    - Department enrichment
         ↓
    scopus_enriched.txt
         ↓
    [Step 3: Merge & Deduplicate + WOS Format Alignment] ⭐ v4.4.0
    merge_deduplicate.py
    - Extract WOS standard formats (institutions, journals, countries, authors)
    - Align Scopus-unique records to WOS standards
    - Strict C1 country validation (v4.4.1)
         ↓
    merged_deduplicated.txt
         ↓
    [Step 4: Language Filter]
    filter_language.py
         ↓
    english_only.txt
         ↓
    [Step 5: Year Range Filter] ⭐ NEW v4.3.0 (Optional)
    filter_by_year.py
    - Custom year range (e.g., 2015-2024)
    - Remove Early Access and historical refs
         ↓
    *_Year_Filtered.txt
         ↓
    [Step 6: Statistical Analysis]
    analyze_records.py
         ↓
Output:
├── scopus_converted_to_wos.txt   (WOS-standardized)
├── scopus_enriched.txt            (AI-enriched)
├── merged_deduplicated.txt        (Full merged dataset)
├── english_only.txt               (Language-filtered)
├── *_Year_Filtered.txt            (Year-filtered, recommended ⭐)
└── *_analysis_report.txt          (Statistical reports)
```

**Automated AI Workflow** (v4.3.0):
```
run_ai_workflow.py --data-dir "/path/to/data" --year-range 2015-2024
  → Executes all steps automatically with AI enhancements
  → Batch concurrent processing (20 threads, 3 min for 660 records)
  → WOS format standardization (country/journal, authors use original algorithm)
  → AI institution enrichment (state/ZIP/department)
  → Year range filtering (removes anomalies) ⭐ NEW
  → Generates comprehensive report with year filtering stats
  → Database memory for instant recall on subsequent runs
  → Performance: 297 API calls, 60 countries, 237 journals
```

### Key Components

**1a. enhanced_converter_batch_v2.py** - Batch Concurrent Converter ⚡ NEW v4.0.1 (RECOMMENDED)
- **EnhancedConverterBatchV2**: Batch concurrent processing with optimized performance
  - 20 concurrent threads (reduced from 50 to avoid API limits)
  - Batch size: 50 items per batch
  - Only standardizes countries (60) and journals (237)
  - Authors use original algorithm (not AI)
  - Database-first approach: check cache before AI call

- **Performance Metrics**:
  - Processing time: 3 minutes for 660 records (vs 70-80 minutes)
  - API calls: 297 total (vs 7000+)
  - Cost: ¥0.01-0.02 per 1000 papers (vs ¥0.14)
  - Speed improvement: 20-30x

**Location**: `enhanced_converter_batch_v2.py`, `wos_standardizer_batch.py`

**1b. enhanced_converter.py** - Enhanced Format Converter with WOS Standardization ⭐ NEW
- **EnhancedConverter**: Integrates base conversion with WOS standardization
  - Wraps ScopusToWosConverter for base conversion
  - Applies WOSStandardizer for format standardization
  - Processes AU, AF, C1, SO fields for WOS compliance

- **WOS Standardization Features**:
  - Country names: Converts to WOS standard (China→Peoples R China, UK→England)
  - Journal names: Generates WOS abbreviations (Journal of XXX→J XXX)
  - Author names: Use original algorithm (not AI, 97%+ accuracy)
  - Database caching: Instant recall for previously seen items

**Location**: `enhanced_converter.py`, `wos_standardizer.py`

**1b. scopus_to_wos_converter.py** - Base Format Converter
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

**2. merge_deduplicate.py** - Merge & Deduplication Tool with WOS Format Alignment ⭐ v4.4.0
- **WOSRecordParser**: Parses WOS plain text format into structured records
  - Handles multi-line field continuations (3-space indent)
  - Preserves field order and formatting

- **WOSStandardExtractor** ⭐ NEW v4.4.0: Extracts and applies WOS standard formats
  - Extracts institution names (C3 field) from WOS records
  - Extracts journal names (SO field) from WOS records
  - Extracts country names (C1 field) with strict validation (v4.4.1)
  - Extracts author names (AU field) from WOS records
  - `_is_valid_country()`: Validates country names, excludes person names/state codes
  - `standardize_scopus_record()`: Aligns Scopus-unique records to WOS standards

- **RecordMatcher**: Identifies duplicate records between WOS and Scopus
  - Primary strategy: DOI matching (100% accuracy)
  - Fallback strategy: Normalized title + year + first author matching

- **RecordMerger**: Merges WOS and Scopus records
  - WOS records take priority (more complete data)
  - Scopus supplements missing WOS fields
  - Citation count: takes maximum of both sources
  - C1/C3 fields: Strictly use WOS format, only supplement if completely missing

- **MergeDeduplicateTool**: Orchestrates the merge workflow (5 steps)
  - Step 1: Read WOS and Scopus files
  - Step 2: Extract WOS standard formats ⭐ NEW
  - Step 3: Identify WOS-Scopus duplicates
  - Step 4: Merge records with WOS format alignment ⭐ NEW
  - Step 5: Write output with standardization statistics

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

**3b. filter_by_year.py** - Year Range Filter Tool ⭐ NEW v4.3.0
- **YearFilter**: Filters records by year range
  - Parses WOS format and identifies PY (publication year) field
  - Filters records within specified year range (e.g., 2015-2024)
  - Detects and removes anomalies (Early Access, historical references)
  - Generates detailed year distribution statistics
  - Preserves WOS format and UTF-8 BOM encoding

- **Key Methods**:
  - `parse_wos_file()`: Parses WOS file and extracts year information
  - `should_keep_record()`: Determines if record matches year criteria
  - `filter_records()`: Filters by year range
  - `write_filtered_file()`: Writes filtered WOS file
  - `generate_report()`: Creates filtering report with year statistics

- **Usage**:
  ```bash
  # Filter by year range
  python3 filter_by_year.py input.txt output.txt --year-range 2015-2024

  # Specify min/max separately
  python3 filter_by_year.py input.txt output.txt --min-year 2015 --max-year 2024
  ```

**Location**: `filter_by_year.py`

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

**6. wos_standardizer.py** - WOS Format Standardization Engine ⭐ NEW
- **WOSStandardDatabase**: Persistent cache for WOS standard formats
  - JSON-based storage at `config/wos_standard_cache.json`
  - Stores author names, country names, journal abbreviations
  - Instant lookup for previously standardized items

- **WOSStandardizer**: AI-driven WOS format standardization
  - `standardize_author()`: Removes diacritics, normalizes format
  - `standardize_country()`: Converts to WOS country standards
  - `standardize_journal()`: Generates WOS journal abbreviations
  - Gemini API integration with retry mechanism
  - Database-first approach (check cache before AI call)

- **Key Features**:
  - Database memory: First run uses AI, subsequent runs use cache
  - WOS compliance: Follows exact WOS formatting rules
  - Cost optimization: Zero cost after initial learning
  - Speed: <0.01s for cached items vs 2-3s for AI calls

**Location**: `wos_standardizer.py`

**7. institution_enricher_v2.py** - AI Institution Enrichment System ⭐ NEW
- **InstitutionEnricherV2**: AI-powered institution information completion
  - Integrates with GeminiEnricherV2 for AI calls
  - Enriches C1 field with missing geographic information
  - Database-first approach with persistent caching

- **Enrichment Features**:
  - State/province codes (FL, CA, Hunan, etc.)
  - ZIP/postal codes (32804, 410208, etc.)
  - Department information (Oncol & Hematol, Sch Med, etc.)
  - WOS-standard abbreviations (Univ, Inst, Med, Hosp, etc.)

- **Database**: `config/institution_ai_cache.json`
  - Persistent storage of enriched institutions
  - Metadata tracking (confidence, source, timestamp)
  - Automatic backup on save

**Location**: `institution_enricher_v2.py`, `gemini_enricher_v2.py`

**8. run_ai_workflow.py** - One-Click AI-Enhanced Workflow ⭐ NEW
- **AIWorkflow**: Complete automated processing pipeline
  - Step 1: Scopus conversion + WOS standardization
  - Step 2: AI institution enrichment
  - Step 3: Merge and deduplicate
  - Step 4: Language filtering
  - Step 5: Statistical analysis
  - Comprehensive reporting with all statistics

- **Key Features**:
  - Single command execution
  - Automatic WOS standardization
  - Optional AI enrichment (--no-ai to disable)
  - Detailed progress tracking
  - Complete workflow report generation

**Location**: `run_ai_workflow.py`

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

### Running the AI-Enhanced Workflow (Recommended, v4.3.0+)
```bash
# Complete AI-enhanced workflow (WOS standardization + AI enrichment + Year filtering)
python3 run_ai_workflow.py --data-dir "/path/to/data" --year-range 2015-2024

# Example:
python3 run_ai_workflow.py \
  --data-dir "/Users/xxx/文献计量学/Nano_NSCLC_Immune" \
  --year-range 2015-2024

# Requires: wos.txt and scopus.csv in data directory
# Produces:
#   - scopus_converted_to_wos.txt (WOS-standardized)
#   - scopus_enriched.txt (AI-enriched with state/ZIP/department)
#   - merged_deduplicated.txt (full merged dataset)
#   - english_only.txt (English-only)
#   - Final_Version_Year_Filtered.txt (Year-filtered, recommended ⭐)
#   - ai_workflow_report.txt (comprehensive statistics with year filtering)

# Optional parameters:
python3 run_ai_workflow.py \
  --data-dir "/path/to/data" \
  --year-range 2015-2024 \
  --language Chinese \
  --no-ai \
  --no-cleaning \
  --log-level WARNING
```

### Running the Complete Workflow (Traditional, v2.1+)
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
# Step 1: Convert Scopus to WOS format with WOS standardization (v3.2.0+)
python3 enhanced_converter.py input.csv output.txt

# Step 1b: Base conversion without WOS standardization
python3 scopus_to_wos_converter.py input.csv output.txt

# Step 2: AI institution enrichment (v3.2.0+)
python3 institution_enricher_v2.py \
    --input scopus_converted.txt \
    --output scopus_enriched.txt \
    --model gemini-2.5-flash

# Step 3: Merge and deduplicate
python3 merge_deduplicate.py wos.txt scopus_enriched.txt merged.txt

# Step 4: Filter by language
python3 filter_language.py merged.txt english_only.txt --language English

# Step 4b: Filter by year range (v4.3.0+) ⭐ NEW
python3 filter_by_year.py english_only.txt filtered_2015-2024.txt --year-range 2015-2024

# Step 5: Statistical analysis
python3 analyze_records.py filtered_2015-2024.txt --config-dir config

# Test WOS standardization
python3 test_wos_standardization.py
python3 wos_standardizer.py --type author --input "Pénault-Llorca, F"
```

### Testing
No formal test suite exists. Manual verification approach:
1. Compare conversion output with real WOS data samples
2. Verify field-by-field accuracy (see 转换质量对比报告.md)
3. Import into VOSviewer/CiteSpace to ensure format compatibility
4. Check deduplication report for accuracy

## AI Enhancement System Details

### WOS Format Standardization (v3.2.0+)

**Problem Solved**: Scopus data contains diacritics and non-standard formats that cause VOSviewer/CiteSpace to misidentify authors and countries.

**Solution**: AI-driven standardization with database memory.

**Implementation** (`wos_standardizer.py`):
1. **Database-first approach**: Check cache before AI call
2. **AI standardization**: Use Gemini to learn WOS standards
3. **Persistent storage**: Save to `config/wos_standard_cache.json`
4. **Instant recall**: Subsequent runs use cache (zero cost, <0.01s)

**Standardization Rules**:
- **Authors**: Remove all diacritics (é→e, ñ→n, ö→o, ü→u), keep compound lastnames
- **Countries**: WOS standards (China→Peoples R China, UK→England, Turkey→Turkiye)
- **Journals**: WOS abbreviations (Journal→J, American→AM, Medicine→MED)

**Quality Impact**:
- Author accuracy: 81.8% → ~100%
- Country accuracy: 50% → 95%+
- Overall quality: 3/5 → 4.5/5 stars

**Location**: `wos_standardizer.py:50-280`

### AI Institution Enrichment (v3.2.0+)

**Problem Solved**: Scopus institution data lacks state codes, ZIP codes, and detailed department information (60% completeness vs WOS 100%).

**Solution**: AI-powered enrichment with database caching.

**Implementation** (`institution_enricher_v2.py`, `gemini_enricher_v2.py`):
1. **Parse C1 field**: Extract institution, city, country
2. **Check database**: Look for cached enrichment
3. **AI enrichment**: Call Gemini API if not cached
4. **Rebuild C1**: Reconstruct with enriched information
5. **Save database**: Persist for future use

**Enrichment Details**:
- State/province codes: FL, CA, NY, Hunan, Guangdong
- ZIP/postal codes: 32804, 410208, 63000
- Departments: Oncol & Hematol, Sch Med, Dept Pathol
- WOS abbreviations: Univ, Inst, Med, Hosp, Canc

**Performance**:
- First run: ~3s per institution, 95.7% success rate
- Second run: <0.01s per institution (database hit)
- Cost: ¥0.14 per 1000 papers (first run), ¥0 (cached)

**Database**: `config/institution_ai_cache.json`
- Stores enriched institutions with metadata
- Automatic backup on save
- Shareable across projects

**Location**: `institution_enricher_v2.py:35-410`, `gemini_enricher_v2.py:171-629`

### Gemini API Integration

**Configuration** (`gemini_config.py`):
```python
API URL: https://gptload.drmeng.top/proxy/bibliometrics/v1beta
API Key: sk-leomeng1997
Model: gemini-2.5-flash (or gemini-2.5-flash-lite)
Max Tokens: 5000 (institution enrichment), 500 (standardization)
Retry: 3 attempts with 5s delay
```

**Models**:
- `gemini-2.5-flash`: Higher accuracy (95.7%), ¥0.14/1000 papers
- `gemini-2.5-flash-lite`: Faster, cheaper (90-95%), ¥0.05/1000 papers

**Recommendation**: Use flash for building database (first 100+ institutions), then switch to flash-lite for daily use.

**Location**: `gemini_config.py:21-210`

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

### WOS Format Alignment (v4.4.0+)

**Purpose**: Ensure Scopus-unique records (not in WOS) use WOS standard formats for institution/journal/country/author names.

**Implementation** (`merge_deduplicate.py`):
1. **Extract WOS Standards**: Parse all WOS records to build dictionaries of standard formats
   - Institutions (C3): `{lowercase: WOS_format}`
   - Journals (SO): `{lowercase: WOS_format}`
   - Countries (C1): `{lowercase: WOS_format}` with strict validation
   - Authors (AU): `{lowercase: WOS_format}`

2. **Validate Country Names** (v4.4.1 critical fix):
   - **Excludes person names**: "Aaron M", "Abdallah S" (Name + single letter)
   - **Excludes state codes**: "AL USA", "CA USA" (2-letter + USA)
   - **Excludes numbers**: Postal codes, building numbers
   - **Validates length**: 4-30 characters typical for countries
   - **Common WOS countries**: 50+ countries in reference list (Peoples R China, USA, England, etc.)
   - **Multi-word validation**: All words must be > 1 letter (not initials)

3. **Align Scopus-unique records**:
   - Check each field (institution/journal/country/author)
   - If value appears in WOS dictionary → use WOS format
   - If not in WOS → keep Scopus format
   - Apply alignment to C1, C3, SO, AU fields

**Benefits**:
- Prevents format inconsistencies in bibliometric tools
- Avoids duplicate entities (same institution with different capitalization)
- Critical for VOSviewer/CiteSpace accuracy

**Statistics Reported**:
```
Scopus独有记录:         150 条（已保留）
  ⭐ Scopus独有记录标准化: 150 条
     （机构、期刊、国家、作者已对齐WOS格式）
```

**Location**: `merge_deduplicate.py:192-303` (`WOSStandardExtractor`), `merge_deduplicate.py:510-545` (`merge_records`)

**Related Documentation**:
- `WOS_FORMAT_ALIGNMENT.md`: Detailed alignment logic and examples
- `C1_COUNTRY_EXTRACTION_FIX.md`: C1 country validation fixes

## Known Limitations

1. **Author Full Names (AF field)**: Scopus sometimes provides only abbreviated names, not full names
   - **Mitigation (v3.2.0+)**: WOS standardization removes diacritics, improving accuracy from 45.5% to 90%+
2. **Reference Citations (CR field)**: Author initials may be missing, volume/page numbers may be imprecise due to format differences
3. **Institution Address Format (C1 field)**: Scopus groups by author, WOS groups by institution - semantic equivalent but structurally different
   - **Mitigation (v3.2.0+)**: AI enrichment adds missing state codes, ZIP codes, and departments, improving completeness from 60% to 95%
   - **Fixed (v4.5.1)**: C1 format now ensures country is always the last independent comma-separated part

These limitations are documented in `example/检验报告_v3.2.0.md` with detailed comparisons to real WOS data.

## Recent Critical Fixes

### v4.5.2 - API Rate Limit Fix (2025-11-20) ⭐ CRITICAL

**Problem**: 频繁遇到429错误（Too Many Requests），导致AI补全失败。

**Root Causes**:
1. 并发线程数过多（50个线程同时调用API）
2. 延迟位置错误（在API调用后延迟）
3. 批量调用缺少延迟（连续发送请求）
4. 429错误处理不完善（固定等待时间）

**Fixes**:
1. **降低并发线程数**: 50 → 5 (降低90%)
2. **修复延迟位置**: 延迟移到API调用前
3. **添加批次间延迟**: 批量处理时每批间隔2-3秒
4. **改进429处理**: 等待2分钟，最多重试7次（独立计数）
5. **创建全局速率限制器**: 新增`rate_limiter.py`工具类

**Impact**:
- 请求频率: 50 req/s → 3 req/s (降低94%)
- 429错误: 频繁发生 → 几乎消除
- 处理时间: 略微增加但更稳定可靠

**Files Modified**:
- `wos_standardizer_batch.py` (并发数、延迟、429处理)
- `gemini_enricher_v2.py` (批次延迟、指数退避)
- `enhanced_converter_batch_v2.py` (并发参数、批次延迟)
- `rate_limiter.py` (新增)

**Documentation**: See `API_RATE_LIMIT_FIX.md` for detailed analysis and recommendations.

---

### v4.5.1 - C1 Format & Institution Cleaning (2025-11-20)

**Date**: 2025-11-20

1. **AI Enrichment C1 Format Fix** ⭐ CRITICAL
   - **Problem**: State and ZIP were merged (e.g., "FL 32804"), preventing country extraction
   - **Fix**: State and ZIP now separate parts, country always last
   - **Impact**: WOS format alignment now works correctly for AI-enriched records

2. **Institution Cleaning Person Name Filter** ⭐ CRITICAL
   - **Problem**: C3 field contained person names (e.g., "Smith, J", "Wang, L")
   - **Fix**: Added regex filters to detect and remove person name patterns
   - **Impact**: VOSviewer institution analysis now accurate, no person names in network

3. **Plot Generation Confirmation** ✅
   - **Status**: `generate_all_figures()` function exists and works
   - **Note**: Requires `matplotlib` and `plot_publications_citations.py`

**Recommendation**: Re-run workflow on existing projects to get corrected results.

See `BUGFIX_v4.5.1.md` for detailed fix documentation.

## File Encoding Requirements

All input/output files:
- **Encoding**: UTF-8 with BOM (`utf-8-sig` in Python)
- **Line endings**: Unix-style (`\n`)
- **CSV reading**: Must handle `utf-8-sig` to strip BOM automatically

## Database Files (v3.2.0+)

**WOS Standardization Database**: `config/wos_standard_cache.json`
- Stores WOS-standardized author names, country names, journal abbreviations
- JSON format with metadata tracking
- Shareable across projects
- Backup automatically created on save

**AI Institution Enrichment Database**: `config/institution_ai_cache.json`
- Stores AI-enriched institution information
- Includes state codes, ZIP codes, departments
- Metadata: confidence scores, timestamps, source
- Automatic backup to `config/ai_cache_backup/`

**Database Management**:
```bash
# View database stats
python3 -c "import json; db=json.load(open('config/wos_standard_cache.json')); print(f'Authors: {len(db[\"authors\"])}, Countries: {len(db[\"countries\"])}, Journals: {len(db[\"journals\"])}')"

# Backup databases
cp config/wos_standard_cache.json config/wos_standard_cache_backup.json
cp config/institution_ai_cache.json config/institution_ai_cache_backup.json

# Clear databases (force re-learning)
rm config/wos_standard_cache.json
rm config/institution_ai_cache.json
```

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
- **Dependencies**:
  - Standard library: csv, re, datetime, typing, textwrap, collections, json, subprocess, argparse, logging, time, pathlib
  - **requests** (for AI features): `pip3 install requests`
- **No virtual environment needed**

**Installation**:
```bash
# Install requests for AI features
pip3 install requests

# Or with --break-system-packages on macOS
pip3 install --break-system-packages requests
```

## v3.2.0 + AI Enhancement v2.0 New Features Summary

### 1. WOS Format Standardization System ⭐ NEW
**Purpose**: Ensure 100% WOS format compliance by removing diacritics and standardizing names.

**Features**:
- Author name diacritics removal (Pénault-Llorca → Penault-Llorca)
- Country name WOS standardization (China → Peoples R China)
- Journal name WOS abbreviation (Journal of XXX → J XXX)
- Database memory for instant recall

**Usage**:
```bash
# Automatic in AI workflow
python3 run_ai_workflow.py --data-dir "/path/to/data"

# Or standalone
python3 enhanced_converter.py scopus.csv output.txt
```

**Impact**:
- Author accuracy: 81.8% → ~100%
- Country accuracy: 50% → 95%+
- Overall quality: 3/5 → 4.5/5 stars

### 2. AI Institution Enrichment System ⭐ NEW
**Purpose**: Complete missing geographic and departmental information in Scopus data.

**Features**:
- State/province code completion (FL, CA, Hunan)
- ZIP/postal code completion (32804, 410208)
- Department information enrichment (Oncol & Hematol)
- WOS-standard abbreviations (Univ, Inst, Med)
- Database caching (98x speed improvement on second run)

**Usage**:
```bash
python3 institution_enricher_v2.py \
    --input scopus_converted.txt \
    --output scopus_enriched.txt
```

**Performance**:
- Success rate: 95.7%
- First run: ~3s per institution
- Second run: <0.01s per institution (cached)
- Cost: ¥0.14 per 1000 papers (first run)

### 3. One-Click AI Workflow ⭐ NEW
**Purpose**: Execute complete processing pipeline with single command.

**Features**:
- Automatic WOS standardization
- Optional AI enrichment
- Merge and deduplicate
- Language filtering
- Statistical analysis
- Comprehensive reporting

**Usage**:
```bash
python3 run_ai_workflow.py --data-dir "/path/to/data"
```

### 4. Database Memory System ⭐ NEW
**Purpose**: Eliminate redundant AI calls through persistent caching.

**Databases**:
- `config/wos_standard_cache.json`: WOS format standards
- `config/institution_ai_cache.json`: Enriched institutions

**Benefits**:
- Zero cost after initial learning
- 98x speed improvement
- Shareable across projects
- Automatic backup

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
