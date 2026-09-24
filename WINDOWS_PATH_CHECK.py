#!/usr/bin/env python3
from pathlib import Path
import os,re,sys,collections
ROOT=Path(__file__).resolve().parent
LIMIT=259
RESERVED={*(f"COM{i}" for i in range(1,10)),*(f"LPT{i}" for i in range(1,10)),"CON","PRN","AUX","NUL"}
issues=[]; seen={}; longest=(0,None)
for p in ROOT.rglob("*"):
    rel=p.relative_to(ROOT).as_posix()
    full=str(p.resolve())
    if len(full)>longest[0]: longest=(len(full),rel)
    if len(full)>LIMIT: issues.append(f"PATH_TOO_LONG {len(full)} {rel}")
    for part in p.relative_to(ROOT).parts:
        if re.search(r'[<>:"\\|?*\x00-\x1f]',part) or part.endswith((' ','.')) or part.rstrip(' .').split('.')[0].upper() in RESERVED:
            issues.append(f"UNSAFE_NAME {rel}")
    key=rel.casefold()
    if key in seen and seen[key]!=rel: issues.append(f"CASE_COLLISION {seen[key]} :: {rel}")
    seen[key]=rel
print(f"PACKAGE_ROOT={ROOT}")
print(f"LONGEST_FULL_PATH={longest[0]} {longest[1]}")
print(f"LEGACY_MAX_PATH_BUDGET={LIMIT}")
if issues:
    print("FAIL")
    for x in issues: print(x)
    sys.exit(1)
print("PASS: Windows path/name/case checks passed")
