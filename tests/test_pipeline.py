import os
import unittest
from src.scraper import fetch_sora_1st_data
from src.parser import parse_sora_1st_all
from src.builder import build_sora_1st_html
from src.pdf_exporter import get_chrome_binary


class TestPipeline(unittest.TestCase):
    """端到端核心数据管道流转与完整性测试"""

    def test_pipeline_data_flow(self):
        """验证整个数据管道流转：获取 -> 解析 -> 构建 -> 导出组件完整性"""
        wt, nt, tr = fetch_sora_1st_data()
        self.assertGreater(len(wt), 1000)
        self.assertGreater(len(nt), 1000)
        self.assertGreater(len(tr), 1000)

        data = parse_sora_1st_all()
        self.assertEqual(len(data["chapters"]), 6)
        self.assertGreater(len(data["books"]), 10)
        self.assertGreater(len(data["recipes"]), 10)
        self.assertGreater(len(data["fishes"]), 5)

        html_path = build_sora_1st_html()
        self.assertTrue(os.path.exists(html_path))
        with open(html_path, "r", encoding="utf-8") as f:
            rendered_html = f.read()

        self.assertIn("<!DOCTYPE html>", rendered_html)
        self.assertIn("cover-page", rendered_html)
        self.assertIn("table-of-contents", rendered_html)

        chrome_bin = get_chrome_binary()
        self.assertIsNotNone(chrome_bin)
        self.assertTrue(os.path.exists(chrome_bin))


if __name__ == '__main__':
    unittest.main()
