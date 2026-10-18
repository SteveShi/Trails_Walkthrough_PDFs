import os
import re
import html
from src.parser import parse_sora_1st_all

def format_strategy(strat: str) -> str:
    """格式化 Boss 战术策略文本，增强排版可读性"""
    if not strat:
        return "常规战斗，注意保持队伍血量并以克制属性魔法攻击。"
    s = html.escape(strat)
    s = re.sub(r'(建议打法\s*[:：])', r'<br><strong>【建议打法】</strong> ', s)
    s = re.sub(r'(注意事项\s*[:：])', r'<br><strong>【注意事项】</strong> ', s)
    s = re.sub(r'(弱点属性\s*[:：])', r'<br><strong>【弱点属性】</strong> ', s)
    s = re.sub(r'(对方配置\s*[:：])', r'<strong>【对方配置】</strong> ', s)
    s = re.sub(r'\n+', '<br>', s)
    if s.startswith('<br>'):
        s = s[4:]
    return s

def build_sora_1st_html(output_path: str = None) -> str:
    """构建《空之轨迹 the 1st 重制版》JRPG 终端风格完整全要素白金攻略 HTML"""
    data = parse_sora_1st_all()

    # 读取样式表
    css_path = os.path.join(os.path.dirname(__file__), "../templates/style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # 确定输出路径
    if not output_path:
        out_dir = os.path.join(os.path.dirname(__file__), "../build")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "sora_1st.html")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append("<html lang='zh-CN'>")
    parts.append("<head>")
    parts.append("<meta charset='UTF-8'>")
    parts.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    parts.append(f"<title>{data['title']} 100%全要素白金攻略</title>")
    parts.append("<style>")
    parts.append(css_content)
    parts.append("</style>")
    parts.append("</head>")
    parts.append("<body>")

    # 1. 封面设计
    parts.append("<div class='cover-page'>")
    parts.append("<div class='cover-orbment-decoration'></div>")
    parts.append("<div class='cover-orbment-inner'></div>")
    parts.append("<div class='cover-header-group'>")
    parts.append("<div class='cover-tagline'>Bracer Guild Liberl Branch · Tactical Orbment Terminal</div>")
    parts.append(f"<div class='cover-title'>{data['title']}</div>")
    parts.append(f"<div class='cover-subtitle'>{data['subtitle']}</div>")
    parts.append(f"<div class='cover-badge'>【最高评价: {data['max_bp']}】</div>")
    parts.append("</div>")

    parts.append("<div class='cover-feature-grid'>")
    parts.append("<div class='cover-feature-item'><strong>100% 白金流程</strong>全主支线任务 / 时限与隐藏BP全解析</div>")
    parts.append("<div class='cover-feature-item'><strong>重制版新特性</strong>原野战斗 / 新增支线 / 指令连结对策</div>")
    parts.append("<div class='cover-feature-item'><strong>四大全收集手册</strong>全书籍小说 / 全料理食谱 / 全钓点图鉴</div>")
    parts.append("<div class='cover-feature-item'><strong>二周目终极挑战</strong>继承机制 / LV+50模式 / 隐藏回路</div>")
    parts.append("</div>")

    parts.append("<div class='cover-footer-meta'>")
    parts.append("游击士协会·利贝尔支部 编制 | 适用平台：PlayStation 5 / Nintendo Switch / Steam (PC)<br>")
    parts.append("严格遵循 A4 竖版 Paged Media 规范 · 包含全章节 368 最大 BP 达成路径 · 防漏检对照手册")
    parts.append("</div>")
    parts.append("</div>")  # end cover-page

    # 2. 目录与系统概览
    parts.append("<div class='overview-section' id='toc'>")
    parts.append("<div class='table-of-contents'>")
    parts.append("<div class='toc-header'>")
    parts.append("<h2 class='toc-title'>📱 游击士终端系统导航目录</h2>")
    parts.append("<span style='font-size: 8.5pt; color: #7f8c8d; font-weight: 600;'>TACTICAL TERMINAL DIRECTORY</span>")
    parts.append("</div>")

    parts.append("<ul class='toc-grid'>")
    for idx, chap in enumerate(data['chapters']):
        parts.append(f"<li class='toc-item'><a href='#chap-{idx}'>{chap['title']}</a><span>P.{idx + 2}</span></li>")
    parts.append("<li class='toc-item'><a href='#appendix-1'>附录一：全书籍与小说收集列表 (全33卷)</a><span>P.8</span></li>")
    parts.append("<li class='toc-item'><a href='#appendix-2'>附录二：全料理食谱与大成功对应表 (全17道)</a><span>P.9</span></li>")
    parts.append("<li class='toc-item'><a href='#appendix-3'>附录三：全钓鱼图鉴与钓点大全 (全10种)</a><span>P.10</span></li>")
    parts.append("<li class='toc-item'><a href='#appendix-4'>附录四：二周目通关继承与终极魔兽挑战</a><span>P.11</span></li>")
    parts.append("</ul>")
    parts.append("</div>")  # end table-of-contents

    # 终端操作准则与时限警示
    parts.append("<div class='alert-box'>")
    parts.append("<strong>⚠️ 游击士行动规范与防漏红线准则：</strong><br>")
    parts.append("1. <strong>时限任务红线</strong>：标有 <span class='badge badge-missable'>时限注意</span> 的委托、书籍与对话，一旦推动关键主线将永久关闭失效，必须在推进主线剧情前优先结算完成。<br>")
    parts.append("2. <strong>BP 完美达成</strong>：本作最高评价要求累计 368 BP，主支线流程中的所有关键推理与询问分支，请务必严格参照本指南标出的最佳选项。<br>")
    parts.append("3. <strong>重制版原野机制</strong>：探索地图时建议先利用角色的原野蓄力攻击击晕敌人，再按下指令战斗按键切入，可获得 100% 先手优势与连结攻击加成。<br>")
    parts.append("4. <strong>最强终极武器</strong>：集齐全部 11 卷《红耀石》后，可在终章武术大会期间前往王都格兰赛尔东街区咖啡厅二层兑换艾丝蒂尔最强武器【太极棍】或约修亚最强武器【黑羽之鸦】。")
    parts.append("</div>")
    parts.append("</div>")  # end overview-section

    # 3. 详细章节全流程
    for idx, chap in enumerate(data['chapters']):
        parts.append(f"<div class='chapter-container' id='chap-{idx}'>")
        parts.append(f"<h1 class='chapter-header'><span>{chap['title']}</span><span style='font-size: 8.5pt; font-weight: normal; opacity: 0.85;'>CHAPTER {idx}</span></h1>")

        # 章节概览卡片
        parts.append("<div class='overview-card'>")
        parts.append(f"<div class='overview-card-title'>📋 本章核心目标与时限防漏排查</div>")
        parts.append("<div class='overview-grid'>")
        main_objs_str = "、".join(chap['main_objectives'][:4]) if chap['main_objectives'] else "按流程推进主线调查"
        if len(chap['main_objectives']) > 4:
            main_objs_str += f" 等共 {len(chap['main_objectives'])} 个关键节点"
        parts.append(f"<div class='overview-row'><span class='overview-label'>核心推进：</span><span class='overview-val'>{main_objs_str}</span></div>")

        miss_str = "、".join(chap['missables'][:4]) if chap['missables'] else "本章无易错漏极短时限委托"
        if len(chap['missables']) > 4:
            miss_str += f" 等共 {len(chap['missables'])} 项时限内容"
        parts.append(f"<div class='overview-row'><span class='overview-label'>时限防漏：</span><span class='overview-val'>{miss_str}</span></div>")
        parts.append("</div>")
        parts.append("</div>")

        # 任务流程卡片
        for quest in chap['quests']:
            classes = ["quest-card"]
            if quest.get('type') == 'main':
                classes.append("quest-main")
            else:
                classes.append("quest-side")
            if quest.get('is_remake_new'):
                classes.append("quest-remake")
            if quest.get('is_missable'):
                classes.append("quest-missable")

            parts.append(f"<div class='{' '.join(classes)}'>")
            parts.append("<div class='quest-header'>")
            parts.append("<div class='quest-title-area'>")
            parts.append(f"<span class='quest-title'>{html.escape(quest['name'])}</span>")
            if quest.get('type') == 'main':
                parts.append("<span class='badge badge-main'>主线任务</span>")
            else:
                parts.append("<span class='badge badge-side'>支线委托</span>")
            if quest.get('is_remake_new'):
                parts.append("<span class='badge badge-remake'>重制版新增/变更</span>")
            if quest.get('is_missable'):
                parts.append("<span class='badge badge-missable'>时限·注意</span>")
            if quest.get('bp'):
                parts.append(f"<span class='badge badge-bp'>BP: {html.escape(quest['bp'])}</span>")
            parts.append("</div>")
            parts.append("</div>")

            # 步骤
            if quest.get('steps'):
                parts.append("<ul class='quest-steps'>")
                for s in quest['steps']:
                    parts.append(f"<li class='quest-step-item'>{html.escape(s)}</li>")
                parts.append("</ul>")
            elif quest.get('content') and quest['content'] != quest['name']:
                clean_c = html.escape(quest['content']).replace('\n', '<br>')
                parts.append(f"<div style='font-size: 9pt; color: #34495e; line-height: 1.5; margin: 6px 0;'>{clean_c}</div>")
            else:
                parts.append("<div style='font-size: 8.8pt; color: #7f8c8d; margin: 4px 0;'>前往指定地点调查并推进剧情对话。</div>")

            parts.append("</div>")  # end quest-card

        # BOSS 战斗卡片
        if chap['bosses']:
            parts.append("<h2 class='section-header'>⚔️ 本章关键 BOSS / 剧情战术速查</h2>")
            for boss in chap['bosses']:
                parts.append("<div class='boss-card'>")
                parts.append("<div class='boss-header'>")
                parts.append(f"<div class='boss-title'>⚔️ {html.escape(boss['name'])}</div>")
                if boss.get('enemies'):
                    parts.append(f"<div class='boss-enemies'>敌方配置：{html.escape(boss['enemies'])}</div>")
                parts.append("</div>")
                parts.append("<div class='boss-strategy'>")
                parts.append(format_strategy(boss['strategy']))
                parts.append("</div>")
                parts.append("</div>")  # end boss-card

        parts.append("</div>")  # end chapter-container

    # 4. 附录一：书籍全收集一览表
    parts.append("<div class='appendix-container' id='appendix-1'>")
    parts.append("<h1 class='chapter-header'><span>附录一：全书籍与小说收集列表 (全33卷)</span><span style='font-size: 8.5pt; font-weight: normal; opacity: 0.85;'>APPENDIX I</span></h1>")
    parts.append("<div class='appendix-desc'>本表收录利贝尔全境发售的《利贝尔通讯》全期（含特别号、第1~10号）及连载小说《红耀石》（全1~11卷）。终章集齐全部 11 卷《红耀石》可在格兰赛尔东街区咖啡厅二层兑换艾丝蒂尔或约修亚的最终最强武器（太极棍 / 黑羽之鸦）。</div>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th style='width: 22%;'>书籍名称</th><th style='width: 25%;'>获得章节/时限</th><th style='width: 28%;'>获得地点/NPC</th><th style='width: 25%;'>收集说明与补救</th></tr></thead>")
    parts.append("<tbody>")
    for b in data['books']:
        timing_badge = "<span class='badge badge-missable'>" + html.escape(b['timing']) + "</span>" if "时限" in b.get('note', '') or "立刻" in b.get('timing', '') else "<span class='badge badge-category'>" + html.escape(b['timing']) + "</span>"
        note_str = html.escape(b['note'])
        if "最终武器" in note_str:
            note_str = f"<strong class='highlight-val'>{note_str}</strong>"
        parts.append(f"<tr><td><strong>{html.escape(b['name'])}</strong></td><td>{timing_badge}</td><td>{html.escape(b['location'])}</td><td>{note_str}</td></tr>")
    parts.append("</tbody></table>")
    parts.append("</div>")  # end appendix-1

    # 5. 附录二：料理与食谱大成功一览表
    parts.append("<div class='appendix-container' id='appendix-2'>")
    parts.append("<h1 class='chapter-header'><span>附录二：全料理食谱与大成功对应表 (全17道)</span><span style='font-size: 8.5pt; font-weight: normal; opacity: 0.85;'>APPENDIX II</span></h1>")
    parts.append("<div class='appendix-desc'>游击士协会便携烹饪指南。由特定角色烹饪时有较高概率制作出“独门料理”（强化效果）或“意外料理”（特殊状态/道具）。集齐全部料理食谱可获得料理达人成就并解锁全体属性加成。</div>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th style='width: 14%;'>食谱名称</th><th style='width: 24%;'>习得地点</th><th style='width: 12%;'>推荐角色</th><th style='width: 16%;'>独门料理</th><th style='width: 14%;'>意外料理</th><th style='width: 20%;'>制作奖励 (Bonus)</th></tr></thead>")
    parts.append("<tbody>")
    for r in data['recipes']:
        parts.append(f"<tr><td><strong>{html.escape(r['name'])}</strong></td><td>{html.escape(r['place'])}</td><td>{html.escape(r['maker'])}</td><td><span class='badge badge-remake'>{html.escape(r['unique'])}</span></td><td><span class='highlight-val'>{html.escape(r['bad'])}</span></td><td><span class='highlight-gold'>{html.escape(r['bonus'])}</span></td></tr>")
    parts.append("</tbody></table>")
    parts.append("</div>")  # end appendix-2

    # 6. 附录三：钓鱼图鉴与钓点大全
    parts.append("<div class='appendix-container' id='appendix-3'>")
    parts.append("<h1 class='chapter-header'><span>附录三：全钓鱼图鉴与钓点大全 (全10种)</span><span style='font-size: 8.5pt; font-weight: normal; opacity: 0.85;'>APPENDIX III</span></h1>")
    parts.append("<div class='appendix-desc'>利贝尔全境钓点水文资料。包含从初级钓竿到终极【水中霸王竿】的全部 10 种鱼类图鉴。鱼王【霸王鲑】仅能在获得特级钓竿后于瓦雷利亚湖深处或王都格兰赛尔御前水池钓起，必定掉落神圣之羽与全属性大量耀晶石。</div>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th style='width: 8%;'>编号</th><th style='width: 16%;'>鱼种名称</th><th style='width: 14%;'>推荐钓竿</th><th style='width: 12%;'>推荐鱼饵</th><th style='width: 26%;'>出现钓点坐标</th><th style='width: 24%;'>掉落耀晶石/奖励</th></tr></thead>")
    parts.append("<tbody>")
    for f in data['fishes']:
        name_str = f"<strong>{html.escape(f['name'])}</strong>"
        if "霸王" in f['name']:
            name_str = f"<strong class='highlight-val'>{html.escape(f['name'])}</strong>"
        parts.append(f"<tr><td>#{f['id']}</td><td>{name_str}</td><td>{html.escape(f['rod'])}</td><td>{html.escape(f['bait'])}</td><td>{html.escape(f['place'])}</td><td>{html.escape(f['drop'])}</td></tr>")
    parts.append("</tbody></table>")
    parts.append("</div>")  # end appendix-3

    # 7. 附录四：二周目通关继承与终极魔兽挑战
    parts.append("<div class='appendix-container' id='appendix-4'>")
    parts.append("<h1 class='chapter-header'><span>附录四：二周目通关继承与终极魔兽挑战</span><span style='font-size: 8.5pt; font-weight: normal; opacity: 0.85;'>APPENDIX IV</span></h1>")
    parts.append("<div class='appendix-desc'>《空之轨迹 the 1st 重制版》通关后将生成二周目通关存档。本作 100% 全成就/白金奖杯必须在二周目达成。</div>")

    # 继承要素表
    parts.append("<h2 class='section-header'>🔄 通关存档继承要素详情</h2>")
    parts.append("<table class='data-table'>")
    parts.append("<thead><tr><th style='width: 25%;'>继承项目</th><th style='width: 25%;'>继承机制说明</th><th style='width: 50%;'>战略价值与建议</th></tr></thead>")
    parts.append("<tbody>")
    parts.append("<tr><td><strong>角色等级与经验值</strong></td><td>全员等级、EXP完好保留</td><td>高等级开局可全程原野快速击杀小怪，快速推进流程</td></tr>")
    parts.append("<tr><td><strong>米拉与耀晶石</strong></td><td>全部携带货币与7属性晶石继承</td><td>开局即可于杂货店大量采购顶级补给品与饰品</td></tr>")
    parts.append("<tr><td><strong>武器、防具与饰品</strong></td><td>一周目获取的全装备道具完好继承</td><td>直接装备终章获取的最强武器（太极棍/黑羽之鸦）压制初期关卡</td></tr>")
    parts.append("<tr><td><strong>战术导力器孔位与结晶回路</strong></td><td>全员导力器开孔等级与全部结晶回路继承</td><td>开局即可配置全屏高阶时空幻魔法，原野与指令战双重秒杀</td></tr>")
    parts.append("<tr><td><strong>图鉴与手册收集数据</strong></td><td>书籍/料理/钓鱼/魔兽手册全量保留</td><td>二周目仅需查漏补缺漏掉的极少条目即可解锁全收集成就</td></tr>")
    parts.append("</tbody></table>")

    # 终极挑战卡片
    parts.append("<h2 class='section-header'>⚔️ 二周目专属挑战模式与终极魔兽攻略</h2>")
    parts.append("<div class='boss-card'>")
    parts.append("<div class='boss-header'>")
    parts.append("<div class='boss-title'>🏆 终极魔兽挑战：【幻想乐章·第二形态】(LV.100)</div>")
    parts.append("<div class='boss-enemies'>敌方配置：幻想乐章·终极形态 + 战术浮游炮×4</div>")
    parts.append("</div>")
    parts.append("<div class='boss-strategy'>")
    parts.append("<strong>【全成就开启条件】</strong>：继承存档开始二周目时，必须在继承设置中勾选开启<strong>「敌人 LV+50」</strong>难度强化挑战模式。<br>")
    parts.append("<strong>【弱点属性与异常】</strong>：全属性有效率 100%，全状态异常与能力降低完全免疫。<br>")
    parts.append("<strong>【战术对策建议】</strong>：<br>")
    parts.append("1. <strong>全员护盾覆盖</strong>：艾丝蒂尔佩戴【天眼】与【行动力5】，开局立刻施放【大地防护】使全员获得完全物理与魔法格挡；<br>")
    parts.append("2. <strong>时空幻高阶驱动</strong>：约修亚与科洛丝装备二周目合成的顶级回路【日轮之耀】与【霸道】，驱动【时间加速·改】与【暗影之矛】抢占行动顺序；<br>")
    parts.append("3. <strong>S-Craft 爆发时机</strong>：浮游炮释放群体减速前，约修亚开启 S 技【漆黑之牙】抢夺暴击(CRITICAL)行动顺位，一举清场完成终极讨伐。")
    parts.append("</div>")
    parts.append("</div>")

    parts.append("</div>")  # end appendix-4

    parts.append("</body>")
    parts.append("</html>")

    full_html = "\n".join(parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    return output_path
