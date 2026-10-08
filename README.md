# 🌿 Solar Terms · 二十四節氣

A bilingual calendar of the 24 solar terms, based on [Hong Kong Observatory data](https://www.hko.gov.hk/en/gts/astronomy/Solar_Term.htm).

## 📅 Add to your calendar

Copy this URL into your calendar app's **Add calendar by URL** or **Subscribe** option:

```text
https://henryhchchc.github.io/SolarTerms/solar_terms.ics
```

The calendar covers the current Hong Kong year and the following two years.
The feed refreshes on January 1, July 1, and when the project changes.

For a one-time import, [download the calendar](https://henryhchchc.github.io/SolarTerms/solar_terms.ics) and open it in your calendar app.

## ☀️ What's inside

- **Bilingual titles:** Traditional Chinese followed by English, such as `小寒 Moderate Cold`.
- **Hong Kong dates:** All-day events with the exact time (UTC+08:00) in their details.
- **Astronomical background:** Bilingual classifications, solar longitudes, and daylight notes for equinoxes and solstices.

Events leave your day available and include no alarms.

## 🛠️ Generate your own

With uv and Python 3.14+, run from the project directory:

```sh
uv run solar-terms
uv run solar-terms 2026 2027 2028 -o terms.ics
```

Without arguments, the output is `solar_terms.ics` for the current Hong Kong year and the following two years.
Pass years and `-o` to choose coverage and output path; the directory must already exist.

Successful runs replace the output file; failed runs preserve it.
Requested years must be available from HKO.
