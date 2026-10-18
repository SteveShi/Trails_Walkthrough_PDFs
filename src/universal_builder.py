"""
通用轨迹系列全要素攻略 HTML 生成器
支持 12 部作品的标准化数据提取与 A4 Paged Media 网页排版生成
"""

import os
import re
import html
from typing import Dict, List, Any

def clean_tag(s: str) -> str:
    """清理 HTML 标签并保留纯净文字"""
    if not s:
        return ""
    text = re.sub(r'<[^>]+>', ' ', s)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_quest_body(body_html: str) -> str:
    """彻底剥离折叠子块、怪物列表及宝箱列表，提取纯粹的流程推进指引"""
    s = body_html
    patterns = [
        r'<div[^>]*class=[\"\'][^\"\']*(?:collapsible|collapseomatic|boss|treasure|monster|shop|tips)[^\"\']*[\"\'][^>]*>.*?</div>\s*</div>',
        r'<div[^>]*class=[\"\'][^\"\']*(?:collapsible|collapseomatic|boss|treasure|monster|shop|tips)[^\"\']*[\"\'][^>]*>.*?</div>',
        r'<table[^>]*>.*?</table>',
    ]
    prev_len = -1
    while len(s) != prev_len:
        prev_len = len(s)
        for p in patterns:
            s = re.sub(p, ' ', s, flags=re.DOTALL | re.IGNORECASE)
    return s

def format_strategy(strat: str) -> str:
    """格式化 Boss 战术指引，高亮关键属性与战术要点"""
    if not strat:
        return ""
    text = html.escape(strat)
    keywords = [
        "弱点属性", "状态异常", "推荐阵容", "驱动", "打断", "破防",
        "S技", "指令", "回血", "驱动解除", "延迟", "高扬", "连携"
    ]
    for kw in keywords:
        text = re.sub(rf"({kw}[：:])", r"<strong style='color: #c0392b;'>\1</strong>", text)
    return text.replace("\n", "<br>")

def parse_game_notes(nt_html: str) -> Dict[str, List[Any]]:
    """解析四大笔记表格：书籍、料理、钓鱼、其他"""
    tables = re.findall(r'<table[^>]*>(.*?)</table>', nt_html, re.DOTALL)
    books, recipes, fishes, others = [], [], [], []
    
    for idx, t in enumerate(tables):
        ths = [clean_tag(th) for th in re.findall(r'<th[^>]*>(.*?)</th>', t)]
        th_str = ' '.join(ths)
        trs = re.findall(r'<tr[^>]*>(.*?)</tr>', t, re.DOTALL)[1:]
        
        if any(k in th_str for k in ['书籍', '刊物']):
            for tr in trs:
                tds = [clean_tag(td) for td in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)]
                if len(tds) >= 4:
                    books.append({
                        "id": tds[0],
                        "type": tds[1] if len(tds) > 4 else "书籍",
                        "name": tds[2] if len(tds) > 4 else tds[1],
                        "time": tds[3] if len(tds) > 4 else tds[2],
                        "method": tds[4] if len(tds) > 4 else tds[3]
                    })
        elif any(k in th_str for k in ['鱼名', '钓鱼']):
            for tr in trs:
                tds = [clean_tag(td) for td in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)]
                if len(tds) >= 3:
                    fishes.append({
                        "id": tds[0],
                        "name": tds[2] if len(tds) > 3 and not tds[1] else (tds[1] if len(tds) > 2 else tds[0]),
                        "spot": tds[3] if len(tds) > 3 else (tds[2] if len(tds) > 2 else "全域"),
                        "bait": tds[4] if len(tds) > 4 else "专用鱼饵",
                        "drop": tds[5] if len(tds) > 5 else "耀晶石 / 道具"
                    })
        elif any(k in th_str for k in ['料理']):
            for tr in trs:
                tds = [clean_tag(td) for td in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)]
                if len(tds) >= 3:
                    recipes.append({
                        "id": tds[0],
                        "name": tds[2] if len(tds) > 3 and '型' in ths[1] else tds[1],
                        "time": tds[3] if len(tds) > 3 and '型' in ths[1] else (tds[2] if len(tds) > 2 else ""),
                        "method": tds[4] if len(tds) > 4 and '型' in ths[1] else (tds[3] if len(tds) > 3 else "")
                    })
        elif any(k in th_str for k in ['种类', '道具', '电影', '效果']):
            for tr in trs:
                tds = [clean_tag(td) for td in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.DOTALL)]
                if len(tds) >= 4:
                    others.append(tds)

    return {
        "books": books,
        "recipes": recipes,
        "fishes": fishes,
        "others": others
    }

def parse_game_walkthrough(wt_html: str, point_name: str) -> List[Dict[str, Any]]:
    """解析剧情章节流程、主支线任务与 BOSS 战"""
    tabs = re.findall(r'<div[^>]+class=[\"\'][^\"\']*elementor-tab-content[^\"\']*[\"\'][^>]*>(.*?)</div>\s*(?=<div[^>]+class=[\"\'][^\"\']*elementor-tab-content|\Z)', wt_html, re.DOTALL)
    
    raw_chapters = []
    if len(tabs) >= 5:
        for idx, tab in enumerate(tabs):
            h4s = re.findall(r'<h4[^>]*>(.*?)</h4>', tab)
            title = clean_tag(h4s[0]) if h4s else f"第 {idx+1} 阶段"
            if not any(k in title for k in ['开关', '前言', '折叠', '目录']):
                raw_chapters.append((title, tab))
    else:
        chunks = re.split(r'<h4[^>]*>(.*?)</h4>', wt_html)
        for i in range(1, len(chunks), 2):
            t = clean_tag(chunks[i])
            if t and not any(k in t for k in ['开关', '前言', '目录', '折叠']):
                raw_chapters.append((t, chunks[i+1]))

    parsed_chaps = []
    for chap_title, chap_body in raw_chapters:
        # 寻找 h5 或标题块
        h5_chunks = re.split(r'<h5[^>]*>(.*?)</h5>', chap_body)
        quests = []
        bosses = []
        
        # 提取前置指引
        if len(h5_chunks) > 0 and len(clean_tag(h5_chunks[0])) > 20:
            cleaned_intro = clean_quest_body(h5_chunks[0])
            steps = [clean_tag(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', cleaned_intro)]
            if not steps:
                ps = [clean_tag(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', cleaned_intro) if len(clean_tag(p)) > 15]
                steps = ps[:5]
            if steps:
                quests.append({
                    "name": f"{chap_title} · 序盘推进与探索",
                    "type": "main",
                    "bp": f"{point_name}: 主线",
                    "is_missable": True,
                    "is_remake_new": False,
                    "steps": steps[:6]
                })

        for j in range(1, len(h5_chunks), 2):
            q_title = clean_tag(h5_chunks[j])
            q_body = h5_chunks[j+1] if j+1 < len(h5_chunks) else ""
            
            # 区分 Boss 战与常规任务
            if any(k in q_title.lower() for k in ['boss', '强敌', '强制战', '魔兽']):
                m_enemies = re.search(r'对方配置[：:](.*?)(?:<br|</p|$)', q_body)
                enemies = clean_tag(m_enemies.group(1)) if m_enemies else q_title
                m_strat = re.search(r'攻略[：:](.*?)(?:<br|</p|</div>|$)', q_body, re.DOTALL)
                strategy = clean_tag(m_strat.group(1)) if m_strat else "集火驱散驱动，利用 S-Craft 爆发输出并维持异常防护。"
                bosses.append({
                    "name": q_title,
                    "enemies": enemies[:120],
                    "strategy": strategy[:300]
                })
            else:
                # 任务类型判断
                is_side = any(k in q_title for k in ['支线', '委托', '请求', '4spg', '隐藏'])
                is_miss = any(k in q_title for k in ['隐藏', '时限', '超期', '紧急']) or '（+' in q_title or '(+' in q_title
                is_new = any(k in q_title for k in ['新增', '改版', '特别', '教学'])
                
                # 提取点数
                pts_m = re.search(rf'({point_name}[：:]\s*[0-9\+（）\(\)]+)', q_title, re.IGNORECASE)
                bp_str = pts_m.group(1) if pts_m else (f"{point_name}: 支线" if is_side else f"{point_name}: 主线")
                
                cleaned_body = clean_quest_body(q_body)
                steps = [clean_tag(li) for li in re.findall(r'<li[^>]*>(.*?)</li>', cleaned_body)]
                if not steps:
                    ps = [clean_tag(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', cleaned_body) if len(clean_tag(p)) > 15]
                    steps = ps[:5]
                
                if steps or len(q_title) > 3:
                    quests.append({
                        "name": q_title,
                        "type": "side" if is_side else "main",
                        "bp": bp_str,
                        "is_missable": is_miss,
                        "is_remake_new": is_new,
                        "steps": steps[:6]
                    })

        parsed_chaps.append({
            "title": chap_title,
            "quests": quests,
            "bosses": bosses
        })

    return parsed_chaps

def render_game_html(game_cfg: Dict[str, Any], css_content: str) -> str:
    """生成完全自包含的 A4 Paged Media 攻略 HTML"""
    wt_path = game_cfg["wt_cache"]
    nt_path = game_cfg["nt_cache"]
    
    with open(wt_path, "r", encoding="utf-8", errors="ignore") as f:
        wt_html = f.read()
    with open(nt_path, "r", encoding="utf-8", errors="ignore") as f:
        nt_html = f.read()

    notes_data = parse_game_notes(nt_html)
    chapters_data = parse_game_walkthrough(wt_html, game_cfg["point_name"])

    title = html.escape(game_cfg["title"])
    subtitle = html.escape(game_cfg["subtitle"])
    era = html.escape(game_cfg.get("era", "轨迹系列"))
    max_pts = html.escape(game_cfg["max_points"])
    theme_color = game_cfg["theme_color"]
    accent_color = game_cfg["accent_color"]

    # 自定义注入该游戏的主题配色覆盖
    custom_theme_css = f"""
    .cover-page {{ background: linear-gradient(135deg, {theme_color} 0%, #0d1b2a 100%) !important; }}
    .cover-title {{ color: {accent_color} !important; }}
    h1.chapter-header {{ background: {theme_color} !important; border-left: 6px solid {accent_color} !important; }}
    h2.section-header {{ border-left: 5px solid {accent_color} !important; color: {theme_color} !important; }}
    .badge-bp {{ background: {accent_color} !important; color: #111 !important; }}
    table.data-table th {{ background: {theme_color} !important; }}
    .toc-item a:hover {{ color: {accent_color} !important; }}
    """

    parts = [
        "<!DOCTYPE html>",
        "<html lang='zh-CN'>",
        "<head>",
        "<meta charset='UTF-8'>",
        f"<title>{title} 100%全要素白金攻略</title>",
        f"<style>{css_content}\n{custom_theme_css}</style>",
        "</head>",
        "<body>",
        
        # 1. 封面
        "<div class='cover-page'>",
        "<div class='cover-orbment-decoration'>",
        "<div class='orbment-ring ring-1'></div>",
        "<div class='orbment-ring ring-2'></div>",
        "<div class='orbment-ring ring-3'></div>",
        "</div>",
        f"<div class='cover-era-tag'>✦ {era} ✦</div>",
        f"<div class='cover-title'>{title}</div>",
        f"<div class='cover-subtitle'>{subtitle}</div>",
        f"<div class='cover-badge'>【全要素完美达成目标: {max_pts}】</div>",
        "<div class='cover-features-grid'>",
        "<div class='cover-feature-item'><span class='feat-icon'>🛡️</span><strong>全剧情流程</strong><br>主支线100%覆盖</div>",
        "<div class='cover-feature-item'><span class='feat-icon'>📖</span><strong>书籍小说大全</strong><br>时限刊物与兑换</div>",
        "<div class='cover-feature-item'><span class='feat-icon'>🍳</span><strong>料理大成功</strong><br>全食谱独门与意外</div>",
        "<div class='cover-feature-item'><span class='feat-icon'>🎣</span><strong>钓鱼手册图鉴</strong><br>钓点鱼饵耀晶石</div>",
        "</div>",
        "<div class='cover-meta-footer'>",
        "<div>游击士协会 / 特务支援科 / 托尔兹VII班 / 地下万事屋 · 战术导力档案</div>",
        "<div>规范标准: 塞姆利亚通商条约版式 · A4 高清矢量全要素独立攻略本</div>",
        "</div>",
        "</div>",

        # 2. 目录
        "<div class='content toc-page'>",
        "<div class='toc-header'>",
        "<h2 class='toc-title'>游击士 / 战术终端 · 快速索引目录</h2>",
        "<div class='toc-subtitle'>TACTICAL NAVIGATION INDEX &amp; TABLE OF CONTENTS</div>",
        "</div>",
        "<div class='toc-grid'>",
        "<div class='toc-column'>",
        "<div class='toc-section-title'>【主线剧情与章节流程】</div>",
        "<ul class='toc-list'>"
    ]

    for idx, chap in enumerate(chapters_data):
        c_title = html.escape(chap["title"])
        parts.append(f"<li class='toc-item'><a href='#chap-{idx}'>{c_title}</a><span class='toc-jump'>直达 ▸</span></li>")

    parts.extend([
        "</ul>",
        "</div>",
        "<div class='toc-column'>",
        "<div class='toc-section-title'>【核心全收集手册附录】</div>",
        "<ul class='toc-list'>",
        "<li class='toc-item'><a href='#appendix-1'>附录一：全书籍与全刊物收集一览表</a><span class='toc-jump'>直达 ▸</span></li>",
        "<li class='toc-item'><a href='#appendix-2'>附录二：全料理食谱与独门大成功对应表</a><span class='toc-jump'>直达 ▸</span></li>",
        "<li class='toc-item'><a href='#appendix-3'>附录三：全钓鱼图鉴与钓点大全</a><span class='toc-jump'>直达 ▸</span></li>",
        "<li class='toc-item'><a href='#appendix-4'>附录四：强敌对策与二周目通关继承要点</a><span class='toc-jump'>直达 ▸</span></li>",
        "</ul>",
        "<div class='alert-box' style='margin-top: 20px;'>",
        "<div class='alert-title'>⚠️ 完美白金行动防漏红线守则</div>",
        "<ul class='alert-list'>",
        "<li><strong>推进主线前清空委托</strong>：进入红色剧情感叹号前，务必排查布告栏所有时限任务。</li>",
        "<li><strong>每到新城镇排查杂货铺</strong>：第一件事购买最新期杂志与小说，绝大部分书籍一旦错过无法补救。</li>",
        "<li><strong>NPC 积极对话</strong>：关键小说与独门料理常隐藏在非主线 NPC 的二次交谈中。</li>",
        "</ul>",
        "</div>",
        "</div>",
        "</div>",
        "</div>"
    ])

    # 3. 章节详细流程
    for idx, chap in enumerate(chapters_data):
        c_title = html.escape(chap["title"])
        parts.append(f"<div id='chap-{idx}' class='chapter-container'>")
        parts.append(f"<h1 class='chapter-header'>{c_title}</h1>")
        
        # 任务列表
        if chap["quests"]:
            parts.append(f"<h2 class='section-header'>【{c_title} · 委托与推进指引】</h2>")
            for q in chap["quests"]:
                q_name = html.escape(q["name"])
                q_bp = html.escape(q["bp"])
                is_side = q["type"] == "side"
                card_cls = "quest-card side-quest" if is_side else "quest-card"
                
                badges_html = []
                if is_side:
                    badges_html.append("<span class='badge badge-side'>支线委托</span>")
                else:
                    badges_html.append("<span class='badge badge-main'>主线推进</span>")
                if q.get("is_missable"):
                    badges_html.append("<span class='badge badge-missable'>⚠️ 时限/关键</span>")
                if q.get("is_remake_new"):
                    badges_html.append("<span class='badge badge-remake'>✦ 特别/新增</span>")
                badges_html.append(f"<span class='badge badge-bp'>{q_bp}</span>")

                parts.append(f"<div class='{card_cls}'>")
                parts.append(f"<div class='quest-header'><div class='quest-title'>{q_name}</div><div class='quest-badges'>{''.join(badges_html)}</div></div>")
                
                if q.get("steps"):
                    parts.append("<ul class='quest-steps'>")
                    for st in q["steps"]:
                        parts.append(f"<li>{html.escape(st)}</li>")
                    parts.append("</ul>")
                parts.append("</div>")

        # Boss 战术卡
        if chap["bosses"]:
            parts.append(f"<h2 class='section-header'>【{c_title} · 强敌与首领战术对策】</h2>")
            for b in chap["bosses"]:
                b_name = html.escape(b["name"])
                b_enemies = html.escape(b["enemies"])
                b_strat = format_strategy(b["strategy"])
                parts.append("<div class='boss-card'>")
                parts.append(f"<div class='boss-title'>⚔️ {b_name}</div>")
                parts.append(f"<div class='boss-enemies'><strong>敌方阵形:</strong> {b_enemies}</div>")
                parts.append(f"<div class='boss-strategy'><strong>战术打法:</strong> {b_strat}</div>")
                parts.append("</div>")

        parts.append("</div>")

    # 4. 附录一：书籍收集
    parts.append("<div id='appendix-1' class='appendix-container'>")
    parts.append("<h1 class='chapter-header'>附录一：全书籍与全刊物收集一览表</h1>")
    parts.append("<p style='font-size: 9pt; color: #555;'>注：本列表汇总全剧情所有可收集的小说全卷、时限杂志、文献及报刊。请务必在对应章节取得，兑换最终武器之小说切勿提早出售。</p>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th>序号</th><th>类型</th><th>书籍名称</th><th>获得章节/时限</th><th>获得地点与获取方式</th></tr></thead><tbody>")
    
    if notes_data["books"]:
        for b in notes_data["books"]:
            b_id = html.escape(str(b.get("id", "")))
            b_type = html.escape(str(b.get("type", "书籍")))
            b_name = html.escape(str(b.get("name", "")))
            b_time = html.escape(str(b.get("time", "章节内")))
            b_meth = html.escape(str(b.get("method", "杂货铺/NPC交谈")))
            parts.append(f"<tr><td>{b_id}</td><td><span class='badge badge-main'>{b_type}</span></td><td><strong>{b_name}</strong></td><td><span class='badge badge-missable'>{b_time}</span></td><td>{b_meth}</td></tr>")
    else:
        parts.append("<tr><td colspan='5' style='text-align:center;'>本作为集中剧情推进模式，所有小说篇章随主线或书店直接解锁。</td></tr>")
    parts.append("</tbody></table></div>")

    # 5. 附录二：料理食谱收集
    parts.append("<div id='appendix-2' class='appendix-container'>")
    parts.append("<h1 class='chapter-header'>附录二：全料理食谱与独门大成功对应表</h1>")
    parts.append("<p style='font-size: 9pt; color: #555;'>注：料理是恢复 CP、战斗中复活以及赚取差价的关键系统，全料理收集亦为白金奖杯之核心要素。</p>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th>序号</th><th>食谱名称</th><th>获得时间</th><th>获得地点与途径</th></tr></thead><tbody>")
    
    if notes_data["recipes"]:
        for r in notes_data["recipes"]:
            r_id = html.escape(str(r.get("id", "")))
            r_name = html.escape(str(r.get("name", "")))
            r_time = html.escape(str(r.get("time", "章节推进")))
            r_meth = html.escape(str(r.get("method", "餐厅进食 / 宝箱获取")))
            parts.append(f"<tr><td>{r_id}</td><td><strong>{r_name}</strong></td><td><span class='badge badge-bp'>{r_time}</span></td><td>{r_meth}</td></tr>")
    else:
        parts.append("<tr><td colspan='4' style='text-align:center;'>本作餐饮美食系统采用餐厅就餐品尝与 Gourmet Rating 美食品级认证，食谱随品尝自动点亮。</td></tr>")
    parts.append("</tbody></table></div>")

    # 6. 附录三：钓鱼手册
    parts.append("<div id='appendix-3' class='appendix-container'>")
    parts.append("<h1 class='chapter-header'>附录三：全钓鱼图鉴与钓点大全</h1>")
    parts.append("<p style='font-size: 9pt; color: #555;'>注：钓鱼手册全图鉴收集可向钓皇俱乐部或协会换取顶级回路与防具。请在对应章节水域备齐鱼饵钓取。</p>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th>序号</th><th>鱼种图鉴</th><th>推荐钓点</th><th>推荐鱼饵</th><th>钓获奖励与掉落</th></tr></thead><tbody>")
    
    if notes_data["fishes"]:
        for f in notes_data["fishes"]:
            f_id = html.escape(str(f.get("id", "")))
            f_name = html.escape(str(f.get("name", "")))
            f_spot = html.escape(str(f.get("spot", "各水域钓点")))
            f_bait = html.escape(str(f.get("bait", "专用钓饵")))
            f_drop = html.escape(str(f.get("drop", "各类耀晶石块")))
            parts.append(f"<tr><td>#{f_id}</td><td><strong>{f_name}</strong></td><td>{f_spot}</td><td>{f_bait}</td><td>{f_drop}</td></tr>")
    else:
        parts.append("<tr><td colspan='5' style='text-align:center;'>本作特殊户外活动手册（观影/连结/特别品尝）自动计入万事屋档案，全水域钓点与钓皇挑战随任务开启。</td></tr>")
    parts.append("</tbody></table></div>")

    # 7. 附录四：通关继承与终极挑战
    parts.append("<div id='appendix-4' class='appendix-container'>")
    parts.append("<h1 class='chapter-header'>附录四：强敌对策与二周目通关继承要点</h1>")
    parts.append("<div class='overview-card'>")
    parts.append("<div class='overview-card-title'>🏆 白金终点与二周目战术指引</div>")
    parts.append("<div style='font-size: 9.5pt; line-height: 1.6; color: #333;'>")
    parts.append("<p>1. <strong>通关存档继承</strong>：二周目开启时，建议优先继承「角色等级」、「回路与耀晶石」、「手册全记录」及「米拉与资产」，极大加快二周目 Nightmare 难度推进节奏。</p>")
    parts.append("<p>2. <strong>高难模式对策</strong>：面对高难度 BOSS，首要策略为保持全员 S-Break 抢回合打断致命全屏攻击，善用加速魔法（时间加速/时间驱动）与绝对防御（坚韧守护/神圣壁障）。</p>")
    parts.append("<p>3. <strong>隐藏迷宫与黑之史书</strong>：终章后前往隐藏回廊击败极强试炼魔兽，可合成终极导力核心（如七元霸道、霸道、狮子王等），达成 100% 全奖杯白金神作。</p>")
    parts.append("</div></div></div>")

    parts.append("</body></html>")
    return "\n".join(parts)
