#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, re, shutil, subprocess
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def tex_files(): return list((ROOT/"modules").glob("*/paper/*.tex"))+list((ROOT/"paper").glob("*.tex"))
def read(p): return p.read_text(encoding="utf-8",errors="replace")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--post-build",action="store_true"); a=ap.parse_args()
    errors=[]; warns=[]; labels=defaultdict(list)
    for p in tex_files():
        t=read(p)
        for token in ("??","[?]","TODO","FIXME"):
            if token in t: warns.append(f"{p.relative_to(ROOT)}: 发现 {token}")
        for x in re.findall(r"\\label\{([^}]+)\}",t): labels[x].append(p)
    for k,ps in labels.items():
        if len(ps)>1: errors.append(f"重复 label {k}: "+", ".join(str(p.relative_to(ROOT)) for p in ps))
    for reg in ROOT.glob("modules/*/results/registry.csv"):
        with reg.open(encoding="utf-8",newline="") as f:
            for row in csv.DictReader(f):
                if not row.get("result_id"): continue
                if row.get("used_in_paper","").strip().lower() in {"yes","true","1","y"}:
                    if row.get("status")!="FROZEN" or row.get("review_state")!="CHECKED":
                        errors.append(f"{reg.relative_to(ROOT)}: {row['result_id']} 已用于正文但不是 FROZEN+CHECKED")
    maintex=read(ROOT/"paper/main.tex")
    if "\\tableofcontents" not in maintex or "\\setcounter{page}{1}" not in maintex: errors.append("paper/main.tex 缺目录/正文页码重置")
    if a.post_build:
        log=ROOT/"paper/main.log"
        if log.exists() and "Overfull \\hbox" in read(log): warns.append("LaTeX 日志存在 Overfull \\hbox")
    for w in warns: print("[WARN]",w)
    for e in errors: print("[FAIL]",e)
    if not errors: print("[PASS] final preflight")
    raise SystemExit(1 if errors else 0)
if __name__=="__main__": main()
