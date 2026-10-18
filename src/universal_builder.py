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

def clean_inline_html(text: str) -> str:
    """清理多余媒体与样式标签，保留文字和换行"""
    if not text:
        return ""
    # 去除 script/style/comment
    text = re.sub(r'<(?:script|style)[^>]*>.*?</(?:script|style)>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # 去除图片和外部视频链接提示
    text = re.sub(r'<picture>.*?</picture>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<img[^>]*>', '', text, flags=re.IGNORECASE)
    # 替换 br 和 p 为换行
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
    # 去除所有剩余标签
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    # 规范每行空格
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def format_strategy_text(text: str) -> str:
    """格式化战术与流程文本，高亮关键选择支、加分项及战斗要素"""
    if not text:
        return ""
    escaped = html.escape(text)
    
    # 高亮选择支与判定结果
    escaped = re.sub(r'(【[^】]+】)', r"<span class='choice-highlight'>\1</span>", escaped)
    escaped = re.sub(r'(——(?:DP|AP|BP|SP)\+[0-9]+)', r"<span class='bonus-point-highlight'>\1</span>", escaped)
    
    # 高亮战斗战术关键字
    keywords = [
        "弱点属性", "状态异常", "推荐阵容", "驱动", "打断", "破防",
        "S技", "指令", "回血", "驱动解除", "延迟", "高扬", "连携", "突袭", "情报分析"
    ]
    for kw in keywords:
        escaped = re.sub(rf"({kw}[：:])", r"<strong style='color: #c0392b;'>\1</strong>", escaped)
        
    return escaped.replace("\n", "<br>")

def parse_border_element(block_html: str, point_name: str) -> Dict[str, Any]:
    """解析一个 border 容器块（任务、宝箱、魔兽、Boss、贴士）"""
    cls_m = re.search(r'class=[\"\']([^\"\']+)[\"\']', block_html)
    cls_str = cls_m.group(1) if cls_m else ""
    
    # 提取标题
    title_m = re.search(r'title=[\"\']([^\"\']+)[\"\']', block_html)
    if not title_m:
        title_m = re.search(r'<h[45][^>]*>(.*?)</h[45]>', block_html)
    raw_title = title_m.group(1) if title_m else ""
    title = clean_tag(raw_title)
    
    # 提取点数 (如 DP：3, AP：4, SP：4)
    pts_m = re.search(r'(?:DP|AP|BP|SP)[：:]\s*([0-9\+]+)', block_html)
    pts_str = f"{point_name}: +{pts_m.group(1)}" if pts_m else ""
    
    clean_text = clean_inline_html(block_html)
    lines = clean_text.split('\n')
    # 如果标题在正文第一行，去除避免重复
    if lines and title and title in lines[0]:
        lines = lines[1:]
        
    # 判断具体类型
    if 'main_quest' in cls_str:
        el_type = "main_quest"
    elif 'hidden_quest' in cls_str:
        el_type = "hidden_quest"
    elif 'sub_quest' in cls_str or 'quest' in cls_str:
        el_type = "sub_quest"
    elif 'boss' in cls_str or any(k in title.lower() for k in ['boss', '强敌', '魔兽', '强制战']):
        el_type = "boss"
    elif 'box' in cls_str or '宝箱' in title:
        el_type = "treasure"
    elif 'monster' in cls_str or '战斗手册' in title:
        el_type = "monster"
    elif 'tips' in cls_str or '料理' in title:
        el_type = "tips"
    else:
        el_type = "general"
        
    return {
        "type": el_type,
        "title": title or "要点指引",
        "points": pts_str,
        "lines": lines,
        "raw_text": '\n'.join(lines)
    }

def parse_game_notes(nt_html: str) -> Dict[str, List[Any]]:
    """解析四大笔记表格：书籍、料理、钓鱼、其他"""
    tables = re.findall(r'<table[^>]*>(.*?)</table>', nt_html, re.DOTALL)
    books, recipes, fishes, others = [], [], [], []
    
    for t in tables:
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
                        "spot": tds[3] if len(tds) > 3 else (tds[2] if len(tds) > 2 else "全域水域"),
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
    """解析全剧情章节、主支线任务、探索流程、宝箱与 BOSS 战"""
    # 1. 识别手风琴容器
    acc_items = re.findall(
        r'<div[^>]*class=[\"\'][^\"\']*elementor-accordion-item[^\"\']*[\"\'][^>]*>(.*?)</div>\s*(?=<div[^>]*class=[\"\'][^\"\']*elementor-accordion-item|\Z)',
        wt_html,
        re.DOTALL
    )
    
    raw_chapters = []
    if len(acc_items) >= 4:
        for item in acc_items:
            m_t = re.search(r'class=[\"\'][^\"\']*elementor-accordion-title[^\"\']*[\"\'][^>]*>(.*?)</a>', item)
            m_c = re.search(r'class=[\"\'][^\"\']*elementor-tab-content[^\"\']*[\"\'][^>]*>(.*)', item, re.DOTALL)
            if m_t and m_c:
                t = clean_tag(m_t.group(1))
                c = m_c.group(1)
                # 过滤前置须知/非章节
                if not any(k in t for k in ['前言', '写在开头', '须知', '注意事项', '继承特典', '前作继承', '开关', '目录', '不再更新', '请使用']):
                    raw_chapters.append((t, c))
    else:
        # 界之轨迹等采用 details 容器
        det_items = re.findall(r'<details[^>]*class=[\"\'][^\"\']*e-n-accordion-item[^\"\']*[\"\'][^>]*>(.*?)</details>', wt_html, re.DOTALL)
        if len(det_items) >= 3:
            for item in det_items:
                m_t = re.search(r'<div class=[\"\']e-n-accordion-item-title-text[\"\']>(.*?)</div>', item)
                if not m_t:
                    m_t = re.search(r'<summary[^>]*>(.*?)</summary>', item)
                if m_t:
                    t = clean_tag(m_t.group(1))
                    if not any(k in t for k in ['前言', '写在开头', '须知', '注意事项', '继承特典', '前作继承', '开关', '目录', 'LGC相关']):
                        raw_chapters.append((t, item))
        else:
            # 兜底按 h4 分割
            chunks = re.split(r'<h4[^>]*>(.*?)</h4>', wt_html)
            for i in range(1, len(chunks), 2):
                t = clean_tag(chunks[i])
                if t and not any(k in t for k in ['前言', '写在开头', '须知', '注意事项', '继承特典', '开关', '目录', '不再更新']):
                    raw_chapters.append((t, chunks[i+1]))

    parsed_chaps = []
    
    for chap_title, chap_body in raw_chapters:
        elements = []
        
        # 检查是否包含带类名 border 块
        has_borders = bool(re.search(r'class=[\"\'][^\"\']*(?:quest_border|box_border|monster_border|boss_border|tips_border)[^\"\']*[\"\']', chap_body))
        
        if has_borders:
            border_pattern = r'(<div[^>]*class=[\"\'][^\"\']*(?:quest_border|box_border|monster_border|boss_border|tips_border)[^\"\']*[\"\'][^>]*>.*?</div>\s*</div>)'
            tokens = re.split(border_pattern, chap_body, flags=re.DOTALL)
            
            for tok in tokens:
                tok = tok.strip()
                if not tok:
                    continue
                if "border" in tok[:100]:
                    elements.append(parse_border_element(tok, point_name))
                else:
                    # 普通文本段落（探索与剧情推进）
                    # 检查是否有时间/阶段标签
                    m_div = re.findall(r'<div class=[\"\']text-divider[\"\']><span>(.*?)</span></div>', tok)
                    if m_div:
                        for div_txt in m_div:
                            elements.append({
                                "type": "timeline_divider",
                                "title": f"【日程阶段: {clean_tag(div_txt)}】",
                                "lines": []
                            })
                    
                    c_txt = clean_inline_html(tok)
                    # 过滤纯 UI 开关
                    if len(c_txt) > 5 and not any(k in c_txt for k in ['内部可展开框开关', '不再更新', '请使用改版']):
                        lines = [l for l in c_txt.split('\n') if l.strip()]
                        # 识别日程开头
                        if lines and any(d in lines[0] for d in ['第1天', '第2天', '第3天', '第4天', '演习', '白天', '夜晚', '自由行动']):
                            elements.append({
                                "type": "timeline_divider",
                                "title": f"【日程: {lines[0]}】",
                                "lines": []
                            })
                            lines = lines[1:]
                        if lines:
                            elements.append({
                                "type": "exploration",
                                "title": "城镇与迷宫探索推进",
                                "points": "",
                                "lines": lines,
                                "raw_text": '\n'.join(lines)
                            })
        else:
            # 无 border 的页面（如界之轨迹），按 h4 / h5 解析
            h4_chunks = re.split(r'(<h4[^>]*>.*?</h4>)', chap_body)
            for idx in range(1, len(h4_chunks), 2):
                h4_t = clean_tag(h4_chunks[idx])
                h4_b = h4_chunks[idx+1] if idx+1 < len(h4_chunks) else ""
                if any(k in h4_t for k in ['内部可展开框开关', '前言']):
                    continue
                
                # 每个 h4 作为一个阶段
                elements.append({
                    "type": "timeline_divider",
                    "title": f"【阶段探索: {h4_t}】",
                    "lines": []
                })
                
                # 检查 h4_b 内部的 h5 细分子节
                h5_chunks = re.split(r'(<h5[^>]*>.*?</h5>)', h4_b)
                if len(h5_chunks) > 1:
                    for j in range(1, len(h5_chunks), 2):
                        h5_t = clean_tag(h5_chunks[j])
                        h5_b = h5_chunks[j+1] if j+1 < len(h5_chunks) else ""
                        c_txt = clean_inline_html(h5_b)
                        lines = [l for l in c_txt.split('\n') if l.strip()]
                        
                        is_boss = any(k in h5_t.lower() for k in ['boss', '强敌', '战斗'])
                        is_box = '宝箱' in h5_t
                        is_side = any(k in h5_t for k in ['任务', '委托', '4spg'])
                        
                        el_type = "boss" if is_boss else ("treasure" if is_box else ("sub_quest" if is_side else "exploration"))
                        elements.append({
                            "type": el_type,
                            "title": h5_t,
                            "points": f"{point_name}: 达成" if is_side else "",
                            "lines": lines,
                            "raw_text": c_txt
                        })
                else:
                    c_txt = clean_inline_html(h4_b)
                    lines = [l for l in c_txt.split('\n') if l.strip()]
                    if lines:
                        elements.append({
                            "type": "exploration",
                            "title": h4_t,
                            "points": "",
                            "lines": lines,
                            "raw_text": c_txt
                        })
                        
        parsed_chaps.append({
            "title": chap_title,
            "elements": elements
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
    org_name = html.escape(game_cfg.get("org_name", "战术导力终端档案"))
    max_pts = html.escape(game_cfg["max_points"])
    theme_color = game_cfg["theme_color"]
    accent_color = game_cfg["accent_color"]

    # 自定义注入该游戏的主题配色与精准的 @page 页眉页脚覆盖
    custom_theme_css = f"""
    @page {{
        size: A4 portrait;
        margin: 16mm 14mm 16mm 14mm;
        @top-left {{
            content: "{org_name} · 战术终端文档";
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 8pt;
            color: #7f8c8d;
            border-bottom: 0.5pt solid {accent_color};
            padding-bottom: 2mm;
        }}
        @top-right {{
            content: "{title} 100%全要素详细攻略";
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 8pt;
            color: #7f8c8d;
            border-bottom: 0.5pt solid {accent_color};
            padding-bottom: 2mm;
        }}
        @bottom-left {{
            content: "Falcom 经典全要素 · 全主支线 / 全书籍 / 全料理 / 全钓鱼 / 二周目要素";
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 8pt;
            color: #95a5a6;
            border-top: 0.5pt solid #e0e0e0;
            padding-top: 2mm;
        }}
        @bottom-right {{
            content: "Page " counter(page);
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            font-size: 8.5pt;
            font-weight: 600;
            color: {theme_color};
            border-top: 0.5pt solid #e0e0e0;
            padding-top: 2mm;
        }}
    }}
    @page :first {{
        margin: 0;
        @top-left {{ content: none; }}
        @top-right {{ content: none; }}
        @bottom-left {{ content: none; }}
        @bottom-right {{ content: none; }}
    }}
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
        f"<div>{org_name} · 战术导力全档案</div>",
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
        "<li><strong>推进主线前清空委托</strong>：进入红色剧情感叹号前，务必排查终端或布告栏所有时限任务。</li>",
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
        
        elements = chap["elements"]
        for el in elements:
            el_type = el["type"]
            el_title = html.escape(el["title"])
            el_pts = html.escape(el.get("points", ""))
            lines = el.get("lines", [])
            
            if el_type == "timeline_divider":
                parts.append(f"<div class='timeline-divider'>📅 {el_title}</div>")
                
            elif el_type in ["main_quest", "sub_quest", "hidden_quest"]:
                is_main = el_type == "main_quest"
                is_hidden = el_type == "hidden_quest"
                card_cls = "quest-card quest-main" if is_main else ("quest-card quest-missable" if is_hidden else "quest-card quest-side")
                
                badge_type = "<span class='badge badge-main'>主线推进</span>" if is_main else ("<span class='badge badge-missable'>⚠️ 隐藏任务</span>" if is_hidden else "<span class='badge badge-side'>支线委托</span>")
                badge_pts = f"<span class='badge badge-bp'>{el_pts}</span>" if el_pts else ""
                
                parts.append(f"<div class='{card_cls}'>")
                parts.append(f"<div class='quest-header'><div class='quest-title'>🛡️ {el_title}</div><div class='quest-badges'>{badge_type}{badge_pts}</div></div>")
                if lines:
                    parts.append("<ul class='quest-steps'>")
                    for line in lines:
                        fmt_line = format_strategy_text(line)
                        parts.append(f"<li class='quest-step-item'>{fmt_line}</li>")
                    parts.append("</ul>")
                parts.append("</div>")
                
            elif el_type == "boss":
                parts.append("<div class='boss-card'>")
                parts.append(f"<div class='boss-header'><div class='boss-title'>⚔️ {el_title}</div></div>")
                if lines:
                    parts.append("<div class='boss-strategy'>")
                    for line in lines:
                        fmt_line = format_strategy_text(line)
                        parts.append(f"<div>{fmt_line}</div>")
                    parts.append("</div>")
                parts.append("</div>")
                
            elif el_type == "treasure":
                parts.append("<div class='treasure-card'>")
                parts.append(f"<div class='treasure-header'><span>📦 {el_title}</span></div>")
                if lines:
                    parts.append("<ol class='treasure-list'>")
                    for line in lines:
                        parts.append(f"<li>{html.escape(line)}</li>")
                    parts.append("</ol>")
                parts.append("</div>")
                
            elif el_type == "monster":
                parts.append("<div class='monster-card'>")
                parts.append(f"<div class='monster-header'><span>👾 {el_title}</span></div>")
                if lines:
                    parts.append("<ul class='monster-tags'>")
                    for line in lines:
                        # 拆分魔兽名称
                        monsters = re.split(r'[\s、，,]+', line)
                        for m in monsters:
                            m_clean = m.strip()
                            if m_clean:
                                parts.append(f"<li class='monster-tag'>{html.escape(m_clean)}</li>")
                    parts.append("</ul>")
                parts.append("</div>")
                
            elif el_type == "tips":
                parts.append("<div class='tips-card'>")
                parts.append(f"<div class='tips-header'>💡 {el_title}</div>")
                if lines:
                    for line in lines:
                        parts.append(f"<div>{format_strategy_text(line)}</div>")
                parts.append("</div>")
                
            elif el_type == "exploration":
                parts.append("<div class='exploration-card'>")
                parts.append(f"<div class='exploration-header'><span>🧭 {el_title}</span></div>")
                if lines:
                    parts.append("<ul class='exploration-steps'>")
                    for line in lines:
                        fmt_line = format_strategy_text(line)
                        parts.append(f"<li class='exploration-step-item'>{fmt_line}</li>")
                    parts.append("</ul>")
                parts.append("</div>")

        parts.append("</div>")

    # 4. 附录一：书籍收集
    parts.append("<div id='appendix-1' class='appendix-container'>")
    parts.append("<h1 class='chapter-header'>附录一：全书籍与全刊物收集一览表</h1>")
    parts.append("<p class='appendix-desc'>注：本列表汇总全剧情所有可收集的小说全卷、时限杂志、文献及报刊。请务必在对应章节取得，兑换最终武器之小说切勿提早出售。</p>")
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
    parts.append("<p class='appendix-desc'>注：料理是恢复 CP、战斗中复活以及赚取差价的关键系统，全料理收集亦为白金奖杯之核心要素。</p>")
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
    parts.append("<p class='appendix-desc'>注：钓鱼手册全图鉴收集可向钓皇俱乐部或协会换取顶级回路与防具。请在对应章节水域备齐鱼饵钓取。</p>")
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
    parts.append("<p>3. <strong>隐藏迷宫与终极挑战</strong>：终章后前往隐藏回廊击败极强试炼魔兽，可合成终极导力核心（如七元霸道、霸道、狮子王等），达成 100% 全奖杯白金神作。</p>")
    parts.append("</div></div></div>")

    parts.append("</body></html>")
    return "\n".join(parts)
