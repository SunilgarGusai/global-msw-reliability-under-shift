# Repository release policy

This repository is the public reproducibility companion for the manuscript **“Reliability Gaps Under Geographic Shift in Global Municipal Waste Service Prediction.”**

## Submission freeze

The submission-state computational record is frozen under the tag:

`v1.0.0-submission`

The frozen release should preserve the exact code, machine-readable evidence, configuration, provenance, validation scripts, figures, and integrity metadata supporting the submitted manuscript.

## Immutability rule

- Do not rewrite the scientific contents of an existing frozen release.
- Documentation-only corrections may be made on the development branch when they do not change scientific results.
- Any correction that changes numerical evidence, analysis logic, or scientific interpretation receives a new versioned release.
- Publication metadata (journal citation, DOI, article URL) may be added after acceptance/publication without rewriting the historical submission tag.

## Public repository boundary

The repository is a computational reproducibility artifact rather than a mirror of every journal-portal file. Manuscript submission forms, cover letters, reviewer correspondence, and other administrative files remain outside the repository unless there is a clear scientific-reproducibility reason to include them.
