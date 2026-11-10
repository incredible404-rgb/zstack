#!/usr/bin/env python3
"""Maintainer utility for zstack: validate repository skills & diff against local ~/.agents/skills.

Zero third-party dependencies. Safe and read-only by default.

Usage:
  python scripts/sync_local.py --validate          # Check frontmatter, budgets (<=500B desc, <=500 lines), and plugin manifests
  python scripts/sync_local.py                     # Compare repo skills/ against local ~/.agents/skills/
  python scripts/sync_local.py --diff arena grill  # Show unified diff between local and repo versions
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
MAX_DESC_BYTES = 500
MAX_SKILL_LINES = 500
CORRUPT_TAG = re.compile(r"</(?:invoke|content|parameter)>|<parameter\b", re.I)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not m:
        return None
    block = m.group(1)
    try:
        import yaml  # type: ignore
        d = yaml.safe_load(block)
        if isinstance(d, dict) and d.get("name") and d.get("description"):
            return {k: str(v) for k, v in d.items()}
        return None
    except ImportError:
        pass
    except Exception:
        return None
    out: dict[str, str] = {}
    cur: str | None = None
    for line in block.splitlines():
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if kv:
            cur = kv.group(1)
            val = kv.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            out[cur] = val
        elif cur and (line.startswith("  ") or line.startswith("\t")):
            out[cur] = (out[cur] + " " + line.strip()).strip()
    return out if out.get("name") and out.get("description") else None


def validate_repo() -> int:
    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not skill_dirs:
        print("ERROR: no skills found under skills/", file=sys.stderr)
        return 1

    print(f"Validating {len(skill_dirs)} skills in {SKILLS_DIR} ...")
    expected_manifest_paths: list[str] = []

    for sd in skill_dirs:
        expected_manifest_paths.append(f"./skills/{sd.name}")
        md = sd / "SKILL.md"
        if not md.is_file():
            errors.append(f"{sd.name}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        fm = parse_frontmatter(text)
        if not fm:
            errors.append(f"{sd.name}: invalid YAML frontmatter (missing name or description)")
            continue
        if fm["name"] != sd.name:
            errors.append(f"{sd.name}: frontmatter name '{fm['name']}' != folder '{sd.name}'")
        desc_bytes = len(fm["description"].encode("utf-8"))
        status = "OK"
        if desc_bytes > MAX_DESC_BYTES:
            errors.append(f"{sd.name}: description is {desc_bytes}B (limit {MAX_DESC_BYTES}B)")
            status = "OVER_DESC"
        if lines > MAX_SKILL_LINES:
            errors.append(f"{sd.name}: SKILL.md has {lines} lines (limit {MAX_SKILL_LINES})")
            status = "OVER_LINES"
        if CORRUPT_TAG.search(text):
            errors.append(f"{sd.name}: contains leaked tool XML tags")
            status = "BAD_TAG"
        print(f"  [{status}] {sd.name:28} desc={desc_bytes:>3}B  lines={lines:>3}")

    plugin_json = REPO / ".claude-plugin" / "plugin.json"
    pj_name, pj_ver = None, None
    if plugin_json.is_file():
        pj = json.loads(plugin_json.read_text(encoding="utf-8"))
        pj_name, pj_ver = pj.get("name"), pj.get("version")
        listed = sorted(pj.get("skills") or [])
        if listed != expected_manifest_paths:
            errors.append(f".claude-plugin/plugin.json skills mismatch: {listed} vs {expected_manifest_paths}")
    else:
        errors.append("missing .claude-plugin/plugin.json")

    mkt_json = REPO / ".claude-plugin" / "marketplace.json"
    if mkt_json.is_file():
        mj = json.loads(mkt_json.read_text(encoding="utf-8"))
        plugins = mj.get("plugins") or []
        if not plugins or plugins[0].get("name") != pj_name or plugins[0].get("source") != "./":
            errors.append(".claude-plugin/marketplace.json plugins[0] must match plugin.json name and source './'")
    else:
        errors.append("missing .claude-plugin/marketplace.json")

    root_plugin = REPO / "plugin.json"
    if root_plugin.is_file():
        rp = json.loads(root_plugin.read_text(encoding="utf-8"))
        if not rp.get("$schema") or rp.get("name") != pj_name or rp.get("version") != pj_ver:
            errors.append("root plugin.json must have $schema and match name/version in .claude-plugin/plugin.json")
    else:
        errors.append("missing root plugin.json")

    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("\nAll skills & plugin manifests passed validation.")
    return 0


def compare_local(local_root: pathlib.Path, diff_targets: list[str] | None) -> int:
    if not local_root.is_dir():
        print(f"Local skills directory not found: {local_root}", file=sys.stderr)
        return 1
    targets = set(diff_targets) if diff_targets else None
    for sd in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        if targets and sd.name not in targets:
            continue
        loc = (local_root / sd.name).resolve()
        repo_md = sd / "SKILL.md"
        loc_md = loc / "SKILL.md"
        if not loc_md.is_file():
            print(f"{sd.name:28} local=MISSING")
            continue
        r_lines = repo_md.read_text(encoding="utf-8").splitlines()
        l_lines = loc_md.read_text(encoding="utf-8", errors="replace").splitlines()
        same = r_lines == l_lines
        delta = sum(1 for x in difflib.ndiff(r_lines, l_lines) if x.startswith(("+ ", "- ")))
        print(f"{sd.name:28} {'IDENTICAL' if same else f'ADAPTED/DIFF ({delta} changed lines)'}  (repo={len(r_lines)}L, local={len(l_lines)}L)")
        if diff_targets is not None and not same:
            diff = difflib.unified_diff(
                r_lines, l_lines,
                fromfile=f"zstack/skills/{sd.name}/SKILL.md",
                tofile=f"local/{sd.name}/SKILL.md",
                lineterm="",
            )
            print("\n".join(diff))
            print()
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate zstack skills or compare against local ~/.agents/skills.")
    ap.add_argument("--validate", action="store_true", help="Validate YAML frontmatter, budgets, and plugin manifests")
    ap.add_argument("--local-dir", type=pathlib.Path, default=pathlib.Path.home() / ".agents" / "skills")
    ap.add_argument("--diff", nargs="*", default=None, metavar="SKILL", help="Print unified diff for all or named skills")
    args = ap.parse_args()

    if args.validate:
        sys.exit(validate_repo())
    sys.exit(compare_local(args.local_dir, args.diff))


if __name__ == "__main__":
    main()
