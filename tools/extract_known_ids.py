#!/usr/bin/env python3
"""Extract issue numbers, arXiv IDs, and snake_case names from the master catalog."""
from __future__ import annotations

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "catalog", "FAULT_MASTER_REFERENCE.zh.md")
IDX = os.path.join(ROOT, "catalog", "index")

HEADING = re.compile(r"^### ([A-Z][A-Z0-9-]*\.\d+) `([^`]+)`", re.MULTILINE)
ARXIV = re.compile(r"arXiv:(\d{4}\.\d{4,5})", re.IGNORECASE)
ISSUE = re.compile(
    r"https://github\.com/([^/\s]+)/([^/\s]+)/(?:issues|pull)/(\d+)"
)
BARE_HASH = re.compile(r"(?:^|[^\w])#(\d{3,6})\b")


def main():
    with open(MD, encoding="utf-8") as f:
        text = f.read()
    os.makedirs(IDX, exist_ok=True)

    names = []
    for fid, name in HEADING.findall(text):
        names.append(f"{fid}\t{name}")
    issues = sorted({f"{o}/{r}#{n}" for o, r, n in ISSUE.findall(text)})
    arxivs = sorted(set(ARXIV.findall(text)))

    def w(path, lines):
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + ("\n" if lines else ""))

    w(os.path.join(IDX, "known_names.txt"), names)
    w(os.path.join(IDX, "known_issue_ids.txt"), issues)
    w(os.path.join(IDX, "known_arxiv_ids.txt"), arxivs)
    print(f"names={len(names)} issues={len(issues)} arxiv={len(arxivs)}")


if __name__ == "__main__":
    main()
