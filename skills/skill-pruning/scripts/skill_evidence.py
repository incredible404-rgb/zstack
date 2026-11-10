#!/usr/bin/env python3
"""技能精简证据采集（0 token，只读）：统计本机各技能近 N 天会话命中数、简介字节、正文行数、frontmatter 与标签卫生。

用法：
  python -I skill_evidence.py [--days 45] [--skills-dir ~/.agents/skills] [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import time

H = pathlib.Path.home()
DEFAULT_DIRS = [
    H / ".agents/skills",
    H / ".claude/skills",
    H / ".codex/skills",
    H / ".cursor/skills",
    H / ".pi/agent/skills",
]
OV_SKILLS = H / "data/viking/default"
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?", re.S)
SKILL_PATH = re.compile(r"skills[\\/]+([a-z0-9-]+)[\\/]+SKILL\.md")
CLAUDE_CALL = re.compile(r'"name":"Skill","input":\{"skill":"(?:[\w-]+:)?([a-z0-9-]+)"')
CORRUPT_TAG = re.compile(r"</(?:invoke|content|parameter)>|<parameter\b", re.I)
MAX_DESC_BYTES = 500
MAX_SKILL_LINES = 500
# 单次会话出现超过该数量的不同技能路径，通常是在盘点目录，不计入真实触发
LISTING = 8


def _parse_frontmatter_fallback(raw: str) -> dict | None:
    """无 PyYAML 时的轻量 frontmatter 解析回退。"""
    out: dict[str, str] = {}
    cur_key: str | None = None
    for line in raw.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            cur_key = m.group(1)
            val = m.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            out[cur_key] = val
        elif cur_key and (line.startswith("  ") or line.startswith("\t")):
            out[cur_key] = (out[cur_key] + " " + line.strip()).strip()
    return out if out.get("name") and out.get("description") else None


def inspect_skill(p: pathlib.Path):
    t = p.read_text(encoding="utf-8", errors="replace")
    lines = len(t.splitlines())
    bad_tag = bool(CORRUPT_TAG.search(t))
    m = re.match(r"---\r?\n(.*?)\r?\n---", t, re.S)
    fm = None
    if m:
        block = m.group(1)
        try:
            import yaml  # type: ignore
            d = yaml.safe_load(block)
            if isinstance(d, dict) and d.get("name") and d.get("description"):
                fm = d
        except ImportError:
            fm = _parse_frontmatter_fallback(block)
        except Exception:
            fm = None
    return fm, lines, bad_tag


def transcripts(since: float):
    roots = [(H / ".codex/sessions", SKILL_PATH), (H / ".claude/projects", CLAUDE_CALL)]
    roots += [(H / r, SKILL_PATH) for r in (".pi", ".cursor", ".omp", ".grok", ".dsh", ".hermes")]
    for root, rx in roots:
        if not root.exists():
            continue
        for f in root.rglob("*.jsonl"):
            if "skills" in f.parts:
                continue
            try:
                if f.stat().st_mtime >= since:
                    yield f, rx
            except OSError:
                pass


def discover_skills(
    extra_dir: pathlib.Path | None,
    library_json: pathlib.Path | None = None,
) -> tuple[dict[str, pathlib.Path], dict[str, list[str] | str]]:
    found_paths: dict[str, pathlib.Path] = {}
    agents: dict[str, list[str] | str] = {}

    if extra_dir is not None:
        if extra_dir.is_dir():
            for sub in sorted(extra_dir.iterdir()):
                md = sub / "SKILL.md"
                if md.is_file():
                    found_paths[sub.name] = md
                    agents[sub.name] = extra_dir.name
        return found_paths, agents

    env_lib = os.environ.get("SKILL_LIBRARY_JSON")
    lib_json = library_json or (pathlib.Path(env_lib).expanduser() if env_lib else None)
    if lib_json and lib_json.is_file():
        lib_skills_dir = lib_json.parent / "library" / "skills"
        try:
            lib = json.loads(lib_json.read_text(encoding="utf-8"))
            for s in lib.get("skills", []):
                sname = s["name"]
                agents[sname] = s.get("agents") or []
                cand = lib_skills_dir / sname / "SKILL.md"
                if cand.is_file():
                    found_paths[sname] = cand
        except (OSError, ValueError, KeyError, TypeError):
            pass

    scan_dirs = DEFAULT_DIRS
    for d in scan_dirs:
        if not d or not d.is_dir():
            continue
        for sub in sorted(d.iterdir()):
            md = sub / "SKILL.md"
            if md.is_file() and sub.name not in found_paths:
                found_paths[sub.name] = md
                agents.setdefault(sub.name, d.parent.name.lstrip(".") or "local")

    return found_paths, agents


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--skills-dir", type=pathlib.Path, default=None)
    ap.add_argument("--library-json", type=pathlib.Path, default=None, help="Optional skill router library.json path")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    found_paths, agents = discover_skills(a.skills_dir, a.library_json)
    names = set(found_paths) | set(agents)

    used = {n: 0 for n in names}
    for f, rx in transcripts(time.time() - a.days * 86400):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
            hits = {m.group(1) for m in rx.finditer(txt)} & names
        except OSError:
            continue
        if len(hits) <= LISTING:
            for n in hits:
                used[n] += 1

    rows = []
    for n in sorted(names):
        p = found_paths.get(n)
        fm, lines, bad_tag = inspect_skill(p) if p else (None, None, False)
        desc_b = len(str(fm["description"]).encode("utf-8")) if fm else None
        issues = []
        if not fm:
            issues.append("frontmatter 坏")
        if desc_b and desc_b > MAX_DESC_BYTES:
            issues.append(f"简介>{MAX_DESC_BYTES}B")
        if lines and lines > MAX_SKILL_LINES:
            issues.append(f"正文>{MAX_SKILL_LINES}行")
        if bad_tag:
            issues.append("残留标签")
        if p and OV_SKILLS.is_dir():
            for ov_p in OV_SKILLS.glob(f"**/skills/{n}/SKILL.md"):
                ov_fm, _, _ = inspect_skill(ov_p)
                ov_body = FRONTMATTER_RE.sub("", ov_p.read_text(encoding="utf-8", errors="replace")).replace("\r\n", "\n").strip()
                loc_body = FRONTMATTER_RE.sub("", p.read_text(encoding="utf-8", errors="replace")).replace("\r\n", "\n").strip()
                ov_desc = re.sub(r"\s+", " ", str((ov_fm or {}).get("description", ""))).strip()
                loc_desc = re.sub(r"\s+", " ", str((fm or {}).get("description", ""))).strip()
                if ov_body != loc_body or ov_desc != loc_desc:
                    issues.append("OV副本漂移")
        rows.append({
            "name": n,
            "sessions": used[n],
            "agents": agents.get(n, "local"),
            "desc_bytes": desc_b,
            "lines": lines,
            "frontmatter_ok": bool(fm),
            "issues": issues,
            "path": str(p) if p else None,
        })

    if a.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for r in rows:
        ag = r["agents"] if isinstance(r["agents"], str) else (",".join(r["agents"]) or "none")
        flag = f"  [{', '.join(r['issues'])}]" if r["issues"] else ""
        print(f"{r['name']:30} 会话={r['sessions']:<4} 简介={r['desc_bytes'] or '-':>5}B  行数={r['lines'] or '-':>4}  来源={ag}{flag}")


if __name__ == "__main__":
    main()
