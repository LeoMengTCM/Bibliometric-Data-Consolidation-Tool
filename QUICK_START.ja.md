# クイックスタート

[English](QUICK_START.md) | [中文](QUICK_START.zh-CN.md) | 日本語

## プロジェクトの位置づけ

このリポジトリは、**WOS を基準にした Scopus→WOS 変換・統合システム**として使うことを想定しています。一般的なクリーニング用スクリプト集ではありません。

## 最初に試す実行

同梱の再現用サンプル：

```text
Example/
├── wos.txt
└── scopus.csv
```

ローカル規則と WOS 整合ロジックを先に確認する場合：

```bash
python3 run_ai_workflow.py --data-dir Example --no-ai
```

既定のフルワークフローを実行する場合：

```bash
python3 run_ai_workflow.py --data-dir Example
```

## 入力ファイル

自分のデータディレクトリには次の 2 ファイルが必要です。

```text
/path/to/your-data/
├── wos.txt
└── scopus.csv
```

## 標準ワークフローの内容

1. Scopus CSV を WOS 風プレーンテキストへ変換
2. 現在の WOS コーパスで変換と `C3` 整合を校正
3. WOS と Scopus を統合し重複除去
4. 言語フィルタ
5. 所属クリーニング
6. 解析と図表生成

## よく使うコマンド

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data"
```

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --no-ai
```

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --no-cleaning
```

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --year-range 2015-2024
```

```bash
python3 run_ai_workflow.py --data-dir "/path/to/data" --language Chinese
```

```bash
python3 run_ai_workflow.py --help
```

## `--no-ai` の意味

`--no-ai` でもローカルの WOS 指向変換は止まりません。

残るもの：

- ローカル Scopus → WOS 風変換
- ローカル WOS コーパス校正
- 重複ペアを踏まえた `C3` 補完
- マージ / 重複除去 / フィルタ / クリーニング / 解析

止まるもの：

- AI による WOS 風標準化
- AI による所属補完

## 主な出力

- `scopus_converted_to_wos.txt`
- `scopus_enriched.txt`
- `merged_deduplicated.txt`
- `english_only.txt` など
- `Final_Version.txt`
- `*_analysis_report.txt`
- `ai_workflow_report.txt`
- `Figures and Tables/`

## 現在の検証スナップショット

同梱サンプルでの local round11 では、100 件の重複ペアにおける `C3` 差分が `24` から `12` に改善しています。

## GUI 起動

```bash
python3 gui_app.py
```

または `启动GUI.command` をダブルクリックします。

## 次に読むもの

- `README.ja.md`
- `PROJECT_STRUCTURE.md`
- `docs/README.md`
- `docs/WOS标准化说明.md`
