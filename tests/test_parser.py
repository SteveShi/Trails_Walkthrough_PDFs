import unittest
from src.parser import parse_sora_1st_all

class TestParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = parse_sora_1st_all()

    def test_parse_structure(self):
        data = self.data
        # 核心根字段校验
        self.assertIn("title", data)
        self.assertIn("subtitle", data)
        self.assertIn("max_bp", data)
        self.assertIn("chapters", data)
        self.assertIn("books", data)
        self.assertIn("recipes", data)
        self.assertIn("fishes", data)

        # 章节校验（序章、一、二、三、终章、二周目）
        self.assertEqual(len(data["chapters"]), 6)
        chapter_titles = [c["title"] for c in data["chapters"]]
        self.assertTrue(any("序章" in t for t in chapter_titles))
        self.assertTrue(any("第一章" in t for t in chapter_titles))
        self.assertTrue(any("第二章" in t for t in chapter_titles))
        self.assertTrue(any("第三章" in t for t in chapter_titles))
        self.assertTrue(any("终章「王都" in t for t in chapter_titles))
        self.assertTrue(any("二周目" in t for t in chapter_titles))

        # 章节结构化数据字段校验
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

        # 钓鱼图鉴校验
        self.assertTrue(len(data["fishes"]) >= 6)
        for f in data["fishes"]:
            self.assertIn("id", f)
            self.assertIn("name", f)
            self.assertIn("rod", f)
            self.assertIn("bait", f)
            self.assertIn("place", f)
            self.assertIn("drop", f)

    def test_prologue_opening_data_integrity(self):
        """校验序章开局布莱特家调查闪光点获取生命露水等关键指引未丢失"""
        prologue = self.data["chapters"][0]
        self.assertIn("序章", prologue["title"])
        prologue_quests = prologue["quests"]
        self.assertTrue(len(prologue_quests) > 0)

        # 验证开局任务存在且包含布莱特家与生命露水
        has_opening = any(
            ("布莱特家" in q["name"] or "布莱特家" in q["content"]) and
            ("生命露水" in q["content"] or any("生命露水" in s for s in q["steps"]))
            for q in prologue_quests
        )
        self.assertTrue(has_opening, "序章必须完整保留布莱特家开场调查获得生命露水等关键指引")

    def test_final_chapter_carnelia_guidance(self):
        """校验终章开头前往王都途中的红耀石第8卷与第9卷收集指引未丢失"""
        final_chap = [c for c in self.data["chapters"] if "终章「王都" in c["title"]][0]
        final_quests = final_chap["quests"]
        self.assertTrue(len(final_quests) > 0)

        has_vol8 = any(
            ("红耀石·第8卷" in q["content"] or "红耀石 8" in q["content"] or ("红耀石" in q["content"] and "8" in q["content"])) and
            ("艾尔·雷登" in q["content"] or "奥特" in q["content"])
            for q in final_quests
        )
        has_vol9 = any(
            ("红耀石·第9卷" in q["content"] or "红耀石 9" in q["content"] or ("红耀石" in q["content"] and "9" in q["content"])) and
            ("古琉尼大门" in q["content"] or "瑟尔凡" in q["content"])
            for q in final_quests
        )
        self.assertTrue(has_vol8, "终章必须保留艾尔·雷登获取红耀石第8卷的指引")
        self.assertTrue(has_vol9, "终章必须保留古琉尼大门获取红耀石第9卷的指引")

    def test_ng_plus_chapter_elements(self):
        """校验二周目要素章节非空，且包含继承、LV+50强敌、奖杯等要素"""
        ng_chap = [c for c in self.data["chapters"] if "二周目" in c["title"]][0]
        self.assertTrue(len(ng_chap["quests"]) > 0, "二周目章节 quests 不应为空")
        self.assertTrue(len(ng_chap["main_objectives"]) > 0, "二周目章节 main_objectives 不应为空")

        all_content = " ".join([q["content"] for q in ng_chap["quests"]])
        self.assertTrue(any(term in all_content for term in ["LV+50", "敌人LV+50", "幻想乐章"]), "二周目要素应包含LV+50敌人等具体指引")
        self.assertTrue(any(term in all_content for term in ["继承", "高级回路", "全成就"]), "二周目要素应包含通关继承与高级回路指引")

    def test_recipe_schema_consistency(self):
        """校验所有料理数据严格包含全部统一字段（含 bonus），且无空值"""
        recipes = self.data["recipes"]
        self.assertTrue(len(recipes) >= 8)

        required_keys = {"name", "place", "maker", "unique", "bad", "bonus"}
        for r in recipes:
            for k in required_keys:
                self.assertIn(k, r, f"料理条目缺少字段 '{k}': {r}")
                self.assertTrue(bool(r[k]), f"料理条目中的 '{k}' 字段值不能为空: {r}")

        # 核心经典菜品必须在列表中
        names = {r["name"] for r in recipes}
        self.assertIn("枫糖曲奇", names)
        self.assertIn("鲜榨苹果汁", names)
        self.assertIn("王都皇家牛排", names)

    def test_quest_steps_no_data_pollution(self):
        """校验任务 steps 中已剔除宝箱、回路配置及 Boss 战斗策略等折叠子块"""
        for chap in self.data["chapters"]:
            for q in chap["quests"]:
                for step in q["steps"]:
                    self.assertNotIn("总计：", step, f"任务步骤中混入了宝箱数量统计: {step}")
                    self.assertFalse(step.startswith("Line 1："), f"任务步骤中混入了导力回路配置: {step}")
                    self.assertFalse(step.startswith("Line 2："), f"任务步骤中混入了导力回路配置: {step}")

if __name__ == '__main__':
    unittest.main()
