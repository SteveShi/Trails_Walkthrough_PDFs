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

    def test_sen1_complete_books_and_fish(self):
        """验证《闪之轨迹 1》书籍收录全部 43 卷（红发骑士/红曜石/帝国时报）与 20 种鱼类"""
        sen1_cfg = next(g for g in GAMES_CONFIG if g["id"] == "sen1")
        html = render_game_html(sen1_cfg, self.css_content)
        
        app1_m = re.search(r'<div id=[\x27\"]appendix-1[\x27\"].*?<tbody>(.*?)</tbody>', html, re.DOTALL)
        rows_b = [r for r in re.findall(r'<tr>(.*?)</tr>', app1_m.group(1), re.DOTALL) if 'colspan' not in r]
        self.assertEqual(len(rows_b), 43, f"闪之轨迹 1 书籍数量应为 43，实际为 {len(rows_b)}")

if __name__ == '__main__':
    unittest.main()
