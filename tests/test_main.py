import os
import tempfile
import unittest
from unittest.mock import patch
import main


class TestMainCli(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def test_main_html_only(self):
        exit_code = main.main(["--html-only"])
        self.assertEqual(exit_code, 0)
        build_html = os.path.join(os.path.dirname(__file__), "../build/sora_1st.html")
        self.assertTrue(os.path.exists(build_html))

    def test_main_custom_output(self):
        out_pdf = os.path.join(self.temp_dir.name, "custom_output.pdf")
        exit_code = main.main(["-o", out_pdf])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(out_pdf))
        self.assertGreater(os.path.getsize(out_pdf), 100000)

    @patch("main.export_html_to_pdf", return_value=False)
    def test_main_export_failure(self, mock_export):
        exit_code = main.main([])
        self.assertEqual(exit_code, 1)


if __name__ == '__main__':
    unittest.main()
