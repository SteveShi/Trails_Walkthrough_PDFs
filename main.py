#!/usr/bin/env python3
"""
《英雄传说：轨迹系列》高画质排版全要素攻略生成系统 - CLI 入口
Trails Walkthrough PDF Generator CLI
"""

import argparse
import os
import sys
from src.builder import build_sora_1st_html
from src.pdf_exporter import export_html_to_pdf


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="《英雄传说：轨迹系列》100% 全要素白金攻略 PDF 自动化生成器"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="批量生成全部 12 部轨迹作品独立 PDF"
    )
    parser.add_argument(
        "--game", "-g",
        dest="game",
        default=None,
        help="指定生成某部作品 (如: sora_1st, sora_2nd, zero, ao, sen1~4, hajimari, kuro1~2, kai)"
    )
    parser.add_argument(
        "--output", "-o",
        dest="output",
        default=None,
        help="输出 PDF 文件路径 (默认根据作品名称生成在 dist/ 下)"
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="仅生成 JRPG 终端风格 HTML，不调用 Chrome 渲染导出 PDF"
    )
    args = parser.parse_args(argv)

    if args.all:
        from src.batch_runner import run_batch
        return run_batch()

    if args.game:
        from src.games_config import GAMES_CONFIG
        from src.universal_builder import render_game_html
        cfg_matches = [g for g in GAMES_CONFIG if g["id"] == args.game]
        if not cfg_matches:
            print(f"错误: 未找到作品标识 '{args.game}'。可选列表: {[g['id'] for g in GAMES_CONFIG]}", file=sys.stderr)
            return 1
        cfg = cfg_matches[0]
        css_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates/style.css"))
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        html_content = render_game_html(cfg, css_content)
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"build/{cfg['id']}.html"))
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[{cfg['title']}] HTML 已生成: {html_path}")
        if args.html_only:
            return 0
        out_pdf = os.path.abspath(args.output) if args.output else os.path.abspath(os.path.join(os.path.dirname(__file__), cfg["output_pdf"]))
        success = export_html_to_pdf(html_path, out_pdf)
        if success and os.path.exists(out_pdf):
            size_mb = os.path.getsize(out_pdf) / (1024 * 1024)
            print(f"[{cfg['title']}] PDF 导出成功: {out_pdf} ({size_mb:.2f} MB)")
            return 0
        return 1

    print("=== 开始生成《空之轨迹 the 1st 重制版》100% 全要素白金攻略 PDF ===")
    default_out_pdf = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "dist/空之轨迹_the_1st_重制版_100全要素详细攻略.pdf")
    )
    out_pdf = os.path.abspath(args.output) if args.output else default_out_pdf

    print("[1/2] 正在解析数据并构建 JRPG 游击士终端风格 HTML...")
    html_path = build_sora_1st_html()
    print(f"      HTML 已生成: {html_path}")

    if args.html_only:
        print("      已跳过 PDF 导出 (--html-only)")
        return 0

    print("[2/2] 正在调用 Chrome Headless 引擎渲染矢量 A4 PDF...")
    success = export_html_to_pdf(html_path, out_pdf)

    if success and os.path.exists(out_pdf):
        size_mb = os.path.getsize(out_pdf) / (1024 * 1024)
        print(f"      PDF 导出成功: {out_pdf}")
        print(f"      文件体积: {size_mb:.2f} MB")
        return 0
    else:
        print("      PDF 导出失败，请检查 Chrome 日志！", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
