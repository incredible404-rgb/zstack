#!/usr/bin/env python3
"""Example architecture-diagram builder: renders zstack's 4-phase workflow onto a single HTML sheet.

Usage:
  python -X utf8 examples/zstack_overview.py [out.html]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from svgkit import CSS, JS, WARN, Fig, default_private_terms, privacy_scan, write_page  # noqa: E402


def build_overview() -> str:
    f = Fig("ov", 1360, 420, "zstack multi-agent workflow overview")
    f.sheet()

    # Zones
    f.zone(20, 20, 410, 230, "ui", "L1", "对齐与设计（Align & Design）", "先定 What，再动手")
    f.zone(475, 20, 410, 230, "run", "L2", "实现与验证（Execute & Verify）", "紧反馈闭环 + 异厂复核")
    f.zone(930, 20, 410, 230, "gov", "L3", "复盘与清债（Retro & Prune）", "双向门当场改，单向门入账")
    f.zone(20, 275, 1320, 125, "law", "L0", "薄指针底座与三层记忆（Thin Core & Memory Routing）", "常驻层守预算，细节按需加载")

    # L1 boxes
    f.box(38, 58, 178, 76, "grill", ["三问一轮设计树", "严格拆开 What / How", "收尾产出目标简报"], flows="manual")
    f.box(234, 58, 178, 76, "arena", ["异厂模型并行出草图", "只读盲评打分选底版", "手工嫁接落选稿长处"], flows="manual model")
    f.box(38, 152, 374, 78, "owner-mode", ["目的倒推：本人的域一次问清，可逆步骤直接做到底", "帕累托前沿：一劳永逸（脚本/钩子）+ 循环清扫（做减法）"], flows="all")

    # L2 boxes
    f.box(493, 58, 178, 76, "diagnosing-bugs", ["先建可泛红的紧闭环", "最小化复现后再列假设", "修前先冻结回归测试"], flows="auto")
    f.box(689, 58, 178, 76, "windows-shell", ["先探测 bash / pwsh 7", "跨壳逻辑一律写脚本", "防编码乱码与 CRLF 污染"], flows="auto")
    f.box(493, 152, 374, 78, "REVIEW.md（异厂复核）", ["正确性 / 安全与数据 / 目标对齐 三遍独立审查", "P0 阻断 · P1 交付前修 · P2 限额记录，不报钩子已拦项"], flows="gov model")

    # L3 boxes
    f.box(948, 58, 178, 76, "retro", ["锚定会话真实卡点时刻", "9 类归因 + 单/双向门", "双向门当场修并验绿"], flows="gov")
    f.box(1144, 58, 178, 76, "skill-pruning", ["45 天真实读取会话证据", "简介 <= 500B 触发预算", "撤冗余、清债"], flows="gov", chip="台账", chip_on_line=2)
    f.box(948, 152, 374, 78, "writing-for-agents & prompting", ["常驻指针只写触发分支，正文分层披露", "可移植任务合同与供应商能力适配层彻底解耦"], flows="sync")

    # L0 chevrons / boxes
    f.chevron(38, 312, 400, 68, "0. Repo SSOT", ["AGENTS.md · 架构与术语表", "0 检索延迟，现行代码与规则唯一权威"], flows="all", first=True)
    f.chevron(452, 312, 420, 68, "1. 提炼记忆层", ["跨项目偏好卡 · 实体卡 · 经验卡", "按场景召回，被推翻旧卡原地覆盖"], flows="sync")
    f.chevron(886, 312, 436, 68, "2. 原始会话记录", ["精确报错原文 · CLI 参数 · 历史 diff", "2-4 精确词全文检索，重调前先查前科"], flows="auto")

    # Edges between zones
    f.edge([(412, 96), (493, 96)], flows="manual", label="目标合同", lx=452, ly=89, anchor="middle")
    f.edge([(867, 96), (948, 96)], flows="gov", label="运行轨迹", lx=907, ly=89, anchor="middle")
    f.edge([(1135, 230), (1135, 262), (225, 262), (225, 230)], flows="sync", label="提炼回流指针与经验", lx=680, ly=258, anchor="middle")

    return f.render("zstack 四阶段工程工作流全景图")


def render_html() -> str:
    svg1 = build_overview()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>zstack 工作流全景图</title>
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <header class="titleblock">
    <div class="tb-main">
      <p class="tb-kicker">ARCHITECTURE SHEET · ZSTACK</p>
      <h1>zstack 个性化 Agent 工程工作流</h1>
      <p class="lede">把「对齐 What → 多模型擂台草图 → 紧闭环执行与异厂复核 → 会话复盘与技能清债」收成一套薄指针、可组合的跨客户端技能包。</p>
    </div>
    <dl class="tb-fields">
      <div><dt>范围</dt><dd>13 个技能 + 2 份核心模板</dd></div>
      <div><dt>客户端</dt><dd>Claude Code · Codex · Cursor · pi</dd></div>
      <div><dt>协议</dt><dd>MIT（含上游致谢 NOTICE）</dd></div>
      <div><dt>打码示例</dt><dd><span class="redact-chip">私有台账</span> 演示遮罩样式</dd></div>
    </dl>
  </header>

  <section id="fig-overview">
    <div class="sec-head"><span class="fig-no">FIG 01</span><h2>四层闭环与流向筛选</h2></div>
    <p class="intro">点击下方按钮按驱动方式筛选流向；暗色主题跟随系统自动切换。</p>
    <div class="controls" role="toolbar" aria-label="按流向筛选">
      <button class="flt" data-flt="all" aria-pressed="true">全部</button>
      <button class="flt" data-flt="manual" aria-pressed="false"><span class="sw sw-manual"></span>人工对齐</button>
      <button class="flt" data-flt="auto" aria-pressed="false"><span class="sw sw-auto"></span>闭环执行</button>
      <button class="flt" data-flt="model" aria-pressed="false"><span class="sw sw-model"></span>异厂模型</button>
      <button class="flt" data-flt="gov" aria-pressed="false"><span class="sw sw-gov"></span>复盘清债</button>
      <button class="flt" data-flt="sync" aria-pressed="false"><span class="sw sw-sync"></span>经验沉淀</button>
    </div>
    <p class="scroll-hint">小屏可左右滑动查看完整图纸 →</p>
    <div class="figscroll">{svg1}</div>
  </section>
</main>
<script>{JS}</script>
</body>
</html>
"""


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out/zstack-overview.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    html_text = render_html()
    if WARN:
        for w in WARN:
            print(w, file=sys.stderr)
        sys.exit(1)
    leaks = privacy_scan(html_text, default_private_terms())
    if leaks:
        print(f"Privacy scan hits: {leaks}", file=sys.stderr)
        sys.exit(1)
    write_page(out, html_text)
    print(f"OK: wrote {out} ({len(html_text)} chars), 0 warnings, 0 privacy hits.")


if __name__ == "__main__":
    main()
