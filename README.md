# Solar Terms

Create an iCalendar file of the 24 solar terms using [Hong Kong Observatory data](https://www.hko.gov.hk/en/gts/astronomy/Solar_Term.htm).
Subscribe to [solar_terms.ics](https://henryhchchc.github.io/SolarTerms/solar_terms.ics) using your calendar application's option to add a calendar by URL.
The calendar is refreshed on January 1, July 1, and project updates.
You can also download and import it for a snapshot.

To generate a calendar locally, use Python 3.14+:

```sh
uv run solar_terms.py
uv run solar_terms.py 2026 2027 2028 -o terms.ics
```

Without arguments, fetch the current Hong Kong year and the following two years into `solar_terms.ics`.
Specify years and `-o` to choose the calendar's coverage and output path.
The output directory must already exist.
You can also run `python3.14 solar_terms.py` directly.

Import the generated `.ics` file into your calendar application.
Each term is an all-day event on its Hong Kong date, titled in Traditional Chinese followed by English, such as `小寒 Moderate Cold`.
Details include the exact Hong Kong time (UTC+08:00), bilingual astronomical background, and a link to HKO.
Events leave the day available and have no alarms.
Repeated-import behavior depends on your calendar application.

Successful runs replace the output file; failed runs preserve it.
All requested years must be available from HKO.
