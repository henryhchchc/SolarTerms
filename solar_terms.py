# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

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

HONG_KONG = timezone(timedelta(hours=8), "Hong Kong Time")
SOURCE = (
    "https://www.hko.gov.hk/en/gts/astronomy/data/files/24SolarTerms_{year:04d}.xml"
)
DETAIL_URL = "https://www.hko.gov.hk/en/gts/astronomy/Solar_Term.htm"
# HKO tables, rotated to January's first term (solar longitude 285 degrees).
NAMES = (
    ("小寒", "Moderate Cold"),
    ("大寒", "Severe Cold"),
    ("立春", "Spring Commences"),
    ("雨水", "Spring Showers"),
    ("驚蟄", "Insects Waken"),
    ("春分", "Vernal Equinox"),
    ("清明", "Bright and Clear"),
    ("穀雨", "Corn Rain"),
    ("立夏", "Summer Commences"),
    ("小滿", "Corn Forms"),
    ("芒種", "Corn on Ear"),
    ("夏至", "Summer Solstice"),
    ("小暑", "Moderate Heat"),
    ("大暑", "Great Heat"),
    ("立秋", "Autumn Commences"),
    ("處暑", "End of Heat"),
    ("白露", "White Dew"),
    ("秋分", "Autumnal Equinox"),
    ("寒露", "Cold Dew"),
    ("霜降", "Frost"),
    ("立冬", "Winter Commences"),
    ("小雪", "Light Snow"),
    ("大雪", "Heavy Snow"),
    ("冬至", "Winter Solstice"),
)
SEASONAL_NOTES = {
    0: "晝夜長度大致相等。\nDay and night are approximately equal in length.",
    90: (
        "北半球全年日照時間最長。\n"
        "Longest daylight of the year in the Northern Hemisphere."
    ),
    180: "晝夜長度大致相等。\nDay and night are approximately equal in length.",
    270: (
        "北半球全年日照時間最短。\n"
        "Shortest daylight of the year in the Northern Hemisphere."
    ),
}


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


def escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def fold_line(value: str) -> Iterator[str]:
    # Count UTF-8 bytes, including the leading space on continuation lines.
    current = ""
    size = 0
    for character in value:
        width = len(character.encode("utf-8"))
        if size + width > 75:
            yield current
            current = " "
            size = 1
        current += character
        size += width
    yield current


def render_calendar(terms: Iterable[SolarTerm]) -> Iterator[str]:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    yield from (
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SolarTerms//HKO Solar Terms//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:二十四節氣 24 Solar Terms",
    )
    for term in terms:
        chinese, english = NAMES[term.index]
        start = term.instant.date()
        end = start + timedelta(days=1)
        uid = uuid.uuid5(uuid.NAMESPACE_URL, f"{term.source}#term-{term.index}")
        longitude = (285 + 15 * term.index) % 360
        classification = (
            "中氣 Major solar term" if longitude % 30 == 0 else "節氣 Minor solar term"
        )
        description_lines = [
            f"{term.instant:%Y-%m-%d %H:%M} Hong Kong Time (UTC+08:00)",
            "",
            classification,
            f"太陽黃經 Solar longitude: {longitude}°",
        ]
        if note := SEASONAL_NOTES.get(longitude):
            description_lines.extend(["", note])
        description_lines.extend(
            ["", "資料來源 Source: 香港天文台 Hong Kong Observatory", DETAIL_URL]
        )
        description = "\n".join(description_lines)
        yield from (
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{end:%Y%m%d}",
            f"SUMMARY:{escape_text(f'{chinese} {english}')}",
            f"DESCRIPTION:{escape_text(description)}",
            f"URL:{DETAIL_URL}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        )
    yield "END:VCALENDAR"


def write_calendar(path: Path, lines: Iterable[str]) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as file:
            temporary = Path(file.name)
            file.writelines(
                (folded + "\r\n").encode("utf-8")
                for line in lines
                for folded in fold_line(line)
            )
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_year(value: str) -> int:
    try:
        year = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("year must be an integer") from exc
    if not 1 <= year <= 9998:
        raise argparse.ArgumentTypeError("year must be between 1 and 9998")
    return year


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert HKO solar terms to an all-day calendar."
    )
    parser.add_argument(
        "years",
        nargs="*",
        type=parse_year,
        help="default: current Hong Kong year and next two",
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("solar_terms.ics"))
    args = parser.parse_args()
    current_year = datetime.now(HONG_KONG).year
    years = sorted(set(args.years or range(current_year, current_year + 3)))
    try:
        terms = (term for year in years for term in fetch_terms(year))
        write_calendar(args.output, render_calendar(terms))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {24 * len(years)} events to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
