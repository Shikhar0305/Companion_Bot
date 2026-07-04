"""Run Set B (manual investigator queries) through the pipeline and score it.

    python -m eval.run_manual_eval
    LLM_PROFILE=ollama OLLAMA_MODEL=gemma3:4b EMBEDDER=e5 python -m eval.run_manual_eval

Reuses ``AnswerPipeline.run()`` unchanged. The active backend profile is read
from the environment via ``app.config.get_settings`` (so ``stub`` and ``ollama``
are selected the same way the live service selects them — no code branch here).

For every case it captures answer / draft_answer / abstained / refused /
citations / verifier_report / reranked doc_types, judges it with the Set B
contract, and aggregates the 7 validation-plan dimensions. Results are written to
``eval/results/manual_eval.json`` and ``eval/results/manual_eval.md``.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import date

from core.constants import ABSTENTION_MESSAGE
from eval.manual_investigator_set import MANUAL_CASES, ManualCase, judge

RESULT_DIR = "eval/results"


def _build_pipeline():
    os.environ.setdefault("CORPUS_ROOT", "data/corpus")
    from app.config import get_settings
    from app.deps import _build_services, _load_corpus, _seed_demo_kb
    from rag.graph import AnswerPipeline

    settings = get_settings()
    services = _build_services(settings)
    if _load_corpus(services) == 0:
        _seed_demo_kb(services)
    return AnswerPipeline(services), settings


def _run_case(pipeline, case: ManualCase) -> dict:
    state = pipeline.run(case.query)
    ans = state.answer
    abstained = bool(ans.abstained)
    refused = bool(ans.refused)
    citations = [
        {"marker": c.marker, "doc_type": c.doc_type, "title": c.title, "section": c.section}
        for c in (ans.citations or [])
    ]
    cited_doc_types = sorted({c["doc_type"] for c in citations})
    draft = state.draft_answer or ""
    reranked_doc_types = [rc.chunk.doc_type for rc in state.reranked]
    passed = judge(case, abstained=abstained, refused=refused, cited_doc_types=cited_doc_types)
    return {
        "query": case.query,
        "category": case.category,
        "lang": case.lang,
        "must_abstain": case.must_abstain,
        "expected_doc_types": list(case.expected_doc_types),
        "dims": list(case.dims),
        # --- captured fields (as required) ---
        "answer": ans.text,
        "draft_answer": draft,
        "abstained": abstained,
        "refused": refused,
        "citations": citations,
        "cited_doc_types": cited_doc_types,
        "verifier_report": state.verifier_report,
        "reranked_doc_types": reranked_doc_types,
        # --- derived signals for the scorecard ---
        "abstain_reason": getattr(state, "abstain_reason", None),
        "model_used": getattr(state, "model_used", None),
        "confidence": ans.confidence,
        "exact_abstention": draft.strip() == ABSTENTION_MESSAGE,
        "n_citations": len(citations),
        "unknown_markers": list((state.verifier_report or {}).get("unknown_markers", [])),
        "passed": passed,
    }


def _rate(num: int, den: int) -> float:
    return round(num / den, 4) if den else 0.0


def _scorecard(rows: list[dict]) -> dict:
    should_answer = [r for r in rows if not r["must_abstain"]]
    should_abstain = [r for r in rows if r["must_abstain"]]
    answered = [r for r in should_answer if not (r["abstained"] or r["refused"])]

    # Dim 1 — citation discipline (over answered cases)
    clean_markers = [r for r in answered if not r["unknown_markers"] and r["n_citations"] >= 1]
    avg_cites = round(sum(r["n_citations"] for r in answered) / len(answered), 2) if answered else 0.0

    # Dim 2 — grounding-gate compatibility: nuisance abstentions the MODEL caused,
    # i.e. a should-answer case that abstained on a gate reason while retrieval
    # actually surfaced a correct-doc_type passage in the reranked set.
    nuisance = [
        r for r in should_answer
        if (r["abstained"] and r["abstain_reason"] in ("grounding_gate_failed", "no_citations")
            and set(r["expected_doc_types"]) & set(r["reranked_doc_types"]))
    ]

    # Dim 3 — exact-abstention compliance (over model-handled should-abstain cases,
    # i.e. NOT refused pre-retrieval by the guardrail).
    model_abstain = [r for r in should_abstain if not r["refused"]]
    exact = [r for r in model_abstain if r["exact_abstention"]]
    leaks = [r for r in should_abstain if not (r["abstained"] or r["refused"])]

    # Dim 4 — Hindi/Hinglish
    multiling = [r for r in rows if r["lang"] in ("hindi", "hinglish")]
    admitted = [r for r in multiling if not r["refused"]]
    multiling_pass = [r for r in multiling if r["passed"]]

    # Dims 5/6/7 — per-category accuracy
    def cat_rate(cat: str) -> float:
        sub = [r for r in rows if r["category"] == cat]
        return _rate(sum(r["passed"] for r in sub), len(sub))

    return {
        "overall": _rate(sum(r["passed"] for r in rows), len(rows)),
        "n": len(rows),
        "dim1_citation_discipline": {
            "grounded_answer_rate": _rate(len(answered), len(should_answer)),
            "clean_marker_rate": _rate(len(clean_markers), len(answered)),
            "avg_citations": avg_cites,
        },
        "dim2_grounding_gate": {
            "nuisance_abstention_rate": _rate(len(nuisance), len(should_answer)),
            "nuisance_queries": [r["query"] for r in nuisance],
        },
        "dim3_exact_abstention": {
            "correct_abstention_rate": _rate(sum(r["passed"] for r in should_abstain), len(should_abstain)),
            "exact_string_rate": _rate(len(exact), len(model_abstain)),
            "leak_rate": _rate(len(leaks), len(should_abstain)),
            "leak_queries": [r["query"] for r in leaks],
        },
        "dim4_hindi_hinglish": {
            "guardrail_admit_rate": _rate(len(admitted), len(multiling)),
            "pass_rate": _rate(len(multiling_pass), len(multiling)),
            "rejected_queries": [r["query"] for r in multiling if r["refused"]],
        },
        "dim5_legal": cat_rate("legal"),
        "dim6_sop": cat_rate("sop"),
        "dim7_recovery": cat_rate("recovery"),
        "decision_tree": cat_rate("decision_tree"),
    }


def _write_json(path: str, header: dict, score: dict, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"header": header, "scorecard": score, "cases": rows}, fh, indent=2, ensure_ascii=False)


def _write_md(path: str, header: dict, score: dict, rows: list[dict]) -> None:
    L = [
        f"# Set B — Manual Investigator Query Evaluation ({header['date']})",
        "",
        f"**Profile:** `{header['llm_profile']}`"
        + (f" (`{header['ollama_model']}`)" if header["llm_profile"] == "ollama" else "")
        + f"  ·  **Embedder:** `{header['embedder']}`  ·  **chunks:** {header['chunks']}",
        "",
        f"**Overall: {score['overall']:.1%}**  (n={score['n']})",
        "",
        "## Dimension scorecard",
        "",
        "| Dim | Metric | Value |",
        "|---|---|---|",
        f"| 1 Citation discipline | grounded-answer / clean-marker / avg cites | "
        f"{score['dim1_citation_discipline']['grounded_answer_rate']:.1%} / "
        f"{score['dim1_citation_discipline']['clean_marker_rate']:.1%} / "
        f"{score['dim1_citation_discipline']['avg_citations']} |",
        f"| 2 Grounding-gate compat | nuisance-abstention rate | "
        f"{score['dim2_grounding_gate']['nuisance_abstention_rate']:.1%} |",
        f"| 3 Exact abstention | correct / exact-string / **leak** | "
        f"{score['dim3_exact_abstention']['correct_abstention_rate']:.1%} / "
        f"{score['dim3_exact_abstention']['exact_string_rate']:.1%} / "
        f"**{score['dim3_exact_abstention']['leak_rate']:.1%}** |",
        f"| 4 Hindi/Hinglish | guardrail-admit / pass | "
        f"{score['dim4_hindi_hinglish']['guardrail_admit_rate']:.1%} / "
        f"{score['dim4_hindi_hinglish']['pass_rate']:.1%} |",
        f"| 5 Legal | pass rate | {score['dim5_legal']:.1%} |",
        f"| 6 SOP | pass rate | {score['dim6_sop']:.1%} |",
        f"| 7 Recovery | pass rate | {score['dim7_recovery']:.1%} |",
        f"| – Decision-tree | pass rate | {score['decision_tree']:.1%} |",
        "",
        "## Per-case results",
        "",
        "| ✓ | Cat | Lang | Query | Cited / Outcome |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        mark = "✅" if r["passed"] else "❌"
        if r["refused"]:
            outcome = "REFUSED"
        elif r["abstained"]:
            outcome = f"ABSTAIN ({r['abstain_reason'] or 'n/a'})"
        else:
            outcome = "+".join(r["cited_doc_types"]) or "no-cite"
        q = r["query"].replace("|", "\\|")
        L.append(f"| {mark} | {r['category']} | {r['lang']} | {q} | {outcome} |")
    # Flags worth eyeballing
    flags = []
    if score["dim3_exact_abstention"]["leak_queries"]:
        flags.append(f"- **LEAK (must-abstain but answered):** {score['dim3_exact_abstention']['leak_queries']}")
    if score["dim4_hindi_hinglish"]["rejected_queries"]:
        flags.append(f"- **Hindi/Hinglish rejected by guardrail:** {score['dim4_hindi_hinglish']['rejected_queries']}")
    if score["dim2_grounding_gate"]["nuisance_queries"]:
        flags.append(f"- **Nuisance abstentions (retrieval OK, model dropped it):** {score['dim2_grounding_gate']['nuisance_queries']}")
    if flags:
        L += ["", "## Flags", ""] + flags
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=RESULT_DIR)
    ap.add_argument("--prefix", default="manual_eval")
    args = ap.parse_args()

    pipeline, settings = _build_pipeline()
    rows = [_run_case(pipeline, c) for c in MANUAL_CASES]
    score = _scorecard(rows)
    header = {
        "date": str(date.today()),
        "llm_profile": settings.llm_profile,
        "ollama_model": settings.ollama_model,
        "embedder": settings.embedder,
        "chunks": pipeline.services.vector_store.count(),
    }

    os.makedirs(args.out_dir, exist_ok=True)
    json_path = os.path.join(args.out_dir, f"{args.prefix}.json")
    md_path = os.path.join(args.out_dir, f"{args.prefix}.md")
    _write_json(json_path, header, score, rows)
    _write_md(md_path, header, score, rows)

    print(f"Profile: {header['llm_profile']}"
          + (f" ({header['ollama_model']})" if header["llm_profile"] == "ollama" else "")
          + f"  Embedder: {header['embedder']}  chunks: {header['chunks']}")
    print(f"Set B overall: {score['overall']:.1%}  (n={score['n']})")
    print(f"  dim3 leak_rate: {score['dim3_exact_abstention']['leak_rate']:.1%}"
          f"   exact-string: {score['dim3_exact_abstention']['exact_string_rate']:.1%}")
    print(f"  dim4 Hindi/Hinglish admit: {score['dim4_hindi_hinglish']['guardrail_admit_rate']:.1%}"
          f"   pass: {score['dim4_hindi_hinglish']['pass_rate']:.1%}")
    print(f"  legal {score['dim5_legal']:.1%} · sop {score['dim6_sop']:.1%} · "
          f"recovery {score['dim7_recovery']:.1%} · decision_tree {score['decision_tree']:.1%}")
    print(f"Wrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
