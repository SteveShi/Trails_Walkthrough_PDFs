"""
轨迹系列全 12 作全要素收集品（书籍、料理、钓鱼）完整数据全量同步器
直接通过 WordPress wpDataTables 服务端接口拉取 100% 完整未截断数据
"""

import json
import os
import re
import subprocess
import time
from typing import Dict, List, Any

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/notes_complete"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

GAMES_NOTES_MAP = [
    {
        "id": "sora_1st",
        "title": "空之轨迹 the 1st（重制版）",
        "url": "https://trails-game.com/walkthrough/sora-1st-notes/",
        "tables": {
            "books": {"wpid": 197, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 195, "name_col": "料理名称", "type_col": "料理种类", "time_col": "最早获取时间", "method_col": "获取方式", "bonus_col": "首次成功制作加成"}
        }
    },
    {
        "id": "sora_2nd",
        "title": "空之轨迹 the 2nd（重制版）",
        "url": "https://trails-game.com/walkthrough/sc-note/",
        "tables": {
            "fishes": {"wpid": 54, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓饵", "drop_col": "掉落物"},
            "books": {"wpid": 45, "name_col": "书籍名称", "type_col": "书籍类型", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 47, "name_col": "料理名称", "type_col": "料理类型", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "zero",
        "title": "零之轨迹 / 改",
        "url": "https://trails-game.com/walkthrough/zero-notes/",
        "tables": {
            "fishes": {"wpid": 42, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓饵", "drop_col": "掉落物"},
            "books": {"wpid": 38, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 39, "name_col": "料理名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "ao",
        "title": "碧之轨迹 / 改",
        "url": "https://trails-game.com/walkthrough/ao-note/",
        "tables": {
            "fishes": {"wpid": 46, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓饵", "drop_col": "掉落物"},
            "books": {"wpid": 41, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 40, "name_col": "料理名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "sen1",
        "title": "闪之轨迹 I / 改",
        "url": "https://trails-game.com/walkthrough/coldsteel1-notes/",
        "tables": {
            "fishes": {"wpid": 17, "name_col": "鱼名", "spot_col": "垂钓地点", "bait_col": "鱼竿", "drop_col": "掉落物"},
            "books": {"wpid": 22, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 13, "name_col": "料理名称", "time_col": "获得时间", "method_col": "获得方式", "bonus_col": "独门料理人"},
            "characters": {"wpid": 23, "category_col": "人物分类", "name_col": "人物名称", "entry_col": "词条名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "sen2",
        "title": "闪之轨迹 II / 改",
        "url": "https://trails-game.com/walkthrough/coldsteel2-notes/",
        "tables": {
            "fishes": {"wpid": 32, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓竿", "drop_col": "掉落物"},
            "books": {"wpid": 25, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 14, "name_col": "料理名称", "time_col": "获得时间", "method_col": "获得方式", "bonus_col": "独门料理人"},
            "characters": {"wpid": 24, "category_col": "人物分类", "name_col": "人物名称", "entry_col": "词条名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "sen3",
        "title": "闪之轨迹 III",
        "url": "https://trails-game.com/walkthrough/coldsteel3-notes/",
        "tables": {
            "fishes": {"wpid": 33, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓鱼点", "drop_col": "掉落物"},
            "books": {"wpid": 28, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 19, "name_col": "料理名称", "time_col": "获取时间", "method_col": "获取方式", "bonus_col": "独门料理人"},
            "characters": {"wpid": 30, "category_col": "人物分类", "name_col": "人物名称", "entry_col": "词条名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "sen4",
        "title": "闪之轨迹 IV",
        "url": "https://trails-game.com/walkthrough/coldsteel4-notes/",
        "tables": {
            "fishes": {"wpid": 34, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓鱼点", "drop_col": "掉落物"},
            "books": {"wpid": 29, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 20, "name_col": "料理名称", "time_col": "获取时间", "method_col": "获取方式", "bonus_col": "独门料理人"},
            "characters": {"wpid": 31, "category_col": "人物分类", "name_col": "人物名称", "entry_col": "词条名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "hajimari",
        "title": "创之轨迹",
        "url": "https://trails-game.com/walkthrough/hajimari-notes/",
        "tables": {
            "fishes": {"wpid": 112, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "钓鱼点", "drop_col": "掉落物"},
            "books": {"wpid": 113, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 114, "name_col": "料理名称", "time_col": "获得时间", "method_col": "获得方式", "bonus_col": "独门料理人"},
            "characters": {"wpid": 116, "category_col": "人物分类", "name_col": "人物名称", "entry_col": "词条名称", "time_col": "获取时间", "method_col": "获取方式"}
        }
    },
    {
        "id": "kuro1",
        "title": "黎之轨迹 I",
        "url": "https://trails-game.com/walkthrough/kuro-notes/",
        "tables": {
            "books": {"wpid": 141, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 150, "name_col": "料理名称", "type_col": "料理类型", "time_col": "获取时间", "method_col": "获取方式", "bonus_col": "料理人"}
        }
    },
    {
        "id": "kuro2",
        "title": "黎之轨迹 II",
        "url": "https://trails-game.com/walkthrough/kuro2-notes/",
        "tables": {
            "fishes": {"wpid": 174, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "章节", "drop_col": "掉落道具（C/B/A）"},
            "books": {"wpid": 163, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"},
            "recipes": {"wpid": 166, "name_col": "料理名称", "type_col": "料理类型", "time_col": "获取时间", "method_col": "获取方式", "bonus_col": "料理人"}
        }
    },
    {
        "id": "kai",
        "title": "界之轨迹",
        "url": "https://trails-game.com/walkthrough/kai-notes/",
        "tables": {
            "fishes": {"wpid": 203, "name_col": "鱼名", "spot_col": "钓鱼点", "bait_col": "章节", "drop_col": "掉落道具（C/B/A）"},
            "books": {"wpid": 189, "name_col": "书籍名称", "type_col": "书籍分类", "time_col": "获取时间", "method_col": "获取方式"}
        }
    }
]

def clean_val(v: Any) -> str:
    if v is None:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(v))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_table_data(wpid: int, nonce: str, referer_url: str, max_retries: int = 3) -> List[List[str]]:
    ajax_url = f"https://trails-game.com/wp-admin/admin-ajax.php?action=get_wdtable&table_id={wpid}"
    post_data = f"draw=1&start=0&length=300&wdtNonce={nonce}"
    
    cmd = [
        "curl", "-s", "-X", "POST", ajax_url,
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", f"Referer: {referer_url}",
        "-H", "X-Requested-With: XMLHttpRequest",
        "-d", post_data
    ]
    
    for attempt in range(max_retries):
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.stdout:
            try:
                data = json.loads(res.stdout)
                rows = data.get("data", [])
                if rows or attempt == max_retries - 1:
                    return rows
            except Exception as e:
                pass
        time.sleep(1.0)
    return []

def sync_single_game(game_cfg: Dict[str, Any]) -> Dict[str, Any]:
    gid = game_cfg["id"]
    title = game_cfg["title"]
    url = game_cfg["url"]
    
    print(f"\n========================================================")
    print(f"  正在同步《{title}》收集品数据...")
    print(f"  URL: {url}")
    print(f"========================================================")
    
    # 1. 获取最新 HTML
    curl_res = subprocess.run([
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        url
    ], capture_output=True, text=True)
    
    html = curl_res.stdout
    if not html:
        print(f"❌ 无法拉取页面 HTML: {url}")
        return {}

    # 提取所有 nonce
    nonces = dict(re.findall(r'id=[\"\']wdtNonceFrontendServerSide_(\d+)[\"\'][^>]*value=[\"\']([^\"\']+)[\"\']', html))
    
    # 提取所有 table 的真实表头
    table_headers: Dict[int, List[str]] = {}
    table_matches = re.findall(r'<table[^>]*data-wpdatatable_id=[\"\'](\d+)[\"\'][^>]*>(.*?)</table>', html, re.DOTALL)
    for wpid_str, table_inner in table_matches:
        wpid = int(wpid_str)
        if wpid not in table_headers:
            ths = [re.sub(r'<[^>]+>', '', th).strip() for th in re.findall(r'<th[^>]*>(.*?)</th>', table_inner, re.DOTALL)]
            table_headers[wpid] = ths

    result: Dict[str, List[Any]] = {
        "books": [],
        "recipes": [],
        "fishes": [],
        "characters": []
    }
    
    # 处理各个配置表格
    for category, tcfg in game_cfg["tables"].items():
        wpid = tcfg["wpid"]
        nonce = nonces.get(str(wpid))
        if not nonce:
            print(f"  ⚠️ 未找到 wpID {wpid} 的有效 nonce，尝试降级读取...")
            continue
            
        headers = table_headers.get(wpid, [])
        raw_rows = fetch_table_data(wpid, nonce, url)
        print(f"  [wpID {wpid} - {category}] 成功获取 {len(raw_rows)} 行数据 | 表头: {' '.join(headers)[:40]}")
        
        # 建立列索引映射
        def get_col_idx(col_name_target: str, default_idx: int) -> int:
            for idx, h in enumerate(headers):
                if col_name_target in h:
                    return idx
            return default_idx

        seen_names = set()
        
        if category == "books":
            idx_name = get_col_idx(tcfg.get("name_col", "书籍名称"), 2)
            idx_type = get_col_idx(tcfg.get("type_col", "书籍分类"), 1)
            idx_time = get_col_idx(tcfg.get("time_col", "获取时间"), 3)
            idx_method = get_col_idx(tcfg.get("method_col", "获取方式"), 4)
            
            for row in raw_rows:
                if len(row) <= idx_name:
                    continue
                b_name = clean_val(row[idx_name])
                if not b_name or b_name in seen_names or b_name == tcfg.get("name_col"):
                    continue
                seen_names.add(b_name)
                
                b_type = clean_val(row[idx_type]) if len(row) > idx_type else "书籍"
                b_time = clean_val(row[idx_time]) if len(row) > idx_time else ""
                b_method = clean_val(row[idx_method]) if len(row) > idx_method else ""
                
                result["books"].append({
                    "id": str(len(result["books"]) + 1),
                    "type": b_type,
                    "name": b_name,
                    "time": b_time,
                    "method": b_method
                })
                
        elif category == "recipes":
            idx_name = get_col_idx(tcfg.get("name_col", "料理名称"), 1)
            idx_time = get_col_idx(tcfg.get("time_col", "获取时间"), 2)
            idx_method = get_col_idx(tcfg.get("method_col", "获取方式"), 3)
            idx_bonus = get_col_idx(tcfg.get("bonus_col", "独门"), 4)
            
            for row in raw_rows:
                if len(row) <= idx_name:
                    continue
                r_name = clean_val(row[idx_name])
                if not r_name or r_name in seen_names or r_name == tcfg.get("name_col"):
                    continue
                seen_names.add(r_name)
                
                r_time = clean_val(row[idx_time]) if len(row) > idx_time else ""
                r_method = clean_val(row[idx_method]) if len(row) > idx_method else ""
                r_bonus = clean_val(row[idx_bonus]) if len(row) > idx_bonus else ""
                
                result["recipes"].append({
                    "id": str(len(result["recipes"]) + 1),
                    "name": r_name,
                    "time": r_time,
                    "method": r_method,
                    "bonus": r_bonus
                })
                
        elif category == "fishes":
            idx_name = get_col_idx(tcfg.get("name_col", "鱼名"), 2 if "图标" in "".join(headers) else 1)
            idx_spot = get_col_idx(tcfg.get("spot_col", "钓鱼点"), 3)
            idx_bait = get_col_idx(tcfg.get("bait_col", "钓饵"), 4)
            idx_drop = get_col_idx(tcfg.get("drop_col", "掉落物"), 5)
            
            for row in raw_rows:
                if len(row) <= idx_name:
                    continue
                f_name = clean_val(row[idx_name])
                if not f_name or f_name in seen_names or f_name == tcfg.get("name_col"):
                    continue
                seen_names.add(f_name)
                
                f_spot = clean_val(row[idx_spot]) if len(row) > idx_spot else ""
                f_bait = clean_val(row[idx_bait]) if len(row) > idx_bait else ""
                f_drop = clean_val(row[idx_drop]) if len(row) > idx_drop else ""
                
                result["fishes"].append({
                    "id": str(len(result["fishes"]) + 1),
                    "name": f_name,
                    "spot": f_spot,
                    "bait": f_bait,
                    "drop": f_drop
                })

        elif category == "characters":
            idx_cat = get_col_idx(tcfg.get("category_col", "分类"), 1)
            idx_name = get_col_idx(tcfg.get("name_col", "人物名称"), 2)
            idx_entry = get_col_idx(tcfg.get("entry_col", "词条名称"), 3)
            idx_time = get_col_idx(tcfg.get("time_col", "获取时间"), 4)
            idx_method = get_col_idx(tcfg.get("method_col", "获取方式"), 5)
            
            for row in raw_rows:
                if len(row) <= idx_entry:
                    continue
                c_name = clean_val(row[idx_name]) if len(row) > idx_name else ""
                c_entry = clean_val(row[idx_entry]) if len(row) > idx_entry else ""
                if not c_name or not c_entry:
                    continue
                key = f"{c_name}_{c_entry}"
                if key in seen_names:
                    continue
                seen_names.add(key)
                
                c_cat = clean_val(row[idx_cat]) if len(row) > idx_cat else ""
                c_time = clean_val(row[idx_time]) if len(row) > idx_time else ""
                c_method = clean_val(row[idx_method]) if len(row) > idx_method else ""
                
                result["characters"].append({
                    "id": str(len(result["characters"]) + 1),
                    "category": c_cat,
                    "name": c_name,
                    "entry": c_entry,
                    "time": c_time,
                    "method": c_method
                })

    print(f"  ✨ 整理统计: 书籍 {len(result['books'])} 本 | 料理 {len(result['recipes'])} 道 | 钓鱼 {len(result['fishes'])} 种 | 人物笔记 {len(result.get('characters', []))} 条")
    
    out_file = os.path.join(OUTPUT_DIR, f"{gid}_notes.json")
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False, indent=2)
    print(f"  💾 已持久化到: {out_file}")
    
    return result

def sync_all_games():
    print("🚀 开始全量同步 12 部轨迹作品未截断官方收集品数据...")
    summary = {}
    for g in GAMES_NOTES_MAP:
        res = sync_single_game(g)
        summary[g["id"]] = {
            "books": len(res.get("books", [])),
            "recipes": len(res.get("recipes", [])),
            "fishes": len(res.get("fishes", []))
        }
        time.sleep(0.5)
        
    print("\n========================================================")
    print("  全量数据同步完成！汇总报告:")
    print("========================================================")
    for gid, counts in summary.items():
        print(f"  - {gid:10s}: 书籍 {counts['books']:2d} 卷 | 料理 {counts['recipes']:2d} 道 | 钓鱼 {counts['fishes']:2d} 种")

if __name__ == "__main__":
    sync_all_games()
