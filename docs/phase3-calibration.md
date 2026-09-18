# Phase 3 - Semantic Calibration

## Context
In Phase 2, the relevance threshold was established as `0.45`, calibrated against an array of simplified, deterministic 3D orthogonal embeddings (e.g., `[1.0, 0.0, 0.0]`).

## Real Embeddings Calibration
Real embeddings produced by `text-embedding-004` consist of 768+ floating-point dimensions. They cluster much closer together, meaning true cosine similarity rarely approaches `0.0` even for unrelated concepts.

To responsibly evaluate this, a calibration suite was created: `agent/tests/semantic_calibration.py`.

## Limitations and Defaults
As real-world API keys and representative backend datasets are not yet available in the shared environment, the calibration suite includes a structural guardrail: it detects the absence of the key and safely exits, defaulting to the original `0.45` threshold.

**Warning**: Once real data is queried, `0.45` will likely be too low for `text-embedding-004`, as unrelated sentences frequently score `0.6` to `0.75` in dense vector spaces. The `semantic_calibration.py` script must be run by the deployment engineer to extract the average cosine similarity of an "irrelevant" query, and the `relevance_threshold` in `RankingConfig` should be updated accordingly.

