# Jira Ticket: Replicate Goodwill Central Texas CAT Class Scraper

## Goal

Replicate the Goodwill Central Texas Career Advancement Training (CAT) class scraper using the existing Wufoo form implementation

## Description

This ticket covers replicating the Goodwill Central Texas CAT class schedule scraper in a new environment or for integration purposes. The scraper has been tested and confirmed working as of 2025-11-21, successfully fetching 222 training sessions across 19 class types from GRC and GCC locations.

**Example Forms:**
- GRC Career Advancement Essentials: https://gwcareeradvancement.wufoo.com/forms/grc-career-advancement-essentials/
- GCC Computer Basics: https://gwcareeradvancement.wufoo.com/forms/gcc-computer-basics/
- (17 additional forms - see implementation for full list)

**Implementation:** https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/cat/scraper_cat_classes.py

**Documentation:** https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/cat/README.md

**Expected output:**

See Sample data (Nov 21): https://github.com/RyanHansz/GW-info-gather/blob/main/data/cat_classes.json

## Acceptance Criteria

- Scraper runs successfully and pulls all active training sessions from 19 Wufoo forms with expected fields (date, time, instructor, spots_remaining, etc.)
- Verify by spot-checking forms at https://gwcareeradvancement.wufoo.com/forms/ against scraped data
- Training sessions are stored where the referral generation tool can reference them
- As an end user, I can search for and see available CAT classes with accurate scheduling information in the referral tool
- Scraper correctly identifies full sessions (0 spots remaining) and past sessions
- Date/time parsing handles multiple formats correctly (MM/DD/YY, month names, various time notations)

---

## Background

The Goodwill Central Texas Career Advancement Training (CAT) program offers free skills training classes at two locations. The scraper extracts class schedules from Wufoo registration forms to make this information accessible programmatically.

### Locations

**GRC - Goodwill Resource Center (South Austin)**
- 9 class types
- Classes include: Career Advancement Essentials, Computer Basics/Keyboarding, Digital Skills 1:1, Financial Empowerment Training, Indeed Lab, Interview Preparation & Practice, Job Preparation 1:1, Online Safety, Virtual Career Advancement Essentials

**GCC - Goodwill Community Center (North Austin)**
- 10 class types
- Classes include: All GRC classes plus Wonderlic Prep & Practice and AI Basics

### Technical Approach

The scraper uses **Playwright** browser automation to load Wufoo forms and extract session information from dropdown menus.

**Form Structure:**
Each Wufoo form contains a dropdown with session options formatted like:
- `"November 10-14, 9:00-12:00 pm, Mary -- 0 remaining"`
- `"December 8-11, 9:00am-12:00pm; Mary -- 4 remaining"`
- `"10/10/25, 2:00-3:00pm; Alex -- 1 remaining"`

**Key Parsing Logic:**
1. Extract spots remaining: `(\d+)\s+remaining`
2. Extract instructor name: `[,;]\s*([A-Za-z]+)\s*--`
3. Parse time ranges (handles shared periods, separate periods, en-dash)
4. Parse dates (MM/DD/YY or month name format)
5. Detect past sessions and full classes

---

## Implementation Requirements

### Dependencies

```bash
pip install playwright
playwright install chromium
```

### Core Functions to Implement

1. **`parse_session_text(session_text)`**
   - Parses complex session strings from dropdown options
   - Extracts: date, time, instructor, spots_remaining
   - Handles multiple date/time formats
   - Identifies full/past sessions
   - Returns: dictionary with parsed fields

2. **`scrape_form(page, url, class_name, location, location_full)`**
   - Scrapes a single Wufoo form for class sessions
   - Navigates to form URL with Playwright
   - Locates dropdown menu and extracts all options
   - Calls `parse_session_text()` for each option
   - Returns: class dictionary with sessions array

3. **`scrape_all_cat_classes()`**
   - Main orchestration function
   - Iterates through all 19 forms in CAT_FORMS dictionary
   - Handles pagination and rate limiting (1s delay between forms)
   - Returns: list of all classes with sessions

4. **`save_results(classes, filename)`**
   - Saves scraped data to JSON file
   - Adds metadata (scraped_at timestamp, source, total_classes)
   - Default output: `data/cat_classes.json`

### Data Fields to Extract

**Class-Level Fields:**
- `class_name`: Name of the training class
- `location`: Location code (GRC or GCC)
- `location_full`: Full location name
- `form_url`: Wufoo form URL
- `sessions`: Array of session objects
- `last_updated`: Timestamp of scrape

**Session-Level Fields:**
- `date`: ISO 8601 date (YYYY-MM-DD)
- `date_display`: Human-readable date from form
- `time_start`: Start time in 24-hour format (HH:MM)
- `time_end`: End time in 24-hour format (HH:MM)
- `time_display`: Human-readable time range with AM/PM
- `instructor`: Instructor first name
- `spots_remaining`: Number of available spots (integer)
- `is_full`: Boolean (true if 0 spots remaining)
- `is_past`: Boolean (true if date has passed)
- `raw_text`: Original unparsed session text

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

---

## Testing Checklist

### Unit Tests

- [ ] Test `parse_session_text()` with MM/DD/YY format
- [ ] Test `parse_session_text()` with month name format
- [ ] Test `parse_session_text()` with various time formats (9:00-12:00 pm, 9:00am-12:00pm, 2:00-3:00pm)
- [ ] Test `parse_session_text()` with en-dash vs hyphen in time ranges
- [ ] Test `parse_session_text()` with 0 spots remaining (is_full detection)
- [ ] Test `parse_session_text()` with past dates (is_past detection)
- [ ] Test `parse_session_text()` with invalid/unparseable text
- [ ] Test instructor name extraction with comma vs semicolon separators

### Integration Tests

- [ ] Run scraper on all 19 forms
- [ ] Verify total session count is reasonable (~200-230)
- [ ] Verify all classes have required fields
- [ ] Verify sessions have required fields
- [ ] Spot-check parsed data against actual Wufoo forms
- [ ] Test time conversion to 24-hour format is correct
- [ ] Verify past session detection works correctly
- [ ] Test error handling when form is unavailable
- [ ] Test handling of forms with no sessions

### Performance Tests

- [ ] Scraper completes all 19 forms in under 60 seconds
- [ ] No rate limiting errors from Wufoo
- [ ] Browser automation handles dynamic content loading
- [ ] Memory usage stays reasonable

---

## Configuration

Form URLs are organized by location in the `CAT_FORMS` dictionary:

```python
CAT_FORMS = {
    'GRC': {
        'location_full': 'Goodwill Resource Center (South Austin)',
        'forms': {
            'Career Advancement Essentials': 'https://gwcareeradvancement.wufoo.com/forms/grc-career-advancement-essentials/',
            'Computer Basics/Keyboarding': 'https://gwcareeradvancement.wufoo.com/forms/grc-computer-basics/',
            # ... 7 more forms
        }
    },
    'GCC': {
        'location_full': 'Goodwill Community Center (North Austin)',
        'forms': {
            'Career Advancement Essentials': 'https://gwcareeradvancement.wufoo.com/forms/gcc-career-advancement-essentials/',
            'Computer Basics/Keyboarding': 'https://gwcareeradvancement.wufoo.com/forms/gcc-computer-basics/',
            # ... 8 more forms
        }
    }
}
```

**Rate Limiting:**
- 1-second delay between form scrapes
- Playwright wait_until='networkidle' ensures full page load

---

## Edge Cases Handled by Current Implementation

1. **Multiple Date Formats**: Handles both `10/10/25` and `November 10-14` formats
2. **Time Format Variations**: Handles `9:00-12:00 pm` (shared period), `9:00am-12:00pm` (separate periods), `12:30pm–1:30pm` (en-dash)
3. **AM/PM Inference**: When start time has no period, infers from end period and hour values
4. **Past Date Detection**: Automatically flags sessions that have already occurred
5. **Full Session Detection**: Identifies sessions with 0 spots remaining
6. **Missing Instructor**: Handles cases where instructor name is missing
7. **Unparseable Sessions**: Logs error and continues with remaining sessions
8. **Empty Forms**: Gracefully handles forms with no sessions
9. **Year Inference**: For month name dates, infers current or next year based on whether date has passed
10. **Date Ranges**: Extracts first date from ranges like "November 10-14"

---

## Success Criteria

- [ ] Scraper successfully fetches sessions from all 19 Wufoo forms
- [ ] All required data fields are populated correctly
- [ ] Date/time parsing accuracy: >95% of sessions parse correctly
- [ ] Scraper completes in reasonable time (< 60 seconds)
- [ ] Past session detection works correctly
- [ ] Full session detection works correctly (is_full flag)
- [ ] Error handling prevents crashes on individual form failures
- [ ] Code follows existing project structure and conventions
- [ ] Documentation is clear and complete
- [ ] Output JSON validates against expected schema

---

## Deployment

1. Verify scraper is in `scrapers/cat/` directory
2. Ensure `scraper_cat_classes.py` is executable with correct permissions
3. Test scraper:
   ```bash
   python3 scrapers/cat/scraper_cat_classes.py
   ```
4. Verify output is saved to `data/cat_classes.json`
5. Validate JSON structure and data quality
6. Configure scheduled runs (if applicable)
7. Set up monitoring/alerting for scraper failures

---

## References

- **Reference Implementation**: [scrapers/cat/scraper_cat_classes.py](https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/cat/scraper_cat_classes.py) (304 lines)
- **Documentation**: [scrapers/cat/README.md](https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/cat/README.md)
- **Sample Data**: [data/cat_classes.json](https://github.com/RyanHansz/GW-info-gather/blob/main/data/cat_classes.json)
- **Repository**: https://github.com/RyanHansz/GW-info-gather
- **Test Results**: Successfully scraped 222 sessions across 19 classes on 2025-11-21

---

## Notes

- The existing implementation at `scrapers/cat/scraper_cat_classes.py` is complete and working
- Wufoo forms are generally stable but session data updates regularly as classes fill up
- No authentication required for public Wufoo forms
- The scraper respects Wufoo's servers with built-in 1-second delays between requests
- Consider caching responses during development/testing to reduce load
- Session count fluctuates as new classes are added and past classes are removed (typically ~200-230 sessions)
- Some sessions may fail to parse (~8% in testing) - these are logged but don't stop the scraper

---

## Estimated Effort

Since the implementation already exists, replication effort depends on scope:

**For code review and documentation:**
- **Code Review**: 1-2 hours
- **Testing**: 1 hour
- **Documentation Review**: 30 minutes
- **Total**: 2.5-3.5 hours

**For creating a derivative or integration:**
- **Setup**: 1-2 hours
- **Adaptation**: 2-4 hours
- **Testing**: 2-3 hours
- **Documentation**: 1-2 hours
- **Total**: 6-11 hours

---

## Priority

**Medium** - Existing scraper is working; replication needed for [specify purpose: deployment, integration, backup, etc.]

---

## Labels

`scraper`, `goodwill-central-texas`, `cat-classes`, `wufoo`, `training`, `career-advancement`, `replication`
