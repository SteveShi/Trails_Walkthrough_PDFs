import os
import subprocess

CHROME_BIN = os.environ.get("CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

def export_html_to_pdf(html_path: str, pdf_path: str, timeout: int = 60) -> bool:
    """使用 Headless Chrome 将 HTML 转译并渲染为像素级矢量 PDF"""
    if not os.path.exists(CHROME_BIN):
        raise FileNotFoundError(f"Google Chrome not found at {CHROME_BIN}")
    
    abs_html = os.path.abspath(html_path)
    if not os.path.exists(abs_html):
        raise FileNotFoundError(f"Source HTML file not found at {abs_html}")

    abs_pdf = os.path.abspath(pdf_path)
    parent_dir = os.path.dirname(abs_pdf)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_pdf}",
        f"file://{abs_html}"
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return res.returncode == 0 and os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 0
    except Exception as e:
        print(f"Error exporting PDF: {e}")
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        success = export_html_to_pdf(sys.argv[1], sys.argv[2])
        print(f"Export result: {success}")
    elif len(sys.argv) == 2:
        out = sys.argv[1].replace(".html", ".pdf")
        success = export_html_to_pdf(sys.argv[1], out)
        print(f"Export result: {success} -> {out}")
    else:
        print("Usage: python3 -m src.pdf_exporter <input_html> [output_pdf]")
