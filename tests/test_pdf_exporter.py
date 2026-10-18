import os
import tempfile
import unittest
from pathlib import Path
from src.builder import build_sora_1st_html
from src.pdf_exporter import export_html_to_pdf, CHROME_BIN, get_chrome_binary


class TestPdfExporter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

    def test_chrome_binary_exists(self):
        self.assertIsNotNone(CHROME_BIN, "Chrome binary not found on system")
        self.assertTrue(os.path.exists(CHROME_BIN), f"Chrome binary not found at {CHROME_BIN}")

    def test_export_pdf(self):
        sample_html = build_sora_1st_html()
        out_pdf = os.path.join(self.temp_dir.name, "test_sample.pdf")

        success = export_html_to_pdf(sample_html, out_pdf)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_pdf))
        self.assertTrue(os.path.getsize(out_pdf) > 50000)  # At least 50KB for rich JRPG guide

    def test_export_nonexistent_html(self):
        out_pdf = os.path.join(self.temp_dir.name, "out.pdf")
        with self.assertRaises(FileNotFoundError):
            export_html_to_pdf("/nonexistent/file.html", out_pdf)

    def test_export_invalid_chrome_binary(self):
        sample_html = build_sora_1st_html()
        out_pdf = os.path.join(self.temp_dir.name, "out.pdf")
        with self.assertRaises(FileNotFoundError):
            export_html_to_pdf(sample_html, out_pdf, chrome_bin="/nonexistent/chrome_binary")


if __name__ == '__main__':
    unittest.main()
