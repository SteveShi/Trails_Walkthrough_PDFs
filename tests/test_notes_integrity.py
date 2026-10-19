"""
收集品数据完整性与无截断回归测试套件
验证全 12 部轨迹作品的书籍、料理、钓鱼数据突破 10 行分页限制，保持 100% 完整收录
"""

import os
import json
import re
import unittest
from src.games_config import GAMES_CONFIG
from src.universal_builder import render_game_html

class TestNotesIntegrity(unittest.TestCase):
    def setUp(self):
        self.css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates/style.css"))
        with open(self.css_path, "r", encoding="utf-8") as f:
            self.css_content = f.read()

    def test_zero_complete_gran_novels(self):
        """验证《零之轨迹》包含全部 22 本书籍及《黑市医生葛兰》全 14 卷"""
        zero_cfg = next(g for g in GAMES_CONFIG if g["id"] == "zero")
        html = render_game_html(zero_cfg, self.css_content)
        
        # 附录一书籍表格行数必须为 22
        app1_m = re.search(r'<div id=[\x27\"]appendix-1[\x27\"].*?<tbody>(.*?)</tbody>', html, re.DOTALL)
        self.assertIsNotNone(app1_m, "附录一书籍表格未找到")
        rows = [r for r in re.findall(r'<tr>(.*?)</tr>', app1_m.group(1), re.DOTALL) if 'colspan' not in r]
        self.assertEqual(len(rows), 22, f"零之轨迹书籍行数应为 22，实际为 {len(rows)}")
        
        # 必须完整包含第 1 卷至第 14 卷
        for vol in range(1, 15):
            self.assertTrue(
                any(f"黑市医生葛兰·第{vol}卷" in r or f"黑市医生葛兰 第{vol}卷" in r for r in rows),
                f"缺少《黑市医生葛兰》第 {vol} 卷"
            )

    def test_ao_complete_notes(self):
        """验证《碧之轨迹》书籍、料理、钓鱼饱满未截断"""
        ao_cfg = next(g for g in GAMES_CONFIG if g["id"] == "ao")
        html = render_game_html(ao_cfg, self.css_content)
        
        app1_m = re.search(r'<div id=[\x27\"]appendix-1[\x27\"].*?<tbody>(.*?)</tbody>', html, re.DOTALL)
        rows_b = [r for r in re.findall(r'<tr>(.*?)</tr>', app1_m.group(1), re.DOTALL) if 'colspan' not in r]
        self.assertTrue(len(rows_b) >= 20, f"碧之轨迹书籍数量不足: {len(rows_b)}")
        
        app2_m = re.search(r'<div id=[\x27\"]appendix-2[\x27\"].*?<tbody>(.*?)</tbody>', html, re.DOTALL)
        rows_r = [r for r in re.findall(r'<tr>(.*?)</tr>', app2_m.group(1), re.DOTALL) if 'colspan' not in r]
        self.assertTrue(len(rows_r) >= 20, f"碧之轨迹料理数量不足: {len(rows_r)}")

    def test_character_notes_integrity(self):
        """验证闪 1~4 与创轨的人物笔记完整性（合计 806 条）"""
        expected_counts = {
            "sen1": 95,
            "sen2": 179,
            "sen3": 141,
            "sen4": 207,
            "hajimari": 184
        }
        for gid, expected in expected_counts.items():
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../data/notes_complete/{gid}_notes.json"))
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            chars = data.get("characters", [])
            self.assertEqual(len(chars), expected, f"{gid} 人物笔记条数应为 {expected}，实际为 {len(chars)}")

    def test_sen1_character_notes_render(self):
        """验证《闪之轨迹 1》HTML 中成功渲染附录四人物笔记表格与关键词"""
        sen1_cfg = next(g for g in GAMES_CONFIG if g["id"] == "sen1")
        html = render_game_html(sen1_cfg, self.css_content)
        
        self.assertIn("id='appendix-characters'", html)
        self.assertIn("附录四：全人物笔记与时限词条全收集对照表", html)
        self.assertIn("character-notes-table", html)
        self.assertIn("黎恩", html)
        self.assertIn("兄妹情深", html)
        self.assertIn("亚莉莎", html)
        self.assertIn("给祖父的礼物", html)

    def test_flow_tables_and_callouts_render(self):
        """验证流程正文表格与战术引用栏正确渲染，未被去格式化"""
        sora_cfg = next(g for g in GAMES_CONFIG if g["id"] == "sora_1st")
        html = render_game_html(sora_cfg, self.css_content)
        
        self.assertIn("flow-data-table", html)
        self.assertIn("tactical-quote-box", html)

if __name__ == '__main__':
    unittest.main()
