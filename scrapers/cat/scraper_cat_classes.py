#!/usr/bin/env python3
"""
Goodwill Central Texas - Career Advancement Training (CAT) Class Scraper
Extracts class schedule information from Wufoo registration forms
"""

import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
import time


# Form URLs organized by location
CAT_FORMS = {
    'GRC': {
        'location_full': 'Goodwill Resource Center (South Austin)',
        'forms': {
            'Budgeting Basics': 'https://gwcareeradvancement.wufoo.com/forms/grc-budgeting-basics/',
            'Career Advancement Essentials': 'https://gwcareeradvancement.wufoo.com/forms/grc-career-advancement-essentials/',
            'Computer Basics/Keyboarding': 'https://gwcareeradvancement.wufoo.com/forms/grc-computer-basics/',
            'Credit Basics': 'https://gwcareeradvancement.wufoo.com/forms/z19v5buf0f0tvm2/',
            'Digital Skills 1:1': 'https://gwcareeradvancement.wufoo.com/forms/grc-digital-skills-11/',
            'Financial Empowerment Training': 'https://gwcareeradvancement.wufoo.com/forms/grc-11-financial-empowerment-trainings/',
            'Indeed Lab': 'https://gwcareeradvancement.wufoo.com/forms/grc-indeed-lab/',
            'Interview Preparation & Practice': 'https://gwcareeradvancement.wufoo.com/forms/grc-interview-preparation-and-practice/',
            'Job Preparation 1:1': 'https://gwcareeradvancement.wufoo.com/forms/grc-job-preparation-11/',
            'Online Safety': 'https://gwcareeradvancement.wufoo.com/forms/grc-online-safety/',
            'Virtual Career Advancement Essentials': 'https://gwcareeradvancement.wufoo.com/forms/virtual-career-advancement-essentials/',
        }
    },
    'GCC': {
        'location_full': 'Goodwill Community Center (North Austin)',
        'forms': {
            'Budgeting Basics': 'https://gwcareeradvancement.wufoo.com/forms/gcc-budgeting-basics/',
            'Career Advancement Essentials': 'https://gwcareeradvancement.wufoo.com/forms/gcc-career-advancement-essentials/',
            'Computer Basics/Keyboarding': 'https://gwcareeradvancement.wufoo.com/forms/gcc-computer-basics/',
            'Credit Basics': 'https://gwcareeradvancement.wufoo.com/forms/x1eozbd71npnt5q/',
            'Digital Skills 1:1': 'https://gwcareeradvancement.wufoo.com/forms/gcc-digital-skills-11/',
            'Financial Empowerment Training': 'https://gwcareeradvancement.wufoo.com/forms/gcc-11-financial-empowerment-trainings/',
            'Indeed Lab': 'https://gwcareeradvancement.wufoo.com/forms/gcc-indeed-lab/',
            'Interview Preparation & Practice': 'https://gwcareeradvancement.wufoo.com/forms/gcc-interview-preparation-and-practice/',
            'Job Preparation 1:1': 'https://gwcareeradvancement.wufoo.com/forms/gcc-job-preparation-11/',
            'Wonderlic Prep & Practice': 'https://gwcareeradvancement.wufoo.com/forms/gcc-wonderlic-prep-and-practice/',
            'AI Basics': 'https://gwcareeradvancement.wufoo.com/forms/zjgi3bu0u7t757/',
            'Online Safety': 'https://gwcareeradvancement.wufoo.com/forms/zs43hn608egpxa/',
        }
    }
}


def parse_session_text(session_text):
    """
    Parse session text like:
    - "November 10-14, 9:00-12:00 pm, Mary -- 0 remaining"
    - "December 8-11, 9:00am-12:00pm; Mary -- 4 remaining"
    - "10/10/25, 2:00-3:00pm; Alex -- 1 remaining"

    Returns dict with parsed fields or None if can't parse
    """
    if not session_text or session_text.strip() == "Select from Dropdown":
        return None

    try:
        # Extract spots remaining
        spots_match = re.search(r'(\d+)\s+remaining', session_text)
        spots_remaining = int(spots_match.group(1)) if spots_match else 0

        # Extract instructor name (after comma or semicolon, before --)
        instructor_match = re.search(r'[,;]\s*([A-Za-z]+)\s*--', session_text)
        instructor = instructor_match.group(1).strip() if instructor_match else None

        # Split on instructor marker to get date/time part
        date_time_part = re.split(r'[,;]\s*[A-Za-z]+\s*--', session_text)[0].strip()

        # Extract time (handles formats like "9:00-11:00", "9:00-12:00 pm", "9:00am-12:00pm", "2:00-3:00pm", "12:30pm–1:30pm")
        time_match = re.search(r'(\d{1,2}:\d{2})\s*(am|pm)?\s*[-–]\s*(\d{1,2}:\d{2})\s*(am|pm)?', date_time_part, re.IGNORECASE)

        time_display = None
        time_start = None
        time_end = None

        if time_match:
            start_time = time_match.group(1)
            start_period = time_match.group(2)
            end_time = time_match.group(3)
            end_period = time_match.group(4)

            # If no am/pm at all, just display the times as-is
            if not start_period and not end_period:
                time_display = f"{start_time}-{end_time}"
            elif not start_period:
                # If start period not specified, infer from end period and time logic
                end_hour = int(end_time.split(':')[0])
                start_hour = int(start_time.split(':')[0])
                # If end is PM and start time is less than end time, start is also AM/PM
                if end_period.lower() == 'pm':
                    # If start is before noon and end is after noon, start is AM
                    if start_hour < 12 and end_hour >= 12:
                        start_period = 'am'
                    else:
                        start_period = end_period
                else:
                    start_period = end_period
                time_display = f"{start_time}{start_period or ''}-{end_time}{end_period}"
            else:
                time_display = f"{start_time}{start_period or ''}-{end_time}{end_period or ''}"

            # Convert to 24-hour format
            start_hour, start_min = map(int, start_time.split(':'))
            if start_period and start_period.lower() == 'pm' and start_hour != 12:
                start_hour += 12
            elif start_period and start_period.lower() == 'am' and start_hour == 12:
                start_hour = 0
            time_start = f"{start_hour:02d}:{start_min:02d}"

            end_hour, end_min = map(int, end_time.split(':'))
            if end_period and end_period.lower() == 'pm' and end_hour != 12:
                end_hour += 12
            elif end_period and end_period.lower() == 'am' and end_hour == 12:
                end_hour = 0
            time_end = f"{end_hour:02d}:{end_min:02d}"

        # Remove time from date part
        if time_match:
            date_part = date_time_part[:time_match.start()].strip().rstrip(',')
        else:
            date_part = date_time_part

        # Parse date (handle various formats)
        date_display = date_part
        date_iso = None

        # Try MM/DD/YYYY or MM/DD/YY format first
        date_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', date_part)
        if date_match:
            month, day, year = date_match.groups()
            # Handle 2-digit vs 4-digit years
            if len(year) == 2:
                full_year = f"20{year}"
            else:
                full_year = year
            date_iso = f"{full_year}-{int(month):02d}-{int(day):02d}"
            date_display = f"{int(month):02d}/{int(day):02d}/{full_year}"
        else:
            # Try "Month DD-DD" or "Month DD" format
            month_match = re.match(r'([A-Za-z]+)\s+(\d{1,2})(?:-\d{1,2})?', date_part)
            if month_match:
                month_name = month_match.group(1)
                day = month_match.group(2)
                # Determine year based on month - if month is later in year than current month,
                # it's likely from the previous year (e.g., "November" in January means Nov of last year)
                now = datetime.now()
                try:
                    # Parse to get month number
                    test_date = datetime.strptime(f"{month_name} {day} {now.year}", "%B %d %Y")
                    session_month = test_date.month

                    # If session month is later in the year than current month, use previous year
                    # (e.g., November/December when we're in January)
                    if session_month > now.month:
                        year_to_use = now.year - 1
                    elif session_month == now.month:
                        # Same month - check the day
                        if int(day) < now.day:
                            year_to_use = now.year  # Earlier this month, could be past
                        else:
                            year_to_use = now.year  # Later this month or today
                    else:
                        # Session month is earlier in year than current month - use current year
                        year_to_use = now.year

                    date_iso = f"{year_to_use}-{session_month:02d}-{int(day):02d}"
                except ValueError:
                    pass

        # Check if date is in the past
        is_past = False
        if date_iso:
            session_date = datetime.fromisoformat(date_iso)
            is_past = session_date < datetime.now()

        return {
            'date': date_iso,
            'date_display': date_display,
            'time_start': time_start,
            'time_end': time_end,
            'time_display': time_display,
            'instructor': instructor,
            'spots_remaining': spots_remaining,
            'is_full': spots_remaining == 0,
            'is_past': is_past,
            'raw_text': session_text
        }

    except Exception as e:
        print(f"  Error parsing session text '{session_text}': {e}")
        return None


def scrape_form(page, url, class_name, location, location_full):
    """Scrape a single Wufoo form for class sessions"""
    print(f"  Scraping {class_name} ({location})...")

    try:
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(1)  # Give dropdowns time to load

        # Find the training date dropdown (look for select elements)
        dropdown = page.locator('select').first

        if not dropdown:
            print(f"    Warning: No dropdown found on {url}")
            return None

        # Get all options
        options = dropdown.locator('option').all()

        sessions = []
        for option in options:
            text = option.inner_text().strip()
            if text and text != "Select from Dropdown":
                parsed = parse_session_text(text)
                if parsed:
                    sessions.append(parsed)

        if not sessions:
            print(f"    No sessions found")
            return None

        print(f"    Found {len(sessions)} session(s)")

        return {
            'class_name': class_name,
            'location': location,
            'location_full': location_full,
            'form_url': url,
            'sessions': sessions,
            'last_updated': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"    Error: {e}")
        return None


def scrape_all_cat_classes():
    """Scrape all CAT class forms"""
    print("=" * 70)
    print("Goodwill Central Texas - CAT Class Schedule Scraper")
    print("=" * 70)
    print()

    all_classes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Scrape GRC forms
        print(f"\nScraping GRC ({CAT_FORMS['GRC']['location_full']})...")
        print("-" * 70)
        for class_name, url in CAT_FORMS['GRC']['forms'].items():
            result = scrape_form(page, url, class_name, 'GRC', CAT_FORMS['GRC']['location_full'])
            if result:
                all_classes.append(result)
            time.sleep(1)  # Be respectful

        # Scrape GCC forms
        print(f"\nScraping GCC ({CAT_FORMS['GCC']['location_full']})...")
        print("-" * 70)
        for class_name, url in CAT_FORMS['GCC']['forms'].items():
            result = scrape_form(page, url, class_name, 'GCC', CAT_FORMS['GCC']['location_full'])
            if result:
                all_classes.append(result)
            time.sleep(1)  # Be respectful

        browser.close()

    return all_classes


def save_results(classes, filename='data/cat_classes.json'):
    """Save results to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Goodwill Central Texas - Career Advancement Training Wufoo Forms',
        'total_classes': len(classes),
        'classes': classes
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(classes)} classes to {filename}")


def main():
    classes = scrape_all_cat_classes()

    if classes:
        save_results(classes)

        # Print summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        total_sessions = sum(len(c['sessions']) for c in classes)
        available_sessions = sum(len([s for s in c['sessions'] if not s['is_full']]) for c in classes)

        print(f"\nTotal Classes: {len(classes)}")
        print(f"Total Sessions: {total_sessions}")
        print(f"Available Sessions: {available_sessions}")

        print("\nSample Classes:")
        for i, cls in enumerate(classes[:3], 1):
            print(f"\n{i}. {cls['class_name']} ({cls['location']})")
            print(f"   URL: {cls['form_url']}")
            print(f"   Sessions: {len(cls['sessions'])}")
            if cls['sessions']:
                session = cls['sessions'][0]
                print(f"   Next: {session['date_display']} at {session['time_display']}")
                print(f"         {session['spots_remaining']} spots remaining")

        print(f"\n✓ Successfully scraped {len(classes)} CAT classes!")
    else:
        print("\n✗ No classes found")


if __name__ == "__main__":
    main()
