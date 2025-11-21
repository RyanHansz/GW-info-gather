# Goodwill Central Texas - Career Advancement Training (CAT) Class Scraper

**Source Code**: [scraper_cat_classes.py](scraper_cat_classes.py)

## Overview

This scraper extracts class schedule information from Goodwill Central Texas Career Advancement Training (CAT) Wufoo registration forms. It pulls upcoming training sessions including dates, times, instructors, and availability from dropdown menus across multiple locations.

## Key Features

✅ **Comprehensive Coverage** - Scrapes 19 class types across 2 locations (GRC & GCC)
✅ **Smart Parsing** - Handles multiple date/time formats (MM/DD/YY, "Month DD-DD", various time notations)
✅ **Availability Tracking** - Extracts spots remaining and identifies full/past sessions
✅ **Instructor Information** - Captures instructor names for each session
✅ **Past Date Detection** - Automatically flags sessions that have already occurred
✅ **Browser Automation** - Uses Playwright to handle dynamic Wufoo form content

## Locations & Classes

### GRC - Goodwill Resource Center (South Austin)
9 class types:
- Career Advancement Essentials
- Computer Basics/Keyboarding
- Digital Skills 1:1
- Financial Empowerment Training
- Indeed Lab
- Interview Preparation & Practice
- Job Preparation 1:1
- Online Safety
- Virtual Career Advancement Essentials

### GCC - Goodwill Community Center (North Austin)
10 class types:
- Career Advancement Essentials
- Computer Basics/Keyboarding
- Digital Skills 1:1
- Financial Empowerment Training
- Indeed Lab
- Interview Preparation & Practice
- Job Preparation 1:1
- Wonderlic Prep & Practice
- AI Basics
- Online Safety

## How It Works

### Form Structure

Each Wufoo form contains a dropdown menu with session options formatted like:
- `"November 10-14, 9:00-12:00 pm, Mary -- 0 remaining"`
- `"December 8-11, 9:00am-12:00pm; Mary -- 4 remaining"`
- `"10/10/25, 2:00-3:00pm; Alex -- 1 remaining"`

### Parsing Logic

The scraper uses regex patterns to extract:

1. **Spots Remaining**: `(\d+)\s+remaining`
2. **Instructor Name**: `[,;]\s*([A-Za-z]+)\s*--`
3. **Time Range**: Handles formats like:
   - `9:00-12:00 pm` (shared period)
   - `9:00am-12:00pm` (separate periods)
   - `12:30pm–1:30pm` (en-dash)
4. **Date**: Supports:
   - MM/DD/YY format (`10/10/25`)
   - Month name format (`November 10-14`)
   - Automatic year inference for month names

### Date/Time Processing

- Converts times to 24-hour format for standardization
- Infers AM/PM when not explicitly stated
- Checks if sessions are in the past
- Identifies full sessions (0 spots remaining)

## Usage

Run the scraper:
```bash
python scrapers/cat/scraper_cat_classes.py
```

Output will be saved to `data/cat_classes.json`.

## Data Structure

### Output Format

```json
{
  "scraped_at": "2025-11-21T14:30:00.123456",
  "source": "Goodwill Central Texas - Career Advancement Training Wufoo Forms",
  "total_classes": 19,
  "classes": [
    {
      "class_name": "Career Advancement Essentials",
      "location": "GRC",
      "location_full": "Goodwill Resource Center (South Austin)",
      "form_url": "https://gwcareeradvancement.wufoo.com/forms/grc-career-advancement-essentials/",
      "sessions": [
        {
          "date": "2025-12-08",
          "date_display": "December 8-11",
          "time_start": "09:00",
          "time_end": "12:00",
          "time_display": "9:00am-12:00pm",
          "instructor": "Mary",
          "spots_remaining": 4,
          "is_full": false,
          "is_past": false,
          "raw_text": "December 8-11, 9:00am-12:00pm; Mary -- 4 remaining"
        }
      ],
      "last_updated": "2025-11-21T14:30:00.123456"
    }
  ]
}
```

### Session Fields

- **date**: ISO 8601 date (YYYY-MM-DD) of the first session day
- **date_display**: Human-readable date as shown on form
- **time_start**: Start time in 24-hour format (HH:MM)
- **time_end**: End time in 24-hour format (HH:MM)
- **time_display**: Human-readable time range with AM/PM
- **instructor**: Instructor's first name
- **spots_remaining**: Number of available spots (integer)
- **is_full**: Boolean indicating if session is full (0 spots)
- **is_past**: Boolean indicating if session date has passed
- **raw_text**: Original unparsed session text from dropdown

## Statistics

Typical scrape yields:
- **~19 classes** across both locations
- **~200-230 sessions** depending on scheduling
- **~140-170 available sessions** (not full, not past)

## Technical Details

### Dependencies

Requires Playwright for browser automation:
```bash
pip install playwright
playwright install chromium
```

### Rate Limiting

- 1-second delay between form scrapes
- Total runtime: ~20-30 seconds for all forms

### Error Handling

- Gracefully handles forms with no sessions
- Skips unparseable session text (logs error)
- Continues scraping if individual forms fail

## Maintenance

### If Forms Change

1. **New Class Added**: Add entry to `CAT_FORMS` dictionary in the scraper
2. **Form URL Changed**: Update URL in `CAT_FORMS` dictionary
3. **Date Format Changed**: Update regex patterns in `parse_session_text()`
4. **Dropdown Selector Changed**: Update `page.locator('select').first` in `scrape_form()`

### Common Issues

**No sessions found for a form:**
- Check if the form URL is still valid
- Verify dropdown selector hasn't changed (inspect form HTML)
- Ensure Playwright has loaded the page fully (check `wait_until='networkidle'`)

**Date parsing errors:**
- Check for new date formats in session text
- Update regex patterns in `parse_session_text()`
- Review error logs for unparsed session text

**Time parsing issues:**
- Verify AM/PM inference logic handles new formats
- Check for special characters (en-dash vs hyphen)
- Ensure 24-hour conversion is correct

## Example Output Summary

```
Total Classes: 19
Total Sessions: 222
Available Sessions: 168

Sample Classes:

1. Career Advancement Essentials (GRC)
   URL: https://gwcareeradvancement.wufoo.com/forms/grc-career-advancement-essentials/
   Sessions: 14
   Next: December 8-11 at 9:00am-12:00pm
         4 spots remaining

2. Computer Basics/Keyboarding (GRC)
   URL: https://gwcareeradvancement.wufoo.com/forms/grc-computer-basics/
   Sessions: 12
   Next: November 25-27 at 1:00pm-3:00pm
         8 spots remaining
```

## Related Resources

- **Goodwill Job Scraper**: [scrapers/goodwill/scraper_api.py](../goodwill/scraper_api.py)
- **Repository**: [GW-info-gather](https://github.com/RyanHansz/GW-info-gather)
- **GRC Location**: Goodwill Resource Center, South Austin
- **GCC Location**: Goodwill Community Center, North Austin
