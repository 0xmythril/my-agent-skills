# Streaming ICS Parser Pattern

For large calendar exports (multi-MB, thousands of events), never load the entire file into memory or use regex across the whole document.

> **Scope.** This is a deliberately minimal, dependency-free parser for the
> common case (`DTSTART`, `SUMMARY`, single VEVENT blocks). It intentionally
> ignores VTIMEZONE definitions, RRULE expansion, EXDATE, VALARM, and non-UTF-8
> encodings. For anything beyond simple digests, use the
> [`icalendar`](https://pypi.org/project/icalendar/) library (or `ics.py`), which
> handles all of the above correctly.

## Core loop

```python
from datetime import date, datetime, timezone, timedelta

def _parse_dtstart(raw: str):
    """
    Parse an unfolded DTSTART line into a `date` (all-day) or aware `datetime`.

    Handles:
        DTSTART:20260609                    -> date(2026, 6, 9)
        DTSTART;VALUE=DATE:20260609         -> date(2026, 6, 9)
        DTSTART:20260609T110000             -> naive datetime (floating local)
        DTSTART:20260609T110000Z            -> aware datetime in UTC
        DTSTART;TZID=Asia/Hong_Kong:20260609T110000
            -> naive datetime + tz name in the second return value

    Returns (value, tzid_or_None). The caller is responsible for attaching a
    real tzinfo when tzid is set (e.g. via zoneinfo.ZoneInfo(tzid)).
    """
    params, _, value = raw.partition(":")
    parts = params.split(";")
    tzid = None
    is_date = False
    for p in parts[1:]:
        if p.startswith("TZID="):
            tzid = p[5:]
        elif p == "VALUE=DATE":
            is_date = True

    value = value.strip()
    if is_date or len(value) == 8:
        return date(int(value[0:4]), int(value[4:6]), int(value[6:8])), None
    if value.endswith("Z"):
        dt = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        return dt, None
    dt = datetime.strptime(value, "%Y%m%dT%H%M%S")
    return dt, tzid


def _iter_unfolded_lines(path):
    """iCalendar line folding: any line starting with space/tab continues the prior line."""
    prev = None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            if line[:1] in (" ", "\t"):
                if prev is not None:
                    prev += line[1:]
                continue
            if prev is not None:
                yield prev
            prev = line
        if prev is not None:
            yield prev


def parse_ics_stream(path):
    events = []
    current = None
    for line in _iter_unfolded_lines(path):
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT":
            if current:
                events.append(current)
            current = None
        elif current is None:
            continue
        elif line.startswith("SUMMARY:"):
            current["summary"] = line.split(":", 1)[1]
        elif line.startswith("DTSTART"):
            value, tzid = _parse_dtstart(line)
            current["dtstart"] = value
            if tzid:
                current["dtstart_tzid"] = tzid
    return events
```

## Why this matters for cron

- Memory safe for 10k+ event calendars.
- Tolerates malformed entries without blowing up the whole job (unknown fields are skipped).
- Easy to add early-exit filters (e.g., only today's events) inside the loop before storing the full list.

## When to reach for a real library instead

Anything that touches recurrence, alarms, floating times across DST, non-Gregorian calendars, or writing ICS back out — use `icalendar`:

```python
# pip install icalendar
from icalendar import Calendar

with open(path, "rb") as f:
    cal = Calendar.from_ical(f.read())

for component in cal.walk("VEVENT"):
    summary = str(component.get("SUMMARY"))
    dtstart = component.decoded("DTSTART")  # returns a date or aware datetime
```

`icalendar` loads the whole file, so keep the streaming parser above for the multi-megabyte, digest-only path.

See also: `digest-implementation-pattern.md` for a real calendar + todo digest cron that uses this parser.
