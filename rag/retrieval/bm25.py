"""Okapi BM25 lexical index (Phase 4).

Pure stdlib so it runs on-device (over the bundled sqlite-vec / flat index) with
no server — the sparse half of hybrid retrieval. IDF-weighted term matching is
what makes rare, distinctive terms (write blocker, CDR, SIM, "section 63") win,
which dense embeddings under-retrieve. Phase 3's per-chunk ``keywords`` are folded
in with extra weight so curated operational terms rank strongly.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN = re.compile(r"[a-z0-9]+")

# How many extra times a curated keyword token is counted in a chunk's BM25 doc.
_KEYWORD_BOOST = 2


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class BM25Index:
    """Incrementally-built Okapi BM25 index over chunk ids."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._tf: dict[str, Counter] = {}      # chunk_id -> term frequencies
        self._len: dict[str, int] = {}         # chunk_id -> document length
        self._df: Counter = Counter()          # term -> document frequency
        self._avgdl: float = 0.0
        self._dirty = True

    def add(self, chunk_id: str, text: str, keywords: list[str] | None = None) -> None:
        tokens = tokenize(text)
        for kw in keywords or []:               # fold in curated keywords (boosted)
            tokens.extend(tokenize(kw) * _KEYWORD_BOOST)
        tf = Counter(tokens)
        self._tf[chunk_id] = tf
        self._len[chunk_id] = sum(tf.values())
        for term in tf:
            self._df[term] += 1
        self._dirty = True

    def _finalize(self) -> None:
        if self._dirty:
            n = len(self._len)
            self._avgdl = (sum(self._len.values()) / n) if n else 0.0
            self._dirty = False

    def _idf(self, term: str) -> float:
        n = len(self._tf)
        df = self._df.get(term, 0)
        # Okapi IDF with +1 so it never goes negative.
        return math.log((n - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query: str, candidate_ids: list[str]) -> dict[str, float]:
        """BM25 score for each candidate id against the query (0 for no match)."""
        self._finalize()
        q_terms = set(tokenize(query))
        scores: dict[str, float] = {}
        for cid in candidate_ids:
            tf = self._tf.get(cid)
            if not tf:
                continue
            dl = self._len[cid]
            s = 0.0
            for term in q_terms:
                f = tf.get(term, 0)
                if not f:
                    continue
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self._avgdl or 1.0))
                s += self._idf(term) * (f * (self.k1 + 1)) / denom
            if s > 0:
                scores[cid] = s
        return scores
