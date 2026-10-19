English | [简体中文版](README.zh-CN.md)

# Trails Series 100% Walkthrough & Vector PDF Publishing Pipeline

> Automated pipeline for compiling, typesetting, and rendering publication-grade A4 vector PDFs in a high-fidelity JRPG Tactical Terminal style for Falcom's *The Legend of Heroes: Trails Series*.  
> **Includes all 13 core games**: Trails in the Sky the 1st (Remake), the 2nd (Remake), the 3rd, Trails from Zero, Trails to Azure, Trails of Cold Steel I–IV, Trails into Reverie, Trails through Daybreak I–II, and Kai no Kiseki (Farewell, O Zemuria).

---

## 📖 Overview

This project provides a fully engineered, modular, and automated pipeline for scraping game data, semantic parsing, CSS Paged Media layout composition, and lossless vector PDF rendering.

The visual design closely follows the iconic **Bracer Guild Tactical Orbment Terminal** interface from the *Trails Series*, featuring custom saga palettes (Orbment Deep Blue, Crossbell Teal, Thors Imperial Crimson, Reverie Violet, Arkride Night-Navy), gold highlights, and concentric orbment geometry. It incorporates extensive CSS Paged Media rules (`@page` margins, `break-inside: avoid` orphan protection, zebra-striped data tables, and missable alert badges) optimized for tablet viewing and dual-sided physical printing.

---

## 🎯 Deliverables (13 Independent PDFs)

Independent high-resolution vector PDFs for all 13 games are generated in the [`dist/`](dist/) directory, totaling **1,793 pages** with 100% complete, un-truncated collectibles (all novel volumes, limited periodicals, cooking recipes, fishing & memory door compendiums, and complete Character Notes for Cold Steel 1–4 and Reverie):

| No. | Saga & Game Title | Max Points | Pages | PDF Size | File Deliverable |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **01** | **Trails in the Sky the 1st (Remake)** | 368 BP | 52 p. | 7.91 MB | [`空之轨迹_the_1st_重制版_100全要素详细攻略.pdf`](dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf) |
| **02** | **Trails in the Sky the 2nd (Remake)** | 382 BP | 50 p. | 7.62 MB | [`空之轨迹_the_2nd_重制版_100全要素详细攻略.pdf`](dist/空之轨迹_the_2nd_重制版_100全要素详细攻略.pdf) |
| **03** | **Trails in the Sky the 3rd** | Platinum | 34 p. | 5.23 MB | [`空之轨迹_the_3rd_100全要素详细攻略.pdf`](dist/空之轨迹_the_3rd_100全要素详细攻略.pdf) |
| **04** | **Trails from Zero** | 380 DP | 86 p. | 10.71 MB | [`零之轨迹_100全要素详细攻略.pdf`](dist/零之轨迹_100全要素详细攻略.pdf) |
| **05** | **Trails to Azure** | 405 DP | 121 p. | 12.62 MB | [`碧之轨迹_100全要素详细攻略.pdf`](dist/碧之轨迹_100全要素详细攻略.pdf) |
| **06** | **Trails of Cold Steel I** | 440 AP | 95 p. | 11.50 MB | [`闪之轨迹1_100全要素详细攻略.pdf`](dist/闪之轨迹1_100全要素详细攻略.pdf) |
| **07** | **Trails of Cold Steel II** | 315 AP | 102 p. | 12.38 MB | [`闪之轨迹2_100全要素详细攻略.pdf`](dist/闪之轨迹2_100全要素详细攻略.pdf) |
| **08** | **Trails of Cold Steel III** | 417 AP | 146 p. | 14.37 MB | [`闪之轨迹3_100全要素详细攻略.pdf`](dist/闪之轨迹3_100全要素详细攻略.pdf) |
| **09** | **Trails of Cold Steel IV** | 353 AP | 229 p. | 19.41 MB | [`闪之轨迹4_100全要素详细攻略.pdf`](dist/闪之轨迹4_100全要素详细攻略.pdf) |
| **10** | **Trails into Reverie** | Platinum | 271 p. | 21.83 MB | [`创之轨迹_100全要素详细攻略.pdf`](dist/创之轨迹_100全要素详细攻略.pdf) |
| **11** | **Trails through Daybreak I** | 405 SP | 186 p. | 16.00 MB | [`黎之轨迹1_100全要素详细攻略.pdf`](dist/黎之轨迹1_100全要素详细攻略.pdf) |
| **12** | **Trails through Daybreak II** | 408 SP | 202 p. | 16.57 MB | [`黎之轨迹2_100全要素详细攻略.pdf`](dist/黎之轨迹2_100全要素详细攻略.pdf) |
| **13** | **Kai no Kiseki -Farewell, O Zemuria-** | 415 SP | 219 p. | 15.36 MB | [`界之轨迹_100全要素详细攻略.pdf`](dist/界之轨迹_100全要素详细攻略.pdf) |

### Every Guide Standardly Features:
1. **Cover & Tactical Terminal TOC**: Immersive tech terminal cover with platinum achievement targets (BP/DP/AP/RP/SP) and direct navigation anchors.
2. **Comprehensive Chapter Walkthrough**: Complete coverage of main story, side quests, hidden dialog branches, red missable alerts, and field action / command battle strategies.
3. **Structured In-Flow Tables & Tactical Callouts**: Quest reward summaries, Q&A choices, and LGC alignment progression are displayed in crisp JRPG terminal tables, while tactical Tips and time-limited Alerts are highlighted with dedicated callout boxes.
4. **Boss Tactical Dossiers**: Weakness effectiveness tables (Earth, Water, Fire, Wind, Time, Space, Mirage), abnormal status immunities, and S-Craft burst recommendations.
5. **Appendix 1: Complete Books & Periodicals**: Novels, limited-time magazines, newspapers, and academic documents with ultimate weapon exchange indicators.
6. **Appendix 2: Full Cooking & Recipe List**: Recipe names, locations, recommended chefs, master dishes (unique), failure dishes, and stat bonuses.
7. **Appendix 3: Complete Fishing & Memory Doors Compendium**: Rod tiers, bait pairings, fishing grounds, and sepith/item drops (3rd exclusively features all 25 Sun, Moon, and Star Doors with unlock requirements and rewards).
8. **Appendix 4: Complete Character Notes (Exclusive to Cold Steel 1–4 & Reverie)**: All 806 entries with precise unlock timeframes and NPC dialogue conditions.
9. **Appendix 5/4: NG+ Carryover & Ultimate Superbosses**: Carryover guide and high-difficulty superboss tactics.

---

## 🏗 Pipeline Architecture

```
[trails-game.com / Guide Database]
                 │
                 ▼
          src/scraper.py           (Web cache & persistence engine)
                 │
                 ▼
          src/parser.py            (Sora 1st Remake deep parser)
       src/universal_builder.py    (Universal multi-game parser & HTML builder)
                 │
                 ▼
        templates/style.css        (Bracer Terminal JRPG print styles)
                 │
                 ▼
        src/pdf_exporter.py        (Chrome Headless Skia vector renderer)
                 │
                 ▼
        src/batch_runner.py        (12-game batch compilation runner)
              main.py              (Unified CLI entry point)
                 │
                 ▼
               dist/*.pdf          (12 Independent Publication-Grade PDFs)
```

---

## 🚀 Quick Start

### 1. Requirements
- **Python**: 3.10 or higher
- **Browser**: Google Chrome or Chromium (standard installation or configured via `CHROME_BIN` environment variable)
- **OS**: macOS / Linux / Windows

### 2. Commands

```bash
# Batch generate all 12 independent PDFs
python3 main.py --all

# Generate a specific game (e.g. Kai no Kiseki)
python3 main.py --game kai

# Default: Generate benchmark game (Trails in the Sky the 1st Remake)
python3 main.py

# HTML-only preview (fast browser debugging without calling Chrome)
python3 main.py --game zero --html-only
```

---

## 🧪 Automated Testing

Run the full unit and integration test suite:

```bash
python3 -m unittest discover -s tests
```

---

## 📝 Author & Copyright

- **Author**: Steve Shi / 轩楝 (`zh-Hans`)
- **Copyright Notice**: *The Legend of Heroes: Trails Series* and all related characters, lore, and assets are trademarks and copyright of Nihon Falcom Corporation.
