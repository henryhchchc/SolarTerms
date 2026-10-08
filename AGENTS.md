# Solar Terms

## Implementation

- Use Python 3.14+ and the standard library; retain inline script metadata for uv.
- Fetch `https://www.hko.gov.hk/en/gts/astronomy/data/files/24SolarTerms_<year>.xml` with a 30-second timeout.
  XML contains dates and times, without names.
- Validate the root year, 24 records, required fields, valid dates/times, strict chronological order, and two records per month.
- Hard-code names and background from HKO's [Traditional Chinese](https://www.hko.gov.hk/tc/gts/time/24solarterms.htm) and [English](https://www.hko.gov.hk/en/gts/time/24solarterms.htm) tables.
  January starts with 小寒; solar longitude starts at 285° and advances by 15°.
  Multiples of 30° are 中氣; other terms are 節氣.
- Preserve Hong Kong dates and exact times (UTC+08:00).
  All-day events end exclusively on the following date.
  Include bilingual classification, longitude, and daylight notes for equinoxes and solstices.
- Sort and deduplicate requested years before streaming terms.
  Keep fetching, rendering, and folding as iterators; avoid materializing the calendar.
- Consume the stream into a temporary file beside the destination.
  Replace output only after successful completion and close; clean up on failure, including errors raised during iteration.
- Preserve UUID5 identifiers derived from the yearly XML URL and term index.
  Event detail links point to `https://www.hko.gov.hk/en/gts/astronomy/Solar_Term.htm`.
- Follow RFC 5545: UTF-8, CRLF, escaped text, UTC timestamps, date-only start/end, transparent availability, and 75-byte folding without splitting Unicode characters.

## Verification

Format Markdown with `rumdl fmt README.md AGENTS.md`.

Do not add automated tests.
Verify changes manually and run the formatter:

```sh
ruff format --target-version py314 solar_terms.py
ruff check --target-version py314 solar_terms.py
```

Compare generated names, dates, times, classifications, and longitudes against HKO.
Inspect the calendar with an independent parser; verification tools may use temporary dependencies without adding runtime dependencies.
Check relevant CLI options and failure paths, stable identifiers, Unicode serialization, and preservation of existing output.

Manual verification on 2026-10-08 with Python 3.14 confirmed:

- All 72 events for 2026–2028 match independently downloaded HKO XML and both name tables; bilingual background matches HKO's explanations.
- Independent parsing, date-only boundaries, stable unique identifiers, UTC timestamps, escaping, CRLF, and 75-byte folding pass.
- Default years, sorted/deduplicated explicit years, and custom output work.
- Invalid arguments, unavailable years, malformed XML, connection failures, and output permission/path errors preserve existing output.
- Iterator output matches the preceding implementation except for generation timestamps.
  Failure after 24 streamed events preserves output and removes the temporary file.
- Ruff formatting and lint checks pass.

Keep README.md focused on usage and calendar behavior; put implementation and verification notes here.
