import unittest
from src.parser import parse_sora_1st_all

class TestParser(unittest.TestCase):
    def test_parse_structure(self):
        data = parse_sora_1st_all()
        # 核心根字段校验
        self.assertIn("title", data)
        self.assertIn("subtitle", data)
        self.assertIn("max_bp", data)
        self.assertIn("chapters", data)
        self.assertIn("books", data)
        self.assertIn("recipes", data)
        self.assertIn("fishes", data)

        # 章节校验（序章、一、二、三、终章）
        self.assertTrue(len(data["chapters"]) >= 5)
        chapter_titles = [c["title"] for c in data["chapters"]]
        self.assertTrue(any("序章" in t for t in chapter_titles))
        self.assertTrue(any("第一章" in t for t in chapter_titles))
        self.assertTrue(any("第二章" in t for t in chapter_titles))
        self.assertTrue(any("第三章" in t for t in chapter_titles))
        self.assertTrue(any("终章" in t for t in chapter_titles))

        # 章节结构化数据校验
        for chap in data["chapters"]:
            self.assertIn("title", chap)
            self.assertIn("raw_html", chap)
            self.assertIn("quests", chap)
            self.assertIn("bosses", chap)
            self.assertIn("main_objectives", chap)
            self.assertIn("missables", chap)

        # 书籍全收集校验
        self.assertTrue(len(data["books"]) >= 10)
        book_names = [b["name"] for b in data["books"]]
        self.assertTrue(any("利贝尔通讯" in n for n in book_names))
        self.assertTrue(any("红耀石" in n for n in book_names))
        for b in data["books"]:
            self.assertIn("name", b)
            self.assertIn("timing", b)
            self.assertIn("location", b)
            self.assertIn("note", b)

        # 料理列表校验
        self.assertTrue(len(data["recipes"]) >= 8)
        recipe_names = [r["name"] for r in data["recipes"]]
        self.assertIn("枫糖曲奇", recipe_names)
        self.assertIn("鲜榨苹果汁", recipe_names)
        for r in data["recipes"]:
            self.assertIn("name", r)
            self.assertIn("place", r)
            self.assertIn("maker", r)
            self.assertIn("unique", r)
            self.assertIn("bad", r)

        # 钓鱼图鉴校验
        self.assertTrue(len(data["fishes"]) >= 6)
        for f in data["fishes"]:
            self.assertIn("id", f)
            self.assertIn("name", f)
            self.assertIn("rod", f)
            self.assertIn("bait", f)
            self.assertIn("place", f)
            self.assertIn("drop", f)

if __name__ == '__main__':
    unittest.main()
