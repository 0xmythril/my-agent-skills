# Digest Cron Script — Known-Working Pattern

This reference captures the concrete implementation of a unified daily digest cron job that fuses calendar (work + personal ICS) with a todo JSON file, cross-analyzes them, and produces a single ranked briefing.

## Data sources
- **Work calendar**: Google Calendar ICS (private basic.ics URL)
- **Personal calendar**: Google Calendar ICS (private basic.ics URL)
- **Todos**: `~/.hermes/todos/daily-todos.json`
- **Weather**: `wttr.in` (curl-friendly, no API key)
- **State**: `~/.hermes/cron/state/daily-digest.json`

## Architecture

```
fetch ICS → parse VEVENTs       load todos JSON
     │                              │
     └──→ filter to today  ←───────┘
              │
         cross-analysis
         (conflicts, gaps, density)
              │
         format digest
              │
         persist state
```

## Key implementation details

### 1. ICS parsing must handle naive + aware datetimes
ICS `DTSTART` values come in three flavors:
- `20260609` (all-day, date object)
- `20260609T110000` (naive local time)
- `20260609T110000Z` (UTC)

Normalization helper:
```python
def to_hkt(dt):
    hkt = timezone(timedelta(hours=8))
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=hkt)
        return dt.astimezone(hkt)
    return dt
```

Apply to **every datetime** before comparison, subtraction, or sorting.

### 2. Use a line-by-line (streaming) ICS parser, never regex on the full file
A Google Calendar ICS export can be **13 MB+ with 6,000+ events**. `re.findall` on that will hang or OOM. Iterate line-by-line, handle iCalendar folding, and flush events on `END:VEVENT`.

(Full streaming parser implementation lives in the related reference `streaming-ics-parser.md`.)

## State structure example
```json
{
  "last_run": "2026-06-24T09:05:12+08:00",
  "work_events_today": 7,
  "personal_events_today": 3,
  "todo_count": 12,
  "conflicts_detected": 2,
  "empty_streaks": {"work": 0, "personal": 1}
}
```