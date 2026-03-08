# Quick Start

English | [中文](QUICK_START.zh-CN.md) | [日本語](QUICK_START.ja.md)

## Project orientation

Use this repository as a **WOS-guided Scopus→WOS conversion and consolidation system**, not as a generic cleaning script collection.

## Recommended first run

The bundled reproducible example is:

```text
Example/
├── wos.txt
└── scopus.csv
```

For a deterministic local run focused on the rule-based conversion and merge logic:

```bash
python3 run_ai_workflow.py --data-dir Example --no-ai
```

For the default full workflow:

```bash
python3 run_ai_workflow.py --data-dir Example
```

## Required input files

Your own data directory must contain:

```text
/path/to/your-data/
├── wos.txt
└── scopus.csv
```

## What the default workflow does

1. Convert Scopus CSV to WOS-style plain text
2. Use the current WOS corpus to calibrate conversion and `C3` alignment
3. Merge WOS and Scopus with deduplication
4. Filter records by language
5. Clean institution names
6. Analyze records and generate figures

## Common commands

Basic run:

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data"
```

Disable the AI branch only:

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --no-ai
```

Disable institution cleaning:

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --no-cleaning
```

Restrict the year range:

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --year-range 2015-2024
```

Filter Chinese-language records:

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --language Chinese
```

Show help:

```bash
python3 run_ai_workflow.py --help
```

## Important note about `--no-ai`

`--no-ai` does **not** turn off the local WOS-guided conversion logic.

It still keeps:

- local Scopus → WOS-style conversion
- local WOS-corpus calibration
- local duplicate-aware `C3` recovery
- merge / deduplication / filtering / cleaning / analysis

It skips only:

- AI-based WOS-style normalization
- AI-based institution enrichment

## Main outputs

- `scopus_converted_to_wos.txt`
- `scopus_enriched.txt`
- `merged_deduplicated.txt`
- `english_only.txt` or another language-filtered file
- `Final_Version.txt`
- `*_analysis_report.txt`
- `ai_workflow_report.txt`
- `Figures and Tables/`

## Validation snapshot

The current local review on the bundled example reduced duplicate-pair `C3` differences on 100 overlapping WOS/Scopus pairs from `24` to `12` by round11.

## GUI launch

```bash
python3 gui_app.py
```

Or double-click `启动GUI.command` in the project root.

## Read next

- `README.md`
- `PROJECT_STRUCTURE.md`
- `docs/README.md`
- `docs/WOS标准化说明.md`
