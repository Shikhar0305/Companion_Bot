"""Run the regression gate in-process and report against the frozen baseline.

    python scripts/run_regression.py                 # measure + diff vs baseline
    python scripts/run_regression.py --update-baseline  # freeze current as baseline

Writes ``eval/reports/regression_report.{csv,md}`` and prints a summary. The
baseline lives at ``eval/baseline.json`` and is the contract the gate enforces
(see tests/test_regression_gate.py and docs Phase 2).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date

BASELINE_PATH = "eval/baseline.json"
REPORT_DIR = "eval/reports"


def _build_pipeline():
    os.environ.setdefault("CORPUS_ROOT", "data/corpus")
    from app.config import get_settings
    from app.deps import _build_services, _load_corpus, _seed_demo_kb
    from rag.graph import AnswerPipeline

    services = _build_services(get_settings())
    if _load_corpus(services) == 0:
        _seed_demo_kb(services)
    return AnswerPipeline(services), get_settings().embedder


def _write_reports(summary: dict, embedder: str) -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(os.path.join(REPORT_DIR, "regression_report.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["category", "failmode", "passed", "abstained", "cited_doc_types", "query"])
        for r in summary["results"]:
            w.writerow([r.case.category, r.case.failmode, r.passed, r.abstained,
                        "|".join(r.cited_doc_types), r.case.query])

    lines = [f"# Regression Report ({embedder} embedder, {date.today()})", "",
             f"**Overall: {summary['overall']:.1%}**  (n={summary['n']})", "",
             "| Category | Accuracy |", "|---|---|"]
    for cat, acc in sorted(summary["by_category"].items()):
        lines.append(f"| {cat} | {acc:.1%} |")
    lines += ["", "## Failing cases", ""]
    for r in summary["results"]:
        if not r.passed:
            got = "ABSTAIN" if r.abstained else ("+".join(r.cited_doc_types) or "no-cite")
            lines.append(f"- [{r.case.category}/{r.case.failmode}] {r.case.query}  → got: {got}")
    with open(os.path.join(REPORT_DIR, "regression_report.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    from eval.regression_set import run_regression
    pipeline, embedder = _build_pipeline()
    summary = run_regression(pipeline)
    _write_reports(summary, embedder)

    frozen = {"overall": summary["overall"], "by_category": summary["by_category"],
              "n": summary["n"], "embedder": embedder, "generated": str(date.today())}

    print(f"\nEmbedder: {embedder}   Overall: {summary['overall']:.1%}   (n={summary['n']})")
    for cat, acc in sorted(summary["by_category"].items()):
        print(f"  {cat:14} {acc:.1%}")

    if args.update_baseline:
        with open(BASELINE_PATH, "w") as fh:
            json.dump(frozen, fh, indent=2)
        print(f"\nBaseline frozen → {BASELINE_PATH}")
    elif os.path.exists(BASELINE_PATH):
        base = json.load(open(BASELINE_PATH))
        print(f"\nvs baseline ({base.get('embedder')}, overall {base['overall']:.1%}):")
        for cat in sorted(summary["by_category"]):
            now, was = summary["by_category"][cat], base["by_category"].get(cat, 0.0)
            d = now - was
            flag = "  <-- REGRESSION" if d < -0.0001 else ""
            print(f"  {cat:14} {was:.1%} -> {now:.1%}  ({d:+.1%}){flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
