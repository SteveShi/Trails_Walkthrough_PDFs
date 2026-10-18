import os
import unittest
from src.builder import build_sora_1st_html
from src.pdf_exporter import export_html_to_pdf, CHROME_BIN

class TestPdfExporter(unittest.TestCase):
    def test_chrome_binary_exists(self):
        self.assertTrue(os.path.exists(CHROME_BIN), f"Chrome binary not found at {CHROME_BIN}")

    def test_export_pdf(self):
        sample_html = build_sora_1st_html()
        out_pdf = "/Users/steve/Downloads/Trails_Walkthrough_PDFs/dist/test_sample.pdf"
        if os.path.exists(out_pdf):
            try:
                os.remove(out_pdf)
            except OSError:
                pass
        success = export_html_to_pdf(sample_html, out_pdf)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_pdf))
        self.assertTrue(os.path.getsize(out_pdf) > 50000) # At least 50KB for rich JRPG guide

if __name__ == '__main__':
    unittest.main()
