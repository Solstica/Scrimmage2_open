#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/"config/project.json"
MAIN=ROOT/"paper/main.tex"

def main():
    ap=argparse.ArgumentParser(description="初始化比赛题目数（当前模板支持1-4问）")
    ap.add_argument("questions",type=int,choices=range(1,5))
    ap.add_argument("--name")
    a=ap.parse_args()
    cfg=json.loads(CFG.read_text(encoding="utf-8"))
    if a.name: cfg["project_name"]=a.name
    for m in cfg["modules"]:
        if re.fullmatch(r"q[1-4]",m["key"]):
            m["active"]=int(m["key"][1:])<=a.questions
    CFG.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    text=MAIN.read_text(encoding="utf-8")
    for i in range(1,5):
        line=rf"\input{{../modules/{i*10+10:02d}_q{i}/paper/q{i}.tex}}"
        # canonical module numbers are 20,30,40,50
        line=rf"\input{{../modules/{10+i*10:02d}_q{i}/paper/q{i}.tex}}"
        active=i<=a.questions
        text=re.sub(rf"^%?\s*\\input\{{\.\./modules/{10+i*10:02d}_q{i}/paper/q{i}\.tex\}}$",
                    line if active else "% "+line,text,flags=re.M)
    MAIN.write_text(text,encoding="utf-8")
    print(f"已设置为 {a.questions} 问。请在创建 feature 分支/worktree 之前提交本次初始化修改。")

if __name__=="__main__": main()
