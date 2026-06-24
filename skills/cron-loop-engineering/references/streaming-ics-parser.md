# Streaming ICS Parser Pattern

For large calendar exports (multi-MB, thousands of events), never load the entire file into memory or use regex across the whole document.

## Core loop
```python
def parse_ics_stream(path):
    events = []
    current = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("BEGIN:VEVENT"):
            current = {}
        elif line.startswith("END:VEVENT"):
            if current:
                events.append(current)
            current = {}
        elif line.startswith("SUMMARY:"):
            current["summary"] = line.split(":", 1)[1]
        elif line.startswith("DTSTART"):
            # handle VALUE=DATE vs DATE-TIME, TZID, Z suffix, etc.
            ...
        # handle iCalendar line folding (next line starts with space/tab)
    return events
```

## Why this matters for cron
- Memory safe for 10k+ event calendars
- Tolerates malformed entries without blowing up the whole job
- Easy to add early-exit filters (e.g., only today’s events) before storing the full list

See also: `digest-implementation-pattern.md` for a real calendar + todo digest cron that uses this parser.
