#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 memory_papers.json 中全部论文 PDF 到当前目录。
用法：  python3 download_pdfs.py
说明：在你自己的电脑上运行（需联网）。脚本会跳过已下载的文件，可重复运行续传。
"""
import json, os, re, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "memory_papers.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (paper-archiver; contact: you@example.com)"}

def safe(name: str) -> str:
    name = re.sub(r"[^\w一-鿿 .\-]", "_", name)
    return re.sub(r"\s+", " ", name).strip()[:120]

def main():
    papers = json.load(open(DATA, encoding="utf-8"))["papers"]
    todo = [p for p in papers if p.get("pdf")]
    print(f"共 {len(papers)} 篇，其中 {len(todo)} 篇有 PDF 链接。")
    ok = skip = fail = 0
    for i, p in enumerate(todo, 1):
        fn = f"{p['id']}_{safe(p['title'])}.pdf"
        dest = os.path.join(HERE, fn)
        if os.path.exists(dest) and os.path.getsize(dest) > 1024:
            skip += 1; print(f"[{i}/{len(todo)}] 跳过(已存在) {fn}"); continue
        try:
            req = urllib.request.Request(p["pdf"], headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
                f.write(r.read())
            ok += 1; print(f"[{i}/{len(todo)}] 已下载 {fn}")
            time.sleep(3)  # 对 arXiv 友好，避免触发限流
        except Exception as e:
            fail += 1; print(f"[{i}/{len(todo)}] 失败 {p['id']}: {e}")
    print(f"\n完成：成功 {ok}，跳过 {skip}，失败 {fail}。")
    no_pdf = [p["id"] for p in papers if not p.get("pdf")]
    if no_pdf:
        print("以下条目无公开 PDF 链接，需手动获取：", ", ".join(no_pdf))

if __name__ == "__main__":
    main()
