import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_chrome_binary() -> str | None:
    """探测 Chrome / Chromium 二进制可执行文件路径"""
    # 1. 优先检查环境变量
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin:
        if os.path.exists(env_bin) or shutil.which(env_bin):
            return env_bin

    # 2. 检查 macOS 标准安装路径
    macos_chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(macos_chrome):
        return macos_chrome

    # 3. 检查系统 PATH 中的候选可执行程序 (Linux/Windows/通用)
    for candidate in ("google-chrome", "chromium", "chrome"):
        found = shutil.which(candidate)
        if found:
            return found

    return None


CHROME_BIN = get_chrome_binary()


def export_html_to_pdf(html_path: str, pdf_path: str, timeout: int = 60, chrome_bin: str | None = None) -> bool:
    """使用 Headless Chrome 将 HTML 转译并渲染为像素级矢量 PDF"""
    bin_path = chrome_bin or CHROME_BIN or get_chrome_binary()
    if not bin_path or (not os.path.exists(bin_path) and not shutil.which(bin_path)):
        raise FileNotFoundError(f"Google Chrome binary not found: {bin_path}. Please set CHROME_BIN or install Chrome.")

    html_file = Path(html_path).resolve()
    if not html_file.exists():
        raise FileNotFoundError(f"Source HTML file not found at {html_file}")

    pdf_file = Path(pdf_path).resolve()
    pdf_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        bin_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_file}",
        html_file.as_uri()
    ]

    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        if res.returncode != 0:
            print(f"Error: Chrome headless export exited with code {res.returncode}:\n{res.stderr}", file=sys.stderr)
            return False

        if not (pdf_file.exists() and pdf_file.stat().st_size > 0):
            print(f"Error: PDF output missing or empty at {pdf_file}", file=sys.stderr)
            return False

        return True
    except Exception as e:
        print(f"Error exporting PDF: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    if len(sys.argv) > 2:
        success = export_html_to_pdf(sys.argv[1], sys.argv[2])
        print(f"Export result: {success}")
    elif len(sys.argv) == 2:
        out = sys.argv[1].replace(".html", ".pdf")
        success = export_html_to_pdf(sys.argv[1], out)
        print(f"Export result: {success} -> {out}")
    else:
        print("Usage: python3 -m src.pdf_exporter <input_html> [output_pdf]")
