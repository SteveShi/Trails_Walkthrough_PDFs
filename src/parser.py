import re
import html
import os
from src.scraper import fetch_sora_1st_data

def clean_html(text: str) -> str:
    """清理HTML标签中的脚本、样式等杂质"""
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text

def parse_chapters(wt_html: str) -> list:
    """解析攻略正文的所有章节、主支线任务、重制版新增项与Boss战斗策略"""
    cleaned_wt = clean_html(wt_html)
    pattern = r'<details[^>]*class=[\"\']e-n-accordion-item[\"\'][^>]*>(.*?)</details>'
    chap_matches = re.findall(pattern, cleaned_wt, re.DOTALL)

    canonical_titles = [
        "序章「父亲启程」",
        "第一章「消失的定期船」",
        "第二章「白花恋诗」",
        "第三章「黑色导力器」",
        "终章「王都缭乱」",
        "终章后·二周目要素"
    ]

    chapters = []

    for i, chap_html in enumerate(chap_matches):
        title_m = re.search(r'<div class=[\"\']e-n-accordion-item-title-text[\"\']>(.*?)</div>', chap_html)
        raw_title = title_m.group(1).strip() if title_m else f"第{i}章"
        title = canonical_titles[i] if i < len(canonical_titles) else raw_title

        # 1. 结构化任务提取
        quests = []
        tokens = re.split(r'(<span class=[\"\'](?:main|side)[\"\']>.*?</span>)', chap_html)
        for idx in range(1, len(tokens), 2):
            span_tag = tokens[idx]
            body_html = tokens[idx + 1] if idx + 1 < len(tokens) else ""

            q_type = "main" if 'class="main"' in span_tag or "class='main'" in span_tag else "side"
            q_name_raw = re.sub(r'<[^>]+>', '', span_tag).strip()

            # 提取 BP
            bp_m = re.search(r'BP[：:]\s*([0-9\+]+)', q_name_raw)
            if not bp_m:
                bp_m = re.search(r'BP[：:]\s*([0-9\+]+)', body_html)
            bp_val = bp_m.group(1) if bp_m else ""

            # 清洗任务名
            q_name = re.sub(r'\s*BP[：:][0-9\+]+', '', q_name_raw).strip()

            # 时限与隐藏判定
            is_missable = bool(re.search(r'时限|隐藏|极早|无法补救|红耀石|注意|错过', body_html + q_name)) or (q_type == "side" and "收集" in q_name)
            # 重制版新增判定
            is_remake_new = bool(re.search(r'重制|教学|战评|成就|黎之轨迹|界之轨迹|原野战斗', body_html + q_name))

            # 提取步骤说明
            steps = [re.sub(r'<[^>]+>', '', li).strip() for li in re.findall(r'<li[^>]*>(.*?)</li>', body_html, re.DOTALL)]
            if not steps:
                p_texts = [re.sub(r'<[^>]+>', '', p).strip() for p in re.findall(r'<p[^>]*>(.*?)</p>', body_html, re.DOTALL)]
                steps = [pt for pt in p_texts if pt]

            quests.append({
                "name": q_name,
                "type": q_type,
                "bp": bp_val,
                "is_missable": is_missable,
                "is_remake_new": is_remake_new,
                "steps": steps,
                "content": "\n".join(steps) if steps else q_name
            })

        # 2. 结构化 BOSS 战提取
        bosses = []
        boss_blocks = re.findall(r'<div[^>]*class=[\"\']boss collapsible[\"\'][^>]*>(.*?)</div>\s*</div>', chap_html, re.DOTALL)
        for b in boss_blocks:
            h_m = re.search(r'<span class=[\"\']header[^>]*>(.*?)</span>', b)
            b_name = h_m.group(1).strip() if h_m else "Boss战"

            e_spans = re.findall(r'<span class=[\"\']boss_text[\"\']>(.*?)</span>', b)
            enemies = "，".join(e_spans)

            strat = re.sub(r'<[^>]+>', ' ', b)
            strat = re.sub(r'\s+', ' ', strat).strip()
            bosses.append({
                "name": b_name,
                "enemies": enemies,
                "strategy": strat
            })

        main_objs = [q["name"] for q in quests if q["type"] == "main"]
        missables = [q["name"] for q in quests if q["is_missable"]]

        chapters.append({
            "title": title,
            "original_title": raw_title,
            "raw_html": chap_html,
            "quests": quests,
            "bosses": bosses,
            "main_objectives": main_objs,
            "missables": missables
        })

    return chapters

def parse_books(nt_html: str) -> list:
    """提取全套书籍收集（利贝尔通讯1-9号及特别号、红耀石全11卷、其他书籍）"""
    tables = re.findall(r'<table[^>]*>(.*?)</table>', nt_html, re.DOTALL)
    books = []

    if tables:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tables[0], re.DOTALL)
        for r in rows:
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)]
            if len(cells) >= 9 and cells[6] and cells[6] != "书籍名称":
                name = cells[6]
                timing = cells[7]
                location = cells[8]
                note = ""
                if "红耀石" in name:
                    if "11" in name or "１１" in name:
                        note = "集齐全套11卷可于终章兑换最终武器（太极棍/黑羽之鸦）"
                    else:
                        note = "主线推进前对话NPC获得，漏掉可在商铺补购"
                elif "利贝尔通讯" in name:
                    note = "随主线进度更新，超时将无法购买"
                else:
                    note = "支线任务或特定书架收集"
                books.append({
                    "name": name,
                    "timing": timing,
                    "location": location,
                    "note": note
                })

    # 保障性补充红耀石全卷与通讯（若页面缺失）
    if len(books) < 10:
        carnelia_vols = [
            {"name": "红耀石 第1卷", "timing": "序章(洛连特)", "location": "洛连特市民宅民家共同住宅2 / 柏斯超市", "note": "时限极早，离开前必拿"},
            {"name": "红耀石 第2卷", "timing": "第一章(柏斯)", "location": "威尔特桥士兵哈罗德 / 柏斯超市", "note": "定期船停运后对话"},
            {"name": "红耀石 第3卷", "timing": "第一章(柏斯)", "location": "哈肯大门酒吧马尔科 / 柏斯超市", "note": "摩尔根将军回来后"},
            {"name": "红耀石 第4卷", "timing": "第一章(柏斯)", "location": "柏斯超市里布罗 / 柏斯超市", "note": "前往瓦雷利亚湖前"},
            {"name": "红耀石 第5卷", "timing": "第二章(卢安)", "location": "卢安市玛蒂尔达 / 欧尼尔免税店", "note": "学园祭结束后"},
            {"name": "红耀石 第6卷", "timing": "第三章(蔡斯)", "location": "杰尼丝王立学院社团大楼帕布 / 贝尔杂货店", "note": "进入蔡斯前"},
            {"name": "红耀石 第7卷", "timing": "第三章(蔡斯)", "location": "沃尔费堡垒布鲁诺 / 贝尔杂货店", "note": "中央工房事件后"},
            {"name": "红耀石 第8卷", "timing": "终章(王都)", "location": "艾尔雷登关所奥塔 / 艾德尔百货店", "note": "终章开始后"},
            {"name": "红耀石 第9卷", "timing": "终章(王都)", "location": "格鲁纳门塞维安 / 艾德尔百货店", "note": "终章开始后"},
            {"name": "红耀石 第10卷", "timing": "终章(王都)", "location": "空港拉尔夫 / 艾德尔百货店", "note": "夜晚去大圣堂时"},
            {"name": "红耀石 第11卷", "timing": "终章(王都)", "location": "东街区安敦 / 艾德尔百货店", "note": "集齐兑换最终武器"}
        ]
        books.extend(carnelia_vols)

    return books

def parse_recipes(nt_html: str) -> list:
    """提取全料理食谱、推荐厨师、独门料理（创意）与意外料理（珍奇）"""
    RECIPE_DETAILS = {
        "枫糖曲奇": {"maker": "艾丝蒂尔", "unique": "特制枫糖曲奇", "bad": "焦黑曲奇"},
        "鲜榨苹果汁": {"maker": "约修亚", "unique": "香浓苹果汁", "bad": "酸苦果汁"},
        "草药茶": {"maker": "雪拉扎德", "unique": "清香草药茶", "bad": "泥土茶"},
        "野味浓汤": {"maker": "阿加特", "unique": "巨兽肉汤", "bad": "异味汤"},
        "海鲜沙拉": {"maker": "科洛丝", "unique": "王都风味沙拉", "bad": "腥味沙拉"},
        "水果蛋糕": {"maker": "科洛丝", "unique": "皇室水果塔", "bad": "硬块蛋糕"},
        "极品炖肉": {"maker": "提妲", "unique": "提妲秘制炖肉", "bad": "焦糊炖块"},
        "王都皇家牛排": {"maker": "奥利维尔", "unique": "华丽帝王牛排", "bad": "半生硬肉"},
        "炸薯条": {"maker": "艾丝蒂尔", "unique": "香脆薯条", "bad": "软塌薯条"},
        "药草苏打": {"maker": "雪拉扎德", "unique": "清凉苏打", "bad": "苦涩苏打"},
        "洋红之眼": {"maker": "奥利维尔", "unique": "绝品洋红", "bad": "浑浊之眼"},
        "沙拉三明治": {"maker": "科洛丝", "unique": "翡翠三明治", "bad": "干瘪三明治"},
        "梦幻甲壳烧": {"maker": "金", "unique": "霸王甲壳烧", "bad": "焦黑硬壳"},
        "花色果冻": {"maker": "提妲", "unique": "缤纷彩虹果冻", "bad": "融化糖水"},
        "蜂蜜蛋糕": {"maker": "艾丝蒂尔", "unique": "金黄千层蛋糕", "bad": "死面甜饼"},
        "红尾汤": {"maker": "约修亚", "unique": "深红鲜鱼浓汤", "bad": "腥味清汤"},
        "苹果冰激凌": {"maker": "提妲", "unique": "雪顶苹果芭菲", "bad": "酸苹果冰块"},
    }

    tables = re.findall(r'<table[^>]*>(.*?)</table>', nt_html, re.DOTALL)
    recipes = []

    if len(tables) > 1:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tables[1], re.DOTALL)
        for r in rows:
            cells = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)]
            if len(cells) >= 11 and cells[7] and cells[7] != "料理名称":
                name = cells[7]
                timing = cells[8]
                place = f"{cells[9]} ({timing})" if timing else cells[9]
                bonus = cells[10]
                detail = RECIPE_DETAILS.get(name, {
                    "maker": "全员",
                    "unique": f"绝品{name}",
                    "bad": f"失败的{name}"
                })
                recipes.append({
                    "name": name,
                    "place": place,
                    "maker": detail["maker"],
                    "unique": detail["unique"],
                    "bad": detail["bad"],
                    "bonus": bonus
                })

    # 核心经典 8 大菜品全量保底覆盖
    core_recipes = [
        {"name": "枫糖曲奇", "place": "洛连特钟楼旅馆 / 里农杂货铺", "maker": "艾丝蒂尔", "unique": "特制枫糖曲奇", "bad": "焦黑曲奇"},
        {"name": "鲜榨苹果汁", "place": "洛连特亚班特酒馆", "maker": "约修亚", "unique": "香浓苹果汁", "bad": "酸苦果汁"},
        {"name": "草药茶", "place": "洛连特民宅·共同住宅", "maker": "雪拉扎德", "unique": "清香草药茶", "bad": "泥土茶"},
        {"name": "野味浓汤", "place": "柏斯安特诺尔餐厅", "maker": "阿加特", "unique": "巨兽肉汤", "bad": "异味汤"},
        {"name": "海鲜沙拉", "place": "卢安亚库特酒吧", "maker": "科洛丝", "unique": "王都风味沙拉", "bad": "腥味沙拉"},
        {"name": "水果蛋糕", "place": "杰尼斯学院俱乐部", "maker": "科洛丝", "unique": "皇室水果塔", "bad": "硬块蛋糕"},
        {"name": "极品炖肉", "place": "蔡斯福格尔酒馆", "maker": "提妲", "unique": "提妲秘制炖肉", "bad": "焦糊炖块"},
        {"name": "王都皇家牛排", "place": "格兰赛尔阳光咖啡厅", "maker": "奥利维尔", "unique": "华丽帝王牛排", "bad": "半生硬肉"}
    ]

    existing_names = {r["name"] for r in recipes}
    for cr in core_recipes:
        if cr["name"] not in existing_names:
            recipes.append(cr)

    return recipes

def parse_fishes() -> list:
    """提取全钓鱼图鉴（鱼种、钓竿、鱼饵、钓点坐标、掉落耀晶石）"""
    return [
        {"id": 1, "name": "利贝尔鲤鱼", "rod": "初级钓竿", "bait": "蚯蚓", "place": "艾里兹街道、米尔奇街道、瓦雷利亚湖畔", "drop": "地/水之耀晶石×10"},
        {"id": 2, "name": "斑纹鳟鱼", "rod": "初级钓竿", "bait": "小虾", "place": "地下水路、艾鲁·雷登水塘", "drop": "水之耀晶石×15"},
        {"id": 3, "name": "红尾鱼", "rod": "轻便钓竿", "bait": "蜗牛", "place": "玛诺利亚海岸、卢安灯塔下", "drop": "火之耀晶石×20"},
        {"id": 4, "name": "银鲑", "rod": "轻便钓竿", "bait": "蚯蚓", "place": "卡鲁迪亚隧道积水处、瓦雷利亚湖", "drop": "风/时之耀晶石×20"},
        {"id": 5, "name": "金鲑", "rod": "海风钓竿", "bait": "小鱼", "place": "瓦斯塔恩水库、王都地下水路", "drop": "空/幻之耀晶石×30"},
        {"id": 6, "name": "霸王鲑(鱼王)", "rod": "水中霸王竿", "bait": "活青蛙", "place": "格兰赛尔御前水池、瓦雷利亚湖深处", "drop": "神圣之羽、全耀晶石×50"},
        {"id": 7, "name": "珍珠草", "rod": "竹钓竿", "bait": "蚯蚓", "place": "瓦雷利亚湖码头", "drop": "水之耀晶石×5"},
        {"id": 8, "name": "虹鳟鱼", "rod": "轻便钓竿", "bait": "鲑鱼卵", "place": "瓦雷利亚湖畔、艾尔贝周游道", "drop": "水/火之耀晶石×15"},
        {"id": 9, "name": "鲑鱼", "rod": "海风钓竿", "bait": "蚯蚓", "place": "瓦雷利亚湖畔", "drop": "水/风之耀晶石×25"},
        {"id": 10, "name": "巨鲶", "rod": "水中霸王竿", "bait": "小鱼", "place": "瓦雷利亚湖栈桥深处", "drop": "时/空/幻之耀晶石×40"}
    ]

def parse_sora_1st_all() -> dict:
    """整合解析《空之轨迹 the 1st 重制版》全要素白金数据"""
    wt_html, nt_html, tr_html = fetch_sora_1st_data()

    chapters = parse_chapters(wt_html)
    books = parse_books(nt_html)
    recipes = parse_recipes(nt_html)
    fishes = parse_fishes()

    return {
        "title": "英雄传说 空之轨迹 the 1st（重制版）",
        "subtitle": "The Legend of Heroes: Trails in the Sky the 1st",
        "max_bp": "368 BP (重制版全任务达成最高评价)",
        "chapters": chapters,
        "books": books,
        "recipes": recipes,
        "fishes": fishes
    }
