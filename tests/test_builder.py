import os
import re
import tempfile
import unittest
from src.builder import (
    build_sora_1st_html,
    format_strategy,
    render_cover,
    render_toc,
    render_chapters,
    render_appendices,
)

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

    def test_table_pagination_and_avoid_rules(self):
        """测试表格跨页分页与 avoid 规则：table 自身允许自然跨页，tr 不截断，thead 跨页重复"""
        content = self.content

        # 1. 验证 table.data-table 规则块本身不包含 break-inside: avoid
        table_block_match = re.search(r"table\.data-table\s*\{([^}]+)\}", content)
        self.assertIsNotNone(table_block_match, "必须包含 table.data-table CSS 定义")
        table_block_css = table_block_match.group(1)
        self.assertNotIn("break-inside: avoid", table_block_css)
        self.assertNotIn("page-break-inside: avoid", table_block_css)

        # 2. 验证 thead 具备 table-header-group 以便多页重复表头
        thead_match = re.search(r"table\.data-table thead\s*\{([^}]+)\}", content)
        self.assertIsNotNone(thead_match, "必须包含 table.data-table thead CSS 定义")
        self.assertIn("display: table-header-group", thead_match.group(1))

        # 3. 验证 table.data-table tr 具备 break-inside: avoid 防止单行跨页断裂
        tr_match = re.search(r"table\.data-table tr\s*\{([^}]+)\}", content)
        self.assertIsNotNone(tr_match, "必须包含 table.data-table tr CSS 定义")
        tr_css = tr_match.group(1)
        self.assertIn("break-inside: avoid", tr_css)
        self.assertIn("page-break-inside: avoid", tr_css)

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

    def test_toc_overview_and_anchors(self):
        """测试目录系统导航与锚点直达指示符，确保无假页码数字"""
        content = self.content
        self.assertIn("table-of-contents", content)
        self.assertIn("游击士终端", content)

        # 验证包含直达锚点跳转指示
        self.assertIn("toc-jump", content)
        self.assertIn("直达 ▸", content)

        # 验证不存在假硬编码页码
        self.assertNotIn("<span>P.8</span>", content)
        self.assertNotIn("<span>P.9</span>", content)
        self.assertNotIn("<span>P.10</span>", content)
        self.assertNotIn("<span>P.11</span>", content)
        self.assertNotIn("<span>P.2</span>", content)

    def test_format_strategy(self):
        """测试 format_strategy 的各种边界条件与格式化规则"""
        # 1. 空输入处理
        default_strat = "常规战斗，注意保持队伍血量并以克制属性魔法攻击。"
        self.assertEqual(format_strategy(""), default_strat)
        self.assertEqual(format_strategy(None), default_strat)

        # 2. 关键词替换（中文冒号与英文冒号）
        text = "对方配置：战术浮游炮×4 建议打法: 集中攻击弱点 注意事项：注意全体异常 弱点属性: 时属性100%"
        formatted = format_strategy(text)
        self.assertIn("<strong>【对方配置】</strong>", formatted)
        self.assertIn("<strong>【建议打法】</strong>", formatted)
        self.assertIn("<strong>【注意事项】</strong>", formatted)
        self.assertIn("<strong>【弱点属性】</strong>", formatted)

        # 3. 换行与连续换行符转为 <br>
        multi_lines = "第一行准备\n\n第二行攻击\n第三行收尾"
        formatted_lines = format_strategy(multi_lines)
        self.assertIn("第一行准备<br>第二行攻击<br>第三行收尾", formatted_lines)
        self.assertNotIn("\n", formatted_lines)

        # 4. 开头 <br> 消除
        strat_with_leading_br = "建议打法：开局直接施放大招"
        res = format_strategy(strat_with_leading_br)
        self.assertFalse(res.startswith("<br>"))
        self.assertTrue(res.startswith("<strong>【建议打法】</strong>"))

        # 5. XSS 转义防御
        xss_strat = "<script>alert('xss')</script> & 特务兵"
        res_xss = format_strategy(xss_strat)
        self.assertNotIn("<script>", res_xss)
        self.assertIn("&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;", res_xss)
        self.assertIn("&amp;", res_xss)

    def test_custom_output_path(self):
        """测试自定义输出路径（包括不存在的多级父目录自动创建）"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            deep_path = os.path.join(tmp_dir, "nested", "subfolder", "walkthrough.html")
            self.assertFalse(os.path.exists(os.path.dirname(deep_path)))

            returned_path = build_sora_1st_html(output_path=deep_path)
            self.assertEqual(returned_path, deep_path)
            self.assertTrue(os.path.exists(deep_path))

            with open(deep_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertTrue(content.startswith("<!DOCTYPE html>"))
            self.assertIn("</html>", content)

    def test_modular_render_functions(self):
        """测试各个模块化渲染子函数的独立执行与有效性"""
        sample_data = {
            "title": "测试轨迹",
            "subtitle": "测试副标题",
            "max_bp": "368",
            "chapters": [
                {
                    "title": "序章 父亲·旅启",
                    "main_objectives": ["目标1", "目标2"],
                    "missables": ["注意1"],
                    "quests": [
                        {
                            "name": "测试任务",
                            "type": "main",
                            "bp": "1+2",
                            "steps": ["步骤一", "步骤二"]
                        }
                    ],
                    "bosses": [
                        {
                            "name": "测试Boss",
                            "enemies": "魔兽×2",
                            "strategy": "对方配置：魔兽 建议打法：强攻"
                        }
                    ]
                }
            ],
            "books": [
                {"name": "测试书", "timing": "序章", "location": "杂货店", "note": "时限注意"}
            ],
            "recipes": [
                {"name": "测试料理", "place": "洛连特", "maker": "艾丝蒂尔", "unique": "特制料理", "bad": "失败料理", "bonus": "HP+10"}
            ],
            "fishes": [
                {"id": 1, "name": "测试鱼", "rod": "初级钓竿", "bait": "蚯蚓", "place": "洛连特", "drop": "地水火风各10"}
            ]
        }

        # 封面模块
        cover = render_cover(sample_data)
        self.assertIn("cover-page", cover)
        self.assertIn("测试轨迹", cover)

        # 目录模块
        toc = render_toc(sample_data)
        self.assertIn("table-of-contents", toc)
        self.assertIn("序章 父亲·旅启", toc)
        self.assertIn("toc-jump", toc)

        # 章节模块
        chaps = render_chapters(sample_data["chapters"])
        self.assertIn("chapter-container", chaps)
        self.assertIn("测试Boss", chaps)

        # 附录模块
        apps = render_appendices(sample_data)
        self.assertIn("appendix-1", apps)
        self.assertIn("测试料理", apps)

    def test_xss_escaping_coverage(self):
        """测试在所有动态字段注入 XSS 载荷时的转义覆盖情况"""
        xss_payload = "<script>alert('pwned')</script>&\"'"
        malicious_data = {
            "title": f"标题 {xss_payload}",
            "subtitle": f"副标题 {xss_payload}",
            "max_bp": f"999 {xss_payload}",
            "chapters": [
                {
                    "title": f"章节名 {xss_payload}",
                    "main_objectives": [f"目标 {xss_payload}"],
                    "missables": [f"错漏 {xss_payload}"],
                    "quests": [
                        {
                            "name": f"任务名 {xss_payload}",
                            "type": "main",
                            "bp": f"10 {xss_payload}",
                            "steps": [f"步骤 {xss_payload}"],
                            "content": f"内容 {xss_payload}"
                        }
                    ],
                    "bosses": [
                        {
                            "name": f"首领名 {xss_payload}",
                            "enemies": f"敌方 {xss_payload}",
                            "strategy": f"策略 {xss_payload}"
                        }
                    ]
                }
            ],
            "books": [
                {"name": f"书名 {xss_payload}", "timing": f"时机 {xss_payload}", "location": f"地点 {xss_payload}", "note": f"备注 {xss_payload}"}
            ],
            "recipes": [
                {"name": f"菜谱 {xss_payload}", "place": f"地点 {xss_payload}", "maker": f"作者 {xss_payload}", "unique": f"特制 {xss_payload}", "bad": f"意外 {xss_payload}", "bonus": f"奖励 {xss_payload}"}
            ],
            "fishes": [
                {"id": 99, "name": f"鱼类 {xss_payload}", "rod": f"钓竿 {xss_payload}", "bait": f"鱼饵 {xss_payload}", "place": f"钓点 {xss_payload}", "drop": f"掉落 {xss_payload}"}
            ]
        }

        rendered_cover = render_cover(malicious_data)
        rendered_toc = render_toc(malicious_data)
        rendered_chapters = render_chapters(malicious_data["chapters"])
        rendered_appendices = render_appendices(malicious_data)

        for fragment in [rendered_cover, rendered_toc, rendered_chapters, rendered_appendices]:
            self.assertNotIn("<script>", fragment)
            self.assertIn("&lt;script&gt;", fragment)

if __name__ == '__main__':
    unittest.main()
