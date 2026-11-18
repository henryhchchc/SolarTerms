from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from icalendar import TRANSP, Calendar, Event

from .knowledge import DETAIL_URL, NAMES, describe_term

HONG_KONG = timezone(timedelta(hours=8), "Hong Kong Time")
SOURCE = (
    "https://www.hko.gov.hk/en/gts/astronomy/data/files/24SolarTerms_{year:04d}.xml"
)


@dataclass(frozen=True)
class SolarTerm:
    index: int
    instant: datetime
    source: str


def fetch_terms(year: int) -> Iterator[SolarTerm]:
    source = SOURCE.format(year=year)
    try:
        with urllib.request.urlopen(source, timeout=30) as response:
            root = ET.fromstring(response.read())
    except ET.ParseError as exc:
        raise ValueError(f"{year}: invalid XML from {source}") from exc
    except OSError as exc:
        raise OSError(f"{year}: cannot fetch {source}: {exc}") from exc

    if root.tag != f"SolarTerms_{year:04d}":
        raise ValueError(f"{year}: unexpected XML root {root.tag!r}")
    if len(root) != 24 or any(record.tag != "Data" for record in root):
        raise ValueError(f"{year}: expected exactly 24 Data records")

    previous: datetime | None = None
    for index, record in enumerate(root):
        if sorted(field.tag for field in record) != ["D", "M", "hm"]:
            raise ValueError(f"{year}: record {index + 1} must contain M, D, and hm")
        month = record.findtext("M", "").strip()
        day = record.findtext("D", "").strip()
        clock = record.findtext("hm", "").strip()
        if not (
            re.fullmatch(r"[0-9]{2}", month)
            and re.fullmatch(r"[0-9]{2}", day)
            and re.fullmatch(r"[0-9]{2}:[0-9]{2}", clock)
        ):
            raise ValueError(f"{year}: invalid date/time in record {index + 1}")
        try:
            hour, minute = map(int, clock.split(":"))
            instant = datetime(
                year, int(month), int(day), hour, minute, tzinfo=HONG_KONG
            )
        except ValueError as exc:
            raise ValueError(
                f"{year}: invalid date/time in record {index + 1}"
            ) from exc
        if instant.month != index // 2 + 1:
            raise ValueError(f"{year}: expected two terms per month in calendar order")
        if previous is not None and instant <= previous:
            raise ValueError(f"{year}: records must be strictly chronological")
        previous = instant
        yield SolarTerm(index, instant, source)


def render_calendar(terms: Iterable[SolarTerm], *, source: str | None = None) -> bytes:
    stamp = datetime.now(UTC)
    calendar = Calendar(
        version="2.0",
        name="二十四節氣 24 Solar Terms",
        prodid="-//SolarTerms//HKO Solar Terms//EN",
    )
    if source:
        calendar.source = source
    for term in terms:
        chinese, english = NAMES[term.index]
        start = term.instant.date()
        end = start + timedelta(days=1)
        uid = uuid.uuid5(uuid.NAMESPACE_URL, f"{term.source}#term-{term.index}")
        description = (
            f"{term.instant:%Y-%m-%d %H:%M} Hong Kong Time (UTC+08:00)\n\n"
            f"{describe_term(term.index)}"
        )
        event = Event.new(
            uid=uid,
            stamp=stamp,
            start=start,
            end=end,
            summary=f"{chinese} {english}",
            description=description,
            url=DETAIL_URL,
            transparency=TRANSP.TRANSPARENT,
        )
        calendar.add_component(event)
    return calendar.to_ical()


def write_calendar(path: Path, contents: bytes) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as file:
            temporary = Path(file.name)
            file.write(contents)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a bilingual iCalendar (.ics) file with all-day solar term "
            "events from the Hong Kong Observatory. Covers the current "
            "year and the following two years."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="FILE",
        default=Path("solar_terms.ics"),
        help="write to FILE (default: %(default)s). Its directory must already exist.",
    )
    parser.add_argument(
        "--source",
        metavar="URL",
        help="set the calendar update URL. Omit to leave the update source unset.",
    )
    args = parser.parse_args()
    current_year = datetime.now(HONG_KONG).year
    years = range(current_year, current_year + 3)
    try:
        terms = (term for year in years for term in fetch_terms(year))
        write_calendar(args.output, render_calendar(terms, source=args.source))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {24 * len(years)} events to {args.output}")
    return 0
