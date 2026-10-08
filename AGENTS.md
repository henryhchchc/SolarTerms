# Solar Terms

## Development

- Use Python 3.14+ and the standard library; maintain project metadata and uv.lock.
- Keep fixed names and background in `src/solar_terms/knowledge.py`, separate from CLI and calendar generation.
- Prefer iterators.
  Preserve atomic output replacement and cleanup on failure.
- Preserve stable event identifiers, Hong Kong dates, and exact times (UTC+08:00).
- Hard-code bilingual names and background from HKO's [Traditional Chinese](https://www.hko.gov.hk/tc/gts/time/24solarterms.htm) and [English](https://www.hko.gov.hk/en/gts/time/24solarterms.htm) explanations.
- Follow RFC 5545, including text escaping, CRLF, and 75-byte folding without splitting Unicode characters.
- Publish only the ICS file.
  Keep generated files out of Git and preserve the previous deployment when generation fails.
- Pin GitHub Actions to exact semantic version tags and grant only necessary permissions.
- Keep README.md user-facing and this file limited to durable development guidance.

## Verification

Do not add automated tests.
Verify affected behavior manually against HKO and inspect generated calendars with an independent parser.
Check stable identifiers, date/time handling, serialization, and preservation of existing output on failure as relevant.

Use the formatters and checks:

```sh
ruff format src
ruff check src
rumdl fmt README.md AGENTS.md
actionlint .github/workflows/pages.yml
```
