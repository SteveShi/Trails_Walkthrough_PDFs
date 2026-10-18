import os
import unittest
from src.builder import build_sora_1st_html

class TestBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html_path = build_sora_1st_html()
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.content = f.read()

    def test_build_html(self):
        path = self.html_path
        self.assertTrue(os.path.exists(path))
        content = self.content
        self.assertIn("cover-title", content)
        self.assertIn("红耀石", content)
        self.assertIn("利贝尔鲤鱼", content)
        self.assertIn("枫糖曲奇", content)
        self.assertIn("成为准游击士（布莱特家）", content)
        self.assertIn("badge-missable", content)
        self.assertIn("badge-remake", content)
        self.assertIn("boss-card", content)

    def test_css_and_paged_media_integrity(self):
        content = self.content
        # 确保包含内联的 Paged Media CSS
        self.assertIn("<style>", content)
        self.assertIn("@page", content)
        self.assertIn("size: A4 portrait", content)
        self.assertIn("counter(page)", content)
        self.assertIn("break-inside: avoid", content)
        self.assertIn("quest-card", content)
        self.assertIn("overview-card", content)

    def test_badges_coverage(self):
        content = self.content
        self.assertIn("badge-main", content)
        self.assertIn("badge-side", content)
        self.assertIn("badge-bp", content)
        self.assertIn("badge-remake", content)
        self.assertIn("badge-missable", content)

    def test_appendices_structure(self):
        content = self.content
        # 附录一：书籍
        self.assertIn("附录一：全书籍与小说收集列表", content)
        self.assertIn("利贝尔通讯", content)
        self.assertIn("红耀石", content)
        self.assertIn("最终武器", content)

        # 附录二：料理
        self.assertIn("附录二：全料理食谱与大成功对应表", content)
        self.assertIn("特制枫糖曲奇", content)
        self.assertIn("焦黑曲奇", content)
        self.assertIn("全体HP+20", content)

        # 附录三：钓鱼
        self.assertIn("附录三：全钓鱼图鉴与钓点大全", content)
        self.assertIn("水中霸王竿", content)
        self.assertIn("霸王鲑", content)

        # 附录四：二周目通关继承与终极挑战
        self.assertIn("附录四：二周目通关继承与终极魔兽挑战", content)
        self.assertTrue("LV+50" in content or "继承" in content)

    def test_toc_overview(self):
        content = self.content
        self.assertIn("table-of-contents", content)
        self.assertIn("游击士终端", content)

if __name__ == '__main__':
    unittest.main()
