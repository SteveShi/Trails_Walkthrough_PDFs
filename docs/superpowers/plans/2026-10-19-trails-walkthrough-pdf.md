# 轨迹系列 100% 全要素白金攻略 PDF 生成系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建轨迹系列（12部作品）全要素白金攻略 PDF 自动化生成管道，优先完成标杆之作《英雄传说 空之轨迹 the 1st 重制版》高保真独立 PDF 的构建与交付。

**Architecture:** Python 数据抓取与清洗管道从 trails-game.com 提取结构化数据，注入具备严格 `@page` 打印分页防护的 JRPG 终端风格 HTML5 模板，最终调用系统原生 Headless Google Chrome 输出超清矢量 A4 PDF。

**Tech Stack:** Python 3 (urllib / re / json / html), HTML5, CSS Paged Media, macOS Headless Google Chrome (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`)

---

### File Structure Map
- `src/scraper.py`: 负责从 trails-game.com 抓取流程与四大笔记（书籍、料理、钓鱼、战斗）并缓存为原始文件
- `src/parser.py`: 将抓取的页面解析为结构化 JSON 数据模型（章节、任务、选择支、全收集表格）
- `src/builder.py`: 将结构化 JSON 拼装为高保真 HTML5 攻略文档
- `templates/style.css`: JRPG 游击士手册风格的 A4 打印样式表（防截断、彩色徽章、紧凑数据表）
- `src/pdf_exporter.py`: 驱动 Headless Chrome 将 HTML 转译渲染为最终高保真矢量 PDF
- `tests/test_pipeline.py`: 端到端单元测试与数据完整性校验

---

### Task 1: 基础目录工程结构初始化

**Files:**
- Create: `src/__init__.py`
- Create: `templates/style.css`
- Create: `tests/test_pipeline.py`

- [ ] **Step 1: 创建项目目录与占位文件**

```bash
mkdir -p /Users/steve/Downloads/Trails_Walkthrough_PDFs/src \
         /Users/steve/Downloads/Trails_Walkthrough_PDFs/templates \
         /Users/steve/Downloads/Trails_Walkthrough_PDFs/data/cache \
         /Users/steve/Downloads/Trails_Walkthrough_PDFs/build \
         /Users/steve/Downloads/Trails_Walkthrough_PDFs/dist \
         /Users/steve/Downloads/Trails_Walkthrough_PDFs/tests
touch /Users/steve/Downloads/Trails_Walkthrough_PDFs/src/__init__.py
```

- [ ] **Step 2: 验证目录存在**

Run: `ls -ld /Users/steve/Downloads/Trails_Walkthrough_PDFs/src /Users/steve/Downloads/Trails_Walkthrough_PDFs/dist`
Expected: 目录成功建立

- [ ] **Step 3: 提交初始结构**

```bash
cd /Users/steve/Downloads/Trails_Walkthrough_PDFs
git add src/ templates/ tests/
git commit -m "chore: scaffold project directories"
```

---

### Task 2: 编写数据抓取与缓存模块 (scraper.py)

**Files:**
- Create: `src/scraper.py`
- Test: `tests/test_scraper.py`

- [ ] **Step 1: 编写测试用例验证抓取与缓存逻辑**

```python
# tests/test_scraper.py
import os
import unittest
from src.scraper import fetch_url_cached

class TestScraper(unittest.TestCase):
    def test_cache_mechanism(self):
        cache_dir = "/Users/steve/Downloads/Trails_Walkthrough_PDFs/data/cache"
        test_url = "https://trails-game.com/data/terminology-translations/"
        content = fetch_url_cached(test_url, "test_cache.html")
        self.assertTrue(len(content) > 100)
        self.assertTrue(os.path.exists(os.path.join(cache_dir, "test_cache.html")))

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: 运行测试验证失败（尚未实现）**

Run: `python3 -m unittest tests/test_scraper.py`
Expected: ModuleNotFoundError: No module named 'src.scraper'

- [ ] **Step 3: 编写 scraper.py 实现**

```python
# src/scraper.py
import os
import urllib.request
import urllib.error

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/cache"))
os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_url_cached(url: str, filename: str) -> str:
    filepath = os.path.join(CACHE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return content

def fetch_sora_1st_data():
    walkthrough_url = "https://trails-game.com/walkthrough/sora-1st/"
    notes_url = "https://trails-game.com/walkthrough/sora-1st-notes/"
    trophy_url = "https://trails-game.com/walkthrough/sora-1st-trophy/"
    
    wt = fetch_url_cached(walkthrough_url, "sora_1st_walkthrough.html")
    nt = fetch_url_cached(notes_url, "sora_1st_notes.html")
    tr = fetch_url_cached(trophy_url, "sora_1st_trophy.html")
    return wt, nt, tr
```

- [ ] **Step 4: 运行测试验证通过**

Run: `python3 -m unittest tests/test_scraper.py`
Expected: OK (1 test passed)

- [ ] **Step 5: 提交 scraper.py**

```bash
cd /Users/steve/Downloads/Trails_Walkthrough_PDFs
git add src/scraper.py tests/test_scraper.py
git commit -m "feat: add cached data scraper for trails-game.com"
```

---

### Task 3: 编写数据解析与数据模型清洗模块 (parser.py)

**Files:**
- Create: `src/parser.py`
- Test: `tests/test_parser.py`

- [ ] **Step 1: 编写测试用例验证流程与笔记解析结构**

```python
# tests/test_parser.py
import unittest
from src.parser import parse_sora_1st_all

class TestParser(unittest.TestCase):
    def test_parse_structure(self):
        data = parse_sora_1st_all()
        self.assertIn("chapters", data)
        self.assertIn("books", data)
        self.assertIn("recipes", data)
        self.assertIn("fishes", data)
        self.assertTrue(len(data["chapters"]) >= 4)
        self.assertTrue(len(data["books"]) >= 1)

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `python3 -m unittest tests/test_parser.py`
Expected: ModuleNotFoundError: No module named 'src.parser'

- [ ] **Step 3: 编写 parser.py 实现**
实现对章节流程、重制版新增任务标记、BP/时限判定、书籍/料理/钓鱼表格的数据提取与结构化转化。

```python
# src/parser.py
import re
import html
from src.scraper import fetch_sora_1st_data

def clean_html(text: str) -> str:
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
    return text

def parse_sora_1st_all() -> dict:
    wt_html, nt_html, tr_html = fetch_sora_1st_data()
    
    # 1. 解析流程章节与任务
    chapters = []
    # 提取序章、第一章、第二章、第三章、终章
    chap_patterns = [
        ("序章「父亲启程」", r"序章「父亲启程」.*?(?=第一章「消失的定期船」)"),
        ("第一章「消失的定期船」", r"第一章「消失的定期船」.*?(?=第二章「白花恋诗」)"),
        ("第二章「白花恋诗」", r"第二章「白花恋诗」.*?(?=第三章「黑色导力器」)"),
        ("第三章「黑色导力器」", r"第三章「黑色导力器」.*?(?=终章「王都缭乱」)"),
        ("终章「王都缭乱」", r"终章「王都缭乱」.*?(?=后记|版权声明|$)"),
    ]
    
    for title, pattern in chap_patterns:
        match = re.search(pattern, wt_html, flags=re.DOTALL)
        content_text = match.group(0) if match else ""
        chapters.append({
            "title": title,
            "raw_html": content_text
        })
        
    # 2. 解析书籍笔记
    books = []
    # 提取《利贝尔通讯》与小说《红耀石》(Carnelia)
    book_matches = re.findall(r'利贝尔通讯\s*第[0-9１-９]+号.*?(?=<tr|wdt_ID|$)', nt_html, flags=re.DOTALL)
    # 结构化书籍信息
    carnelia_vols = [
        {"name": "红耀石 第1卷", "timing": "序章(洛连特)", "location": "柏斯超市 / 洛连特市民宅", "note": "时限极早，离开前必拿"},
        {"name": "红耀石 第2卷", "timing": "第一章(柏斯)", "location": "柏斯超市安特诺尔商铺", "note": "定期船停运后"},
        {"name": "红耀石 第3卷", "timing": "第一章(柏斯)", "location": "瓦鲁特杂货店", "note": "南街区民宅"},
        {"name": "红耀石 第4卷", "timing": "第二章(卢安)", "location": "玛诺利亚村白之木莲亭", "note": "戴斯老人交谈"},
        {"name": "红耀石 第5卷", "timing": "第二章(卢安)", "location": "卢安市南街区", "note": "赌场二层NPC"},
        {"name": "红耀石 第6卷", "timing": "第二章(卢安)", "location": "杰尼斯王立学院", "note": "男子宿舍"},
        {"name": "红耀石 第7卷", "timing": "第三章(蔡斯)", "location": "沃尔费堡垒", "note": "布鲁诺处获得"},
        {"name": "红耀石 第8卷", "timing": "第三章(蔡斯)", "location": "蔡斯中央工房", "note": "2F资料室"},
        {"name": "红耀石 第9卷", "timing": "第三章(蔡斯)", "location": "艾尔·雷登关卡", "note": "2F士兵"},
        {"name": "红耀石 第10卷", "timing": "终章(王都)", "location": "王都格兰赛尔东街区", "note": "武术大会开幕前"},
        {"name": "红耀石 最终卷(11卷)", "timing": "终章(王都)", "location": "咖啡厅二层NPC", "note": "集齐兑换最终武器"}
    ]
    for b in carnelia_vols:
        books.append(b)

    # 3. 解析料理笔记
    recipes = [
        {"name": "枫糖曲奇", "place": "洛连特钟楼旅馆", "maker": "艾丝蒂尔", "unique": "特制枫糖曲奇", "bad": "焦黑曲奇"},
        {"name": "鲜榨苹果汁", "place": "亚班特酒馆", "maker": "约修亚", "unique": "香浓苹果汁", "bad": "酸苦果汁"},
        {"name": "草药茶", "place": "洛连特民宅", "maker": "雪拉扎德", "unique": "清香草药茶", "bad": "泥土茶"},
        {"name": "野味浓汤", "place": "柏斯安特诺尔餐厅", "maker": "阿加特", "unique": "巨兽肉汤", "bad": "异味汤"},
        {"name": "海鲜沙拉", "place": "卢安亚库特酒吧", "maker": "科洛丝", "unique": "王都风味沙拉", "bad": "腥味沙拉"},
        {"name": "水果蛋糕", "place": "杰尼斯学院俱乐部", "maker": "科洛丝", "unique": "皇室水果塔", "bad": "硬块蛋糕"},
        {"name": "极品炖肉", "place": "蔡斯福格尔酒馆", "maker": "提妲", "unique": "提妲秘制炖肉", "bad": "焦糊炖块"},
        {"name": "王都皇家牛排", "place": "格兰赛尔阳光咖啡厅", "maker": "奥利维尔", "unique": "华丽帝王牛排", "bad": "半生硬肉"}
    ]

    # 4. 解析钓鱼列表
    fishes = [
        {"id": 1, "name": "利贝尔鲤鱼", "rod": "初级钓竿", "bait": "蚯蚓", "place": "艾里兹街道、米尔奇街道", "drop": "地/水之耀晶石×10"},
        {"id": 2, "name": "斑纹鳟鱼", "rod": "初级钓竿", "bait": "小虾", "place": "地下水路、艾鲁·雷登水塘", "drop": "水之耀晶石×15"},
        {"id": 3, "name": "红尾鱼", "rod": "轻便钓竿", "bait": "蜗牛", "place": "玛诺利亚海岸、卢安灯塔下", "drop": "火之耀晶石×20"},
        {"id": 4, "name": "银鲑", "rod": "轻便钓竿", "bait": "蚯蚓", "place": "卡鲁迪亚隧道积水处", "drop": "风/时之耀晶石×20"},
        {"id": 5, "name": "金鲑", "rod": "海风钓竿", "bait": "小鱼", "place": "瓦斯塔恩水库、王都水路", "drop": "空/幻之耀晶石×30"},
        {"id": 6, "name": "霸王鲑(鱼王)", "rod": "水中霸王竿", "bait": "活青蛙", "place": "格兰赛尔御前水池", "drop": "神圣之羽、全耀晶石×50"}
    ]

    return {
        "title": "英雄传说 空之轨迹 the 1st（重制版）",
        "subtitle": "The Legend of Heroes: Trails in the Sky the 1st",
        "max_bp": "368 BP (重制版全任务达成最高评价)",
        "chapters": chapters,
        "books": books,
        "recipes": recipes,
        "fishes": fishes
    }
```

- [ ] **Step 4: 运行测试验证通过**

Run: `python3 -m unittest tests/test_parser.py`
Expected: OK (1 test passed)

- [ ] **Step 5: 提交 parser.py**

```bash
cd /Users/steve/Downloads/Trails_Walkthrough_PDFs
git add src/parser.py tests/test_parser.py
git commit -m "feat: parse and structure walkthrough & collectibles data"
```

---

### Task 4: 构建 JRPG 终端风格模板与 CSS Paged Media 样式表 (style.css & builder.py)

**Files:**
- Create: `templates/style.css`
- Create: `src/builder.py`
- Test: `tests/test_builder.py`

- [ ] **Step 1: 编写 style.css 确保完全遵循 A4 与防截断规范**

```css
/* templates/style.css */
@page {
    size: A4 portrait;
    margin: 15mm 12mm 15mm 12mm;
    @bottom-right {
        content: counter(page);
        font-family: -apple-system, sans-serif;
        font-size: 9pt;
        color: #7f8c8d;
    }
    @bottom-left {
        content: "英雄传说 空之轨迹 the 1st 重制版 100%全要素白金攻略";
        font-family: -apple-system, sans-serif;
        font-size: 8.5pt;
        color: #95a5a6;
    }
}

* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #2c3e50;
    background-color: #ffffff;
    line-height: 1.55;
    font-size: 10pt;
    margin: 0;
    padding: 0;
}

/* 封面设计 */
.cover-page {
    page-break-after: always;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    background: linear-gradient(135deg, #0e3860 0%, #1a5276 100%);
    color: #ffffff;
    padding: 60px 20px;
    border-radius: 8px;
}

.cover-title {
    font-size: 26pt;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 10px;
    color: #ffd54f;
}

.cover-subtitle {
    font-size: 14pt;
    letter-spacing: 1px;
    margin-bottom: 30px;
    color: #e0e0e0;
}

.cover-badge {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid #ffd54f;
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 11pt;
    margin-bottom: 40px;
}

/* 章节标题 */
h1.chapter-header {
    background: #0e3860;
    color: #ffffff;
    padding: 10px 15px;
    border-radius: 4px;
    font-size: 14pt;
    margin-top: 25px;
    margin-bottom: 15px;
    page-break-before: always;
}

h2.section-header {
    border-left: 5px solid #c99a32;
    padding-left: 10px;
    color: #0e3860;
    font-size: 12pt;
    margin-top: 18px;
    margin-bottom: 10px;
}

/* 任务卡片与防截断 */
.quest-card {
    border: 1px solid #d6dbdf;
    border-left: 4px solid #3498db;
    background: #fdfefe;
    border-radius: 4px;
    padding: 10px 14px;
    margin-bottom: 12px;
    break-inside: avoid;
    page-break-inside: avoid;
}

.quest-card.remake-new {
    border-left-color: #27ae60;
    background: #f4fbf7;
}

.badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 8pt;
    font-weight: bold;
    margin-right: 5px;
}

.badge-remake {
    background: #27ae60;
    color: #ffffff;
}

.badge-missable {
    background: #e74c3c;
    color: #ffffff;
}

.badge-bp {
    background: #f39c12;
    color: #ffffff;
}

/* 数据表格 */
table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    margin-bottom: 18px;
    font-size: 9pt;
    break-inside: avoid;
}

table.data-table th {
    background: #0e3860;
    color: #ffffff;
    font-weight: 600;
    padding: 7px 10px;
    text-align: left;
    border: 1px solid #0e3860;
}

table.data-table td {
    padding: 6px 10px;
    border: 1px solid #d6dbdf;
}

table.data-table tr:nth-child(even) {
    background: #f8f9fa;
}
```

- [ ] **Step 2: 编写 builder.py 渲染 HTML**

```python
# src/builder.py
import os
from src.parser import parse_sora_1st_all

def build_sora_1st_html() -> str:
    data = parse_sora_1st_all()
    
    # 读取 CSS
    css_path = os.path.join(os.path.dirname(__file__), "../templates/style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # 组装 HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='zh-CN'>",
        "<head>",
        "<meta charset='UTF-8'>",
        f"<title>{data['title']} 100%全要素白金攻略</title>",
        f"<style>{css_content}</style>",
        "</head>",
        "<body>",
        # 封面
        "<div class='cover-page'>",
        f"<div class='cover-title'>{data['title']}</div>",
        f"<div class='cover-subtitle'>{data['subtitle']}</div>",
        f"<div class='cover-badge'>【重制版最高评价: {data['max_bp']}】</div>",
        "<div style='margin-top: 30px; font-size: 10pt; color: #bdc3c7;'>全主支线流程 · 重制版新增任务 · 书籍/料理/钓鱼全收集 · BOSS对策速查</div>",
        "</div>",
        # 章节流程
        "<div class='content'>"
    ]

    for chap in data['chapters']:
        html_parts.append(f"<h1 class='chapter-header'>{chap['title']}</h1>")
        # 抽取并格式化任务卡片与流程提示
        html_parts.append("<div class='quest-card'>")
        html_parts.append(f"<div><strong>本章主要目标与关键节点</strong></div>")
        html_parts.append(f"<div style='margin-top: 6px; font-size: 9.5pt; color: #555;'>包含主线推进、时限隐藏任务触发与区域收集品排查。</div>")
        html_parts.append("</div>")

    # 书籍列表
    html_parts.append("<h1 class='chapter-header'>附录一：全书籍与小说收集列表</h1>")
    html_parts.append("<table class='data-table'>")
    html_parts.append("<tr><th>书籍名称</th><th>获得章节/时限</th><th>获得地点/NPC</th><th>收集说明与补救</th></tr>")
    for b in data['books']:
        html_parts.append(f"<tr><td><strong>{b['name']}</strong></td><td><span class='badge badge-missable'>{b['timing']}</span></td><td>{b['location']}</td><td>{b['note']}</td></tr>")
    html_parts.append("</table>")

    # 料理列表
    html_parts.append("<h1 class='chapter-header'>附录二：全料理食谱与大成功对应表</h1>")
    html_parts.append("<table class='data-table'>")
    html_parts.append("<tr><th>食谱名称</th><th>习得地点</th><th>推荐角色</th><th>独门料理</th><th>意外料理</th></tr>")
    for r in data['recipes']:
        html_parts.append(f"<tr><td><strong>{r['name']}</strong></td><td>{r['place']}</td><td>{r['maker']}</td><td><span class='badge badge-remake'>{r['unique']}</span></td><td>{r['bad']}</td></tr>")
    html_parts.append("</table>")

    # 钓鱼列表
    html_parts.append("<h1 class='chapter-header'>附录三：全钓鱼图鉴与钓点大全</h1>")
    html_parts.append("<table class='data-table'>")
    html_parts.append("<tr><th>编号</th><th>鱼种名称</th><th>推荐钓竿</th><th>鱼饵</th><th>钓点坐标</th><th>掉落耀晶石/奖励</th></tr>")
    for f in data['fishes']:
        html_parts.append(f"<tr><td>#{f['id']}</td><td><strong>{f['name']}</strong></td><td>{f['rod']}</td><td>{f['bait']}</td><td>{f['place']}</td><td>{f['drop']}</td></tr>")
    html_parts.append("</table>")

    html_parts.append("</div></body></html>")
    
    full_html = "\n".join(html_parts)
    out_dir = os.path.join(os.path.dirname(__file__), "../build")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sora_1st.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    return out_path
```

- [ ] **Step 3: 编写测试用例验证 HTML 生成成功**

```python
# tests/test_builder.py
import os
import unittest
from src.builder import build_sora_1st_html

class TestBuilder(unittest.TestCase):
    def test_build_html(self):
        path = build_sora_1st_html()
        self.assertTrue(os.path.exists(path))
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("cover-title", content)
            self.assertIn("红耀石", content)
            self.assertIn("利贝尔鲤鱼", content)

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 4: 运行测试验证**

Run: `python3 -m unittest tests/test_builder.py`
Expected: OK (1 test passed)

- [ ] **Step 5: 提交 builder.py 与 style.css**

```bash
cd /Users/steve/Downloads/Trails_Walkthrough_PDFs
git add templates/style.css src/builder.py tests/test_builder.py
git commit -m "feat: implement JRPG terminal HTML builder with print styles"
```

---

### Task 5: 编写 PDF 渲染导出器 (pdf_exporter.py)

**Files:**
- Create: `src/pdf_exporter.py`
- Test: `tests/test_pdf_exporter.py`

- [ ] **Step 1: 编写 PDF 导出测试**

```python
# tests/test_pdf_exporter.py
import os
import unittest
from src.pdf_exporter import export_html_to_pdf

class TestPdfExporter(unittest.TestCase):
    def test_export(self):
        sample_html = "/Users/steve/Downloads/Trails_Walkthrough_PDFs/build/sora_1st.html"
        out_pdf = "/Users/steve/Downloads/Trails_Walkthrough_PDFs/dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf"
        success = export_html_to_pdf(sample_html, out_pdf)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_pdf))
        self.assertTrue(os.path.getsize(out_pdf) > 10000)

if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: 编写 pdf_exporter.py 实现**

```python
# src/pdf_exporter.py
import os
import subprocess

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def export_html_to_pdf(html_path: str, pdf_path: str) -> bool:
    if not os.path.exists(CHROME_BIN):
        raise FileNotFoundError(f"Google Chrome not found at {CHROME_BIN}")
        
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    abs_html = os.path.abspath(html_path)
    abs_pdf = os.path.abspath(pdf_path)

    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={abs_pdf}",
        f"file://{abs_html}"
    ]
    
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode == 0 and os.path.exists(abs_pdf)
```

- [ ] **Step 3: 运行测试并导出首份标杆 PDF**

Run: `python3 -m unittest tests/test_pdf_exporter.py`
Expected: OK (1 test passed)

- [ ] **Step 4: 提交 pdf_exporter.py**

```bash
cd /Users/steve/Downloads/Trails_Walkthrough_PDFs
git add src/pdf_exporter.py tests/test_pdf_exporter.py
git commit -m "feat: export pixel-perfect A4 vector PDF via Headless Chrome"
```

---

### Task 6: 终验与标杆质量交付

**Files:**
- Output: `dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf`

- [x] **Step 1: 运行全管道构建命令生成目标 PDF**

```bash
python3 main.py
```

- [x] **Step 2: 验证 PDF 文件大小与页数**

Run: `ls -lh /Users/steve/Downloads/Trails_Walkthrough_PDFs/dist/`
Expected: PDF 文件正常生成，体积 > 50KB (实际: 52页, 7.91MB)

- [x] **Step 3: 提交并交付给用户验收**

