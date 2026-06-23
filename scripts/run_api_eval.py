#!/usr/bin/env python3
"""End-to-end QA evaluation against the live /ask API.

Sends every labelled case in eval/eval_dataset.py to the API, records the
response, determines expected vs. actual repository, computes category-wise
accuracy, and writes:
  * eval/results/evaluation_report.csv
  * eval/results/evaluation_summary.md

Usage:
    # start the API first (in another shell):
    #   PYTHONPATH=. uvicorn app.main:app --port 8000
    python scripts/run_api_eval.py
    API_URL=http://127.0.0.1:8000/ask python scripts/run_api_eval.py
"""
from __future__ import annotations

import csv
import json
import os
import sys
import urllib.request
from collections import Counter

from eval.eval_dataset import EVAL_CASES

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000/ask")
RESULTS_DIR = "eval/results"
CSV_PATH = os.path.join(RESULTS_DIR, "evaluation_report.csv")
MD_PATH = os.path.join(RESULTS_DIR, "evaluation_summary.md")

# doc_type -> repository bucket
REPO_BY_DOCTYPE = {
    "act": "legal", "sanhita": "legal",
    "recovery": "recovery",
    "decision_tree": "decision_tree",
    "sop": "sop", "manual": "manual", "advisory": "advisory",
    "playbook": "playbook", "circular": "circular",
}


def _ask(query: str) -> dict:
    data = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _actual_repo(resp: dict) -> str:
    if resp.get("refused"):
        return "refused"
    if resp.get("abstained"):
        return "abstained"
    cites = resp.get("citations") or []
    if not cites:
        return "none"
    repos = Counter(REPO_BY_DOCTYPE.get(c.get("doc_type", ""), "other") for c in cites)
    return repos.most_common(1)[0][0]


def _passed(case, resp, actual_repo: str) -> bool:
    if case.category == "refusal":
        return bool(resp.get("refused"))
    if resp.get("refused") or resp.get("abstained"):
        return False
    cites = resp.get("citations") or []
    if case.category == "decision_tree" and case.expected_doc:
        return any(case.expected_doc in (c.get("doc_id") or "") for c in cites)
    return actual_repo == case.expected_repo


def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    try:
        _ask("healthcheck ping")
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot reach API at {API_URL}: {exc}")
        print("Start it first:  PYTHONPATH=. uvicorn app.main:app --port 8000")
        return 2

    rows = []
    for case in EVAL_CASES:
        try:
            resp = _ask(case.query)
        except Exception as exc:  # noqa: BLE001
            resp = {"answer": f"<error: {exc}>", "citations": [], "confidence": "",
                    "refused": False, "abstained": False}
        actual = _actual_repo(resp)
        ok = _passed(case, resp, actual)
        cites = resp.get("citations") or []
        rows.append({
            "category": case.category,
            "query": case.query,
            "expected_repo": case.expected_repo,
            "expected_doc": case.expected_doc or "",
            "actual_repo": actual,
            "cited_docs": "|".join(sorted({c.get("doc_id", "") for c in cites})),
            "confidence": resp.get("confidence", ""),
            "refused": resp.get("refused", False),
            "abstained": resp.get("abstained", False),
            "n_citations": len(cites),
            "pass": "PASS" if ok else "FAIL",
            "answer": (resp.get("answer", "") or "").replace("\n", " ")[:300],
        })

    _write_csv(rows)
    metrics = _metrics(rows)
    _write_summary(rows, metrics)
    _print_metrics(metrics)
    return 0


def _metrics(rows) -> dict:
    def acc(subset):
        return (sum(1 for r in subset if r["pass"] == "PASS") / len(subset)) if subset else 0.0
    by_cat = {}
    for cat in ("legal", "recovery", "decision_tree", "refusal"):
        by_cat[cat] = acc([r for r in rows if r["category"] == cat])
    return {
        "overall": acc(rows),
        "legal": by_cat["legal"],
        "recovery": by_cat["recovery"],
        "decision_tree": by_cat["decision_tree"],
        "refusal": by_cat["refusal"],
        "total": len(rows),
        "passed": sum(1 for r in rows if r["pass"] == "PASS"),
    }


def _write_csv(rows) -> None:
    fields = ["category", "query", "expected_repo", "expected_doc", "actual_repo",
              "cited_docs", "confidence", "refused", "abstained", "n_citations",
              "pass", "answer"]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _root_causes(failed) -> list[str]:
    notes = []
    refused_valid = [r for r in failed if r["category"] != "refusal" and r["refused"]]
    if refused_valid:
        notes.append(f"- **Guardrail over-refusal:** {len(refused_valid)} valid "
                     "query(ies) refused — domain vocabulary missing the relevant terms.")
    abstained = [r for r in failed if r["abstained"]]
    if abstained:
        notes.append(f"- **Abstentions:** {len(abstained)} query(ies) abstained — "
                     "retrieval returned nothing above the relevance floor.")
    wrong_repo = [r for r in failed if r["category"] != "refusal"
                  and not r["refused"] and not r["abstained"]]
    if wrong_repo:
        notes.append(f"- **Retrieval mis-routing:** {len(wrong_repo)} query(ies) "
                     "retrieved the wrong repository/doc (capability routing or "
                     "lexical ranking under the dev embedder).")
    leaked = [r for r in failed if r["category"] == "refusal" and not r["refused"]]
    if leaked:
        notes.append(f"- **Guardrail under-refusal:** {len(leaked)} unrelated "
                     "query(ies) were answered instead of refused.")
    return notes or ["- No failures."]


def _write_summary(rows, m) -> None:
    failed = [r for r in rows if r["pass"] == "FAIL"]
    lines = []
    lines.append("# Evaluation Summary — Cybercrime Investigation Companion Bot\n")
    lines.append(f"Endpoint: `{API_URL}`  |  Cases: **{m['total']}**  |  "
                 f"Passed: **{m['passed']}/{m['total']}**\n")
    lines.append("## Overall metrics\n")
    lines.append("| Metric | Accuracy |")
    lines.append("|---|---|")
    lines.append(f"| Overall | {m['overall']*100:.1f}% |")
    lines.append(f"| Legal | {m['legal']*100:.1f}% |")
    lines.append(f"| Recovery | {m['recovery']*100:.1f}% |")
    lines.append(f"| Decision-tree | {m['decision_tree']*100:.1f}% |")
    lines.append(f"| Refusal | {m['refusal']*100:.1f}% |\n")

    lines.append("## Category-wise results\n")
    lines.append("| Category | Passed | Total |")
    lines.append("|---|---|---|")
    for cat in ("legal", "recovery", "decision_tree", "refusal"):
        sub = [r for r in rows if r["category"] == cat]
        p = sum(1 for r in sub if r["pass"] == "PASS")
        lines.append(f"| {cat} | {p} | {len(sub)} |")
    lines.append("")

    lines.append("## Failed queries\n")
    if failed:
        lines.append("| Category | Query | Expected | Actual | Cited |")
        lines.append("|---|---|---|---|---|")
        for r in failed:
            lines.append(f"| {r['category']} | {r['query']} | "
                         f"{r['expected_repo']}{('/'+r['expected_doc']) if r['expected_doc'] else ''} | "
                         f"{r['actual_repo']} | {r['cited_docs']} |")
    else:
        lines.append("None — all cases passed. ✅")
    lines.append("")

    lines.append("## Root cause analysis\n")
    lines.extend(_root_causes(failed))
    lines.append("")
    lines.append("## Retrieval issues\n")
    rt = [r for r in failed if r["category"] != "refusal" and not r["refused"] and not r["abstained"]]
    if rt:
        for r in rt:
            lines.append(f"- `{r['query']}` → expected **{r['expected_repo']}"
                         f"{('/'+r['expected_doc']) if r['expected_doc'] else ''}**, "
                         f"got **{r['actual_repo']}** ({r['cited_docs'] or 'no citations'}).")
        lines.append("\n*Primary lever: the dev profile uses the lexical HashingEmbedder; "
                     "switching `EMBEDDER=bge` (BGE-M3 semantic) sharpens ranking across "
                     "overlapping documents without code changes.*")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Guardrail issues\n")
    g_over = [r for r in failed if r["category"] != "refusal" and r["refused"]]
    g_under = [r for r in failed if r["category"] == "refusal" and not r["refused"]]
    if g_over:
        lines.append("**Over-refusal (valid queries refused):**")
        for r in g_over:
            lines.append(f"- `{r['query']}`")
    if g_under:
        lines.append("**Under-refusal (unrelated queries answered):**")
        for r in g_under:
            lines.append(f"- `{r['query']}` → cited {r['cited_docs']}")
    if not g_over and not g_under:
        lines.append("- None — guardrail correctly admitted all valid queries and "
                     "refused all unrelated ones.")
    lines.append("")

    with open(MD_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _print_metrics(m) -> None:
    print("\n================ EVALUATION METRICS ================")
    print(f"  Overall accuracy:        {m['overall']*100:.1f}%  ({m['passed']}/{m['total']})")
    print(f"  Legal accuracy:          {m['legal']*100:.1f}%")
    print(f"  Recovery accuracy:       {m['recovery']*100:.1f}%")
    print(f"  Decision-tree accuracy:  {m['decision_tree']*100:.1f}%")
    print(f"  Refusal accuracy:        {m['refusal']*100:.1f}%")
    print("===================================================")
    print(f"  CSV:     {CSV_PATH}")
    print(f"  Summary: {MD_PATH}")


if __name__ == "__main__":
    sys.exit(main())
