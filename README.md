[简体中文版](README.zh-CN.md) | English

# Trails Walkthrough PDF Generator

> High-Fidelity JRPG Tactical Terminal Walkthrough & Vector PDF Publishing Pipeline for *The Legend of Heroes: Trails* Series.  
> Master Benchmark Showcase: **The Legend of Heroes: Trails in the Sky the 1st (Remake) — 100% Full Walkthrough & Platinum Trophy Guide**.

---

## 📖 Overview

This project provides an automated, publishing-grade pipeline to scrape, parse, build, and export comprehensive 100% platinum walkthroughs for Falcom's *Trails* series into beautiful, printable vector A4 PDFs.

Designed with an immersive **Bracer Guild Tactical Orbment Terminal** interface, every section adheres strictly to CSS Paged Media standards (`@page`, `break-inside: avoid`, high-contrast typography, and tactile color accents), producing pixel-perfect documents ready for reading on tablets, monitors, or physical double-sided printing.

---

## 🎯 Master Benchmark: *Trails in the Sky the 1st (Remake)*

The project includes the master deliverable:
- **File**: [`dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf`](dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf)
- **Pages**: 52 A4 Vector Pages
- **File Size**: ~7.91 MB
- **Coverage Highlights**:
  - **100% Full BP Path (368 BP Max)**: All prologue through final chapter main scenarios and side quests with strict timeframes and dialogue choices.
  - **Remake Exclusive Mechanics**: Field battle tactics, command battle optimizations, newly added remake sub-quests, and NG+ carryover / LV+50 difficulty adjustments.
  - **Complete Collection Encyclopedias**:
    - *Carnelia* (红耀石) Vol 1–11 complete novels + Liberl News complete issues with missable warnings.
    - Full cooking recipe compendium (30+ recipes) including recommend chef assignments, unique dishes (独门料理), and peculiar dishes (意外料理).
    - Complete fishing log (全钓鱼图鉴) with bait matching, rod recommendations, coordinates, and septium drop tables.
  - **Boss Tactics & Counters**: Action orders, weakness element tables, counter strategies, and party loadouts.

---

## 🏗 System Architecture

The pipeline consists of four modular, decoupled layers:

```
[Falcom Data / Web Cache]
           │
           ▼
   src/scraper.py         (Scrapes and caches raw walkthrough pages)
           │
           ▼
   src/parser.py          (Parses into structured JSON/Dict schema: quests, books, recipes, fish)
           │
           ▼
   src/builder.py         (Renders JRPG Tactical Terminal HTML + templates/style.css)
           │
           ▼
   src/pdf_exporter.py    (Headless Chrome Skia PDF engine with vector typography)
           │
           ▼
        main.py           (One-click CLI entry point)
           │
           ▼
   dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf (Final Master PDF)
```

1. **Scraper (`src/scraper.py`)**: Fetches raw walkthrough documents from established Falcom game wikis with local caching.
2. **Parser (`src/parser.py`)**: Normalizes raw markup into clean Python data contracts with validation and fallback heuristics.
3. **HTML Builder (`src/builder.py`)**: Assembles responsive, printable HTML adhering to Falcom tactical terminal UI themes (`templates/style.css`).
4. **PDF Exporter (`src/pdf_exporter.py`)**: Uses Google Chrome Headless mode (`--headless=new`, Skia vector engine) to render pristine A4 PDFs without watermarks or page headers/footers.
5. **CLI Runner (`main.py`)**: Unified command-line interface with options for custom output and fast preview.

---

## 🚀 Quick Start

### 1. Requirements

- **Python**: 3.10 or higher
- **Browser**: Google Chrome or Chromium (installed in standard location or specified via `CHROME_BIN`)
- **OS**: macOS, Linux, or Windows

### 2. Generate the Master PDF

Run the unified CLI runner from the project root:

```bash
# Generate the master benchmark PDF (outputs to dist/)
python3 main.py
```

### 3. CLI Options

```bash
# View CLI help
python3 main.py --help

# Generate HTML only (for instant browser preview)
python3 main.py --html-only

# Specify custom PDF output destination
python3 main.py -o /path/to/custom_guide.pdf
```

---

## 🧪 Testing & Verification

The project maintains comprehensive unit tests across all pipeline stages:

```bash
python3 -m unittest discover tests
```

- `test_parser.py`: Schema validation, quest completeness, BP totals, and data integrity.
- `test_builder.py`: HTML generation, table structures, and style integration.
- `test_pdf_exporter.py`: Headless Chrome binary detection, PDF generation, and error handling.
- `test_main.py`: Command-line options, failure handling, and custom output routes.

---

## 📝 Author & Acknowledgments

- **Author**: Steve Shi / 轩楝 (`zh-Hans`)
- **Affiliation**: Bracer Guild Liberl Branch Tactical Intelligence
- **Copyright**: *The Legend of Heroes* and all related characters and trademarks are copyright © Nihon Falcom Corporation.
