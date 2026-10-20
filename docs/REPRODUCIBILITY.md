# Reproduction and audit scope

The repository is a curated copy of the completed local NYC research. `docs/research_snapshot_manifest.json` lists original relative paths and SHA-256 values. Source code, frozen specifications, notebooks, derived data, predictions, coverage/exclusion tables, metrics and audit records are retained. File bytes in the research snapshot were not edited for presentation.

## Available without reacquisition

- Rebuild the static site: `npm run build`.
- Recompute website data and copy/link evidence: `python scripts/build_site_data.py` after installing review requirements.
- Refit the daily DA-price experiment from its included daily table: run `research/price_research/src/run.py` from a scratch copy.
- Run original price tests (11) with one included GRIB fixture and spread saved-output tests (9), plus portable presentation/data-contract tests.
- Inspect the full notebooks and saved figures without executing them.

## Requires the original raw cache

The full hourly demand preparation pipeline, full original raw-source hash audit, spread runner's raw-source verification, and follow-up full runner/audit suites require bulk raw CSV/ZIP/GRIB files omitted from this repo. The follow-up release-preservation test also checks an original local release ZIP that is intentionally omitted. Do not claim every original suite runs in this curated repository.

Source acquisition scripts retain their public source URLs and can retrieve data, but historical files may be revised, removed or show different headers. Do not silently substitute new hashes into frozen audited records. The original full cache remains in the author's local source project.

The source snapshot includes historical README/audit documents describing the original workspace and release; those statements are not claims that this curated repo contains their complete raw caches. The root README and this document define the portable scope.

## Website values

`site/assets/research-data.js` and `site/evidence/results.json` are deterministic projections of the saved metric tables, daily cumulative table and follow-up summaries. Source paths and hashes are in `site/evidence/provenance.json`. Downloadable CSVs preserve original values. All displayed claims refer to the static 2021–2025 research snapshot, not current market data.
