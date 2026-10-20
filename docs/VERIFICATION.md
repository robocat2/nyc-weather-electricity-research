# Presentation release verification

Reviewed October 19, 2026. This record covers the new website and curated repository, not a new market experiment.

## Analytical integrity

- All research files match the publication manifest. Analytical code, specifications and data retain original bytes; three presentation files omit internal explanation instructions, with both hashes recorded.
- Website demand/price errors and percentage improvements reconcile to the original overall metric rows.
- Every original 2025 cumulative payoff point reconciles to independently calculated direction × (RT − DA) and sums to its displayed strategy total.
- Follow-up primary variants and different cohort sizes are preserved. No comparison ranks their raw totals across cohorts.
- Original later-stage exposure disclosures, assumed clearing, excluded costs, negative trading result and forecast-trajectory proxy distinction remain visible.
- Website provenance lists the actual source files and hashes. No new fitting or selection was performed for presentation.

## Portable checks

- Original DA-price tests: 11 passed, with one retained raw GRIB fixture.
- Original spread saved-output tests: 9 passed.
- Presentation/source/data-contract checks: 8 passed.
- JavaScript syntax and static production build passed.
- The entire original raw-cache-dependent audit is not portable here; scope is documented in REPRODUCIBILITY.md.

## Browser verification

Installed headless Google Chrome, actual local HTTP server:

- Desktop screenshot reviewed at 1440px; mobile screenshots reviewed at 390px.
- Horizontal overflow checked at 320, 390, 736 and 1440px; none observed.
- No JavaScript page errors observed.
- Legend hide/show updates the plotted line. Hover and touch display actual matched-date cumulative values.
- Native methods disclosures open correctly.
- All local main-page evidence links return HTTP 200.
- The linked full research page contains all 12 embedded chart images. Source/file links there resolve to the GitHub code paths; the repository is publicly accessible.
- The original browser checks above covered the local presentation. The research overview is now available at https://nyc-weather-electricity-research.vercel.app/; the live homepage was independently confirmed reachable after deployment.

Screenshots are under docs/preview/. The static source has no external fonts, chart-library CDN, analytics, API calls, frontend packages or runtime credentials.
