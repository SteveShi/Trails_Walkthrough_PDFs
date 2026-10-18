"""
轨迹系列 12 部作品全要素攻略 PDF 批处理生成引擎
"""

import os
import sys
import time
import subprocess
from src.games_config import GAMES_CONFIG
from src.universal_builder import render_game_html
from src.pdf_exporter import export_html_to_pdf

def get_pdf_page_count(pdf_path: str) -> int:
    """获取 PDF 总页数 (优先匹配 /Count，兼容未压缩的 /Type /Page)"""
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        counts = [int(c) for c in re.findall(rb'/Count\s+(\d+)', content)]
        if counts:
            return max(counts)
        type_pages = len(re.findall(rb'/Type\s*/Page\b', content))
        if type_pages > 0:
            return type_pages
    except Exception:
        pass
    return -1

def run_batch():
    print("=" * 70)
    print("      🚀 轨迹系列 12 部全要素白金攻略 PDF 自动化生成引擎 🚀")
    print("=" * 70)

    css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates/style.css"))
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../build"))
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../dist"))
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(dist_dir, exist_ok=True)

    results = []
    total_start = time.time()

    for idx, cfg in enumerate(GAMES_CONFIG, start=1):
        gid = cfg["id"]
        title = cfg["title"]
        out_pdf = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", cfg["output_pdf"]))
        html_file = os.path.join(build_dir, f"{gid}.html")

        print(f"\n[{idx}/12] 正在生成《{title}》...")
        t0 = time.time()

        # 如果是 sora_1st，我们优先保留此前经过深度解析定制的最高清版本，或用 universal_builder 统一维护
        # 无论哪种，都确保输出高质量完整的 PDF
        if gid == "sora_1st" and os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 5000000:
            pages = get_pdf_page_count(out_pdf)
            size_mb = os.path.getsize(out_pdf) / (1024 * 1024)
            print(f"      ✅ 标杆首作《{title}》已就绪 (页数: {pages}页, 体积: {size_mb:.2f} MB)")
            results.append({
                "index": idx,
                "title": title,
                "pdf": out_pdf,
                "pages": pages,
                "size_mb": size_mb,
                "success": True,
                "duration": 0
            })
            continue

        # 1. 渲染 HTML
        html_content = render_game_html(cfg, css_content)
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 2. 导出 PDF
        success = export_html_to_pdf(html_file, out_pdf)
        elapsed = time.time() - t0

        if success and os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 500000:
            pages = get_pdf_page_count(out_pdf)
            size_mb = os.path.getsize(out_pdf) / (1024 * 1024)
            print(f"      🎉 成功导出: {os.path.basename(out_pdf)}")
            print(f"         页数: {pages} 页 | 体积: {size_mb:.2f} MB | 耗时: {elapsed:.1f} 秒")
            results.append({
                "index": idx,
                "title": title,
                "pdf": out_pdf,
                "pages": pages,
                "size_mb": size_mb,
                "success": True,
                "duration": elapsed
            })
        else:
            print(f"      ❌ 导出失败: 《{title}》", file=sys.stderr)
            results.append({
                "index": idx,
                "title": title,
                "pdf": out_pdf,
                "pages": 0,
                "size_mb": 0,
                "success": False,
                "duration": elapsed
            })

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print(f"✨ 全套 12 部作品批处理完成！总耗时: {total_elapsed:.1f} 秒")
    print("=" * 70)
    print(f"{'序号':<4} | {'作品名称':<36} | {'页数':<6} | {'文件大小':<10} | {'状态'}")
    print("-" * 70)
    
    total_pages = 0
    all_success = True
    for r in results:
        status_str = "✅ 成功" if r["success"] else "❌ 失败"
        if not r["success"]:
            all_success = False
        total_pages += r["pages"] if r["pages"] > 0 else 0
        print(f" {r['index']:<3} | {r['title']:<34} | {r['pages']:<6} | {r['size_mb']:<6.2f} MB | {status_str}")

    print("-" * 70)
    print(f"汇总统计: 12 部作品攻略总页数: {total_pages} 页 | 全部成功: {all_success}")
    print("=" * 70)
    return 0 if all_success else 1

if __name__ == '__main__':
    sys.exit(run_batch())
