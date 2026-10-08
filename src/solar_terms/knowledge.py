"""Fixed bilingual names and background from HKO."""

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


def describe_term(index: int) -> str:
    longitude = (285 + 15 * index) % 360
    classification = (
        "中氣 Major solar term" if longitude % 30 == 0 else "節氣 Minor solar term"
    )
    lines = [classification, f"太陽黃經 Solar longitude: {longitude}°"]
    if note := SEASONAL_NOTES.get(longitude):
        lines.extend(["", note])
    lines.extend(["", "資料來源 Source: 香港天文台 Hong Kong Observatory", DETAIL_URL])
    return "\n".join(lines)
