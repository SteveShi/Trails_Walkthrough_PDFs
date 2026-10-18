[English](README.md) | 简体中文版

# 轨迹系列全要素攻略与矢量 PDF 出版级生成系统

> 针对 Falcom《英雄传说：轨迹系列》打造的高清战术终端风格排版与出版级矢量 A4 PDF 自动化流水线。  
> 首发标杆示范作品：**《英雄传说 空之轨迹 the 1st（重制版）》100% 全要素详细攻略·白金典藏版**。

---

## 📖 方案概览

本项目提供了一套完全工程化、解耦、自动化的 JRPG 攻略数据抓取、语义解析、排版构建与无损矢量 PDF 导出系统。

版面视觉设计严格参照《空之轨迹》经典 **游击士协会战术导力终端（Tactical Orbment Terminal）** 交互风格，引入深海蓝主色调、金色高光、导力回路同心圆几何纹样，并针对专业打印规范进行了深度 CSS Paged Media 优化（包含 `@page` 边距控制、`break-inside: avoid` 防孤行折断、清晰数据表格与时限预警角标），适用于平板翻阅或高精度双面实体打印。

---

## 🎯 首发标杆成果物：《空之轨迹 the 1st 重制版》

仓库已包含构建完毕的标杆验收成果物：
- **交付路径**：[`dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf`](dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf)
- **页面体量**：52 页 A4 无损矢量排版
- **文件大小**：约 7.91 MB
- **全要素涵盖内容**：
  - **100% 全 BP 达成路径（最高 368 BP）**：序章至终章全主线剧情与短期支线，标明准确截止时限与对话选项。
  - **重制版新增要素**：原野战斗机制与打法、指令连结克制配搭、重制版新增任务（含利贝尔义勇军战术演练等）与二周目 LV+50 继承机制。
  - **四大全收集完备手册**：
    - 《红耀石》全 1–11 卷全小说 +《利贝尔通讯》全期数时限与错失补救地点。
    - 全料理食谱一览表（30+ 道料理），标注主厨推荐、独门料理（大成功）与意外料理。
    - 全钓鱼图鉴与钓点大全，标注推荐钓竿、适配鱼饵、钓点坐标与耀晶石掉落。
  - **全章节 BOSS 详细战术对策**：对方阵容配置、弱点属性分布、关键战术要点与防翻车注意事项。

---

## 🏗 系统架构与管道

全管道由四个独立高内聚的模块构成：

```
[Falcom 数据源 / 网页缓存]
           │
           ▼
   src/scraper.py         (网页抓取与本地持久化缓存)
           │
           ▼
   src/parser.py          (结构化解析与数据校验：任务/书籍/食谱/钓鱼/BOSS)
           │
           ▼
   src/builder.py         (JRPG 战术终端排版构建器 + templates/style.css)
           │
           ▼
   src/pdf_exporter.py    (Headless Chrome Skia 矢量打印引擎)
           │
           ▼
        main.py           (一键 CLI 命令行入口)
           │
           ▼
   dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf (最终标杆交付物)
```

1. **数据抓取 (`src/scraper.py`)**：抓取知名轨迹维基与攻略站点，具备本地幂等缓存。
2. **数据解析 (`src/parser.py`)**：清洗并验证数据模式，确保 BP 算力一致与全要素防漏。
3. **排版构建 (`src/builder.py`)**：装配沉浸式游击士终端界面，生成语义化 HTML。
4. **矢量导出 (`src/pdf_exporter.py`)**：基于 Chrome Headless 模式调用 Skia 打印引擎渲染标准 A4 PDF。
5. **CLI 入口 (`main.py`)**：提供开箱即用的一键生成命令行工具。

---

## 🚀 快速上手与操作指引

### 1. 环境准备

- **Python**：3.10 或更高版本
- **浏览器**：Google Chrome 或 Chromium（支持标准安装路径，或通过环境变量 `CHROME_BIN` 自定义指定）
- **操作系统**：macOS / Linux / Windows

### 2. 一键生成标杆 PDF

在仓库根目录下运行：

```bash
# 生成标杆 PDF 攻略（输出至 dist/ 目录）
python3 main.py
```

### 3. CLI 高级参数

```bash
# 查看帮助说明
python3 main.py --help

# 仅生成 HTML 排版文件（用于浏览器快速调优与预览，不调用 Chrome）
python3 main.py --html-only

# 指定自定义输出 PDF 路径
python3 main.py -o /path/to/custom_guide.pdf
```

---

## 🧪 自动化测试集

运行全量单元测试套件：

```bash
python3 -m unittest discover tests
```

- `test_parser.py`：数据模式验证、任务全要素、BP 累计值及字段容错。
- `test_builder.py`：HTML 生成逻辑、CSS 注入、表格与章节锚点。
- `test_pdf_exporter.py`：Chrome 探测、临时隔离导出及异常路径拦截。
- `test_main.py`：CLI 入口参数解析、`--html-only` 开关与失败路径。

---

## 📝 作者与版权说明

- **作者**：Steve Shi / 轩楝 (`zh-Hans`)
- **版权声明**：《英雄传说：轨迹系列》及其相关所有角色、设定版权均归 Nihon Falcom Corporation（日本ファルコム株式会社）所有。
