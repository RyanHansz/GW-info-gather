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
    # Add summary fields to each class for easier diffing
    for cls in classes:
        valid_sessions = [s for s in cls['sessions'] if s.get('date')]
        cls['total_sessions'] = len(valid_sessions)
        cls['available_sessions'] = len([s for s in valid_sessions if not s['is_full'] and not s.get('is_past', False)])

    # Calculate totals
    total_sessions = sum(c['total_sessions'] for c in classes)
    available_sessions = sum(c['available_sessions'] for c in classes)

    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Goodwill Central Texas - Career Advancement Training Wufoo Forms',
        'total_classes': len(classes),
        'total_sessions': total_sessions,
        'available_sessions': available_sessions,
        'classes': classes
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(classes)} classes to {filename}")


def save_markdown_report(classes, filename=None):
    """Save classes to markdown report"""
    now = datetime.now()

    # Generate filename with date format: MM_DD_YY_CAT_Classes.md
    if filename is None:
        date_prefix = now.strftime('%m_%d_%y')
        filename = f'data/{date_prefix}_CAT_Classes.md'

    # Class catalog information from 2025 CAT Catalog
    class_catalog = {
        'Career Advancement Essentials': {
            'description': 'A comprehensive week-long program designed to equip clients with the tools needed for career readiness. Topics include job application and interview preparation, soft skills development, self-advocacy, and much more.',
            'duration': '3 hours/day (week-long)',
            'requirements': 'Completed Indeed Lab and signed checklist required.'
        },
        'Virtual Career Advancement Essentials': {
            'description': 'Virtual program tailored for clients with scheduling, transportation, or childcare challenges. Participants engage through a dedicated Google Classroom where assignments are posted, feedback is provided, and progress is tracked. Includes a virtual mock interview with a trainer.',
            'duration': '3 hours/day (week-long)',
            'requirements': 'Completed Indeed Lab and signed checklist required.'
        },
        'Indeed Lab': {
            'description': 'Group training designed to help clients enhance their digital resumes and job search skills, with a focus on best practices that can be applied across all job search platforms. Clients work closely with a trainer to build and/or refine their resumes.',
            'duration': '2 hours',
            'requirements': 'Access to Indeed and email account.'
        },
        'Wonderlic Prep & Practice': {
            'description': 'Designed to support clients advancing toward GCTA occupational training programs by enhancing skills and boosting confidence for the Wonderlic assessment. Includes a PowerPoint presentation with tips/strategies (1 hour) and a timed practice test with review (1 hour).',
            'duration': '2 hours',
            'requirements': None
        },
        'Interview Preparation & Practice': {
            'description': 'Learn interview preparation techniques, verbal and non-verbal communication, and elements for a successful interview. Includes time to practice answering questions and receive feedback. Clients will create a professional pitch and learn to make good first and last impressions.',
            'duration': '2 hours',
            'requirements': None
        },
        'Computer Basics/Keyboarding': {
            'description': 'Clients are set up with a NorthStar learner account (free, accessible from any device). Covers Essential Computer Skills (Computer Basics, Internet, Email, Windows/Mac), Essential Software Skills (Word, Excel, PowerPoint, Google Docs), and Using Technology (social media, information literacy, telehealth). Keyboarding uses Typing.com.',
            'duration': '2 hours',
            'requirements': None
        },
        'Budgeting Basics': {
            'description': 'Highlights the importance of creating and maintaining a budget to achieve financial goals. Participants learn practical steps to start and manage a budget effectively, explore budgeting tools and strategies, and differentiate between needs and wants.',
            'duration': '1.5 hours',
            'requirements': None
        },
        'Credit Basics': {
            'description': 'Learn the concept of credit, types of credit, and how credit history can affect your future. Covers credit terms, factors creditors look for when making decisions, and ways to build and repair credit.',
            'duration': '1 hour',
            'requirements': None
        },
        'Digital Skills 1:1': {
            'description': 'One-on-one training covering: NorthStar Computer Basics, Email Basics (setup, compose, attachments, spam), Smartphone Basics (iPhone/Android functions, settings, voicemail), Microsoft Office (Word, Excel, PowerPoint), or Google Workspace (Docs, Sheets, Slides, Drive).',
            'duration': '1 hour',
            'requirements': None
        },
        'Financial Empowerment Training': {
            'description': 'One-on-one financial literacy sessions covering: Budgeting Basics, Credit Basics, Savings Basics, Predatory Loans awareness, Online Safety, and Managing Finances Online. Topics can be customized to client needs.',
            'duration': '1 hour',
            'requirements': None
        },
        'Job Preparation 1:1': {
            'description': 'One-on-one job preparation covering: Indeed resume support, Cover Letters, Letter of Explanation (for criminal background), Job Application Skills, Soft Skills (communication, advocacy, time management), JOFI Career Exploration assessments, and Mock Interviews using the STAR method.',
            'duration': '1 hour',
            'requirements': None
        },
        'Online Safety': {
            'description': 'Learn essentials of protecting personal and financial information online. Covers common online security risks and scams, best practices for securing accounts and data, and builds confidence in managing online safety.',
            'duration': '1 hour',
            'requirements': None
        },
        'AI Basics': {
            'description': 'Learn how Artificial Intelligence (AI) can assist with the job search process including: Resume Optimization, Cover Letter writing, Interview Preparation, and Skills Development.',
            'duration': '1 hour',
            'requirements': None
        }
    }

    # Location info with addresses
    location_info = {
        'GRC': {
            'name': 'GRC - Goodwill Resource Center (South Austin)',
            'address': '1015 Norwood Park Blvd, Austin, TX 78753'
        },
        'GCC': {
            'name': 'GCC - Goodwill Community Center (North Austin)',
            'address': '6505 Burleson Rd, Austin, TX 78744'
        }
    }

    # Calculate stats
    total_sessions = 0
    available_sessions = 0
    future_sessions = 0
    total_spaces = 0

    grc_classes = 0
    grc_sessions = 0
    grc_spaces = 0
    gcc_classes = 0
    gcc_sessions = 0
    gcc_spaces = 0

    for cls in classes:
        valid_sessions = [s for s in cls['sessions'] if s.get('date')]
        total_sessions += len(valid_sessions)

        loc_spaces = sum(s.get('spots_remaining', 0) for s in valid_sessions if not s.get('is_full', True))

        if cls['location'] == 'GRC':
            grc_classes += 1
            grc_sessions += len(valid_sessions)
            grc_spaces += loc_spaces
        else:
            gcc_classes += 1
            gcc_sessions += len(valid_sessions)
            gcc_spaces += loc_spaces

        for session in valid_sessions:
            if not session['is_full']:
                available_sessions += 1
                total_spaces += session.get('spots_remaining', 0)
            if not session.get('is_past', False):
                future_sessions += 1

    # Build markdown
    lines = [
        "# Goodwill Central Texas",
        "# Career Advancement Training (CAT) Classes",
        "",
        f"**Generated:** {now.strftime('%B %d, %Y at %I:%M %p')}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Location | Classes | Sessions | Available Spaces |",
        "|----------|---------|----------|------------------|",
        f"| {location_info['GRC']['name'].split(' - ')[0]} (South Austin) | {grc_classes} | {grc_sessions} | {grc_spaces} |",
        f"| {location_info['GCC']['name'].split(' - ')[0]} (North Austin) | {gcc_classes} | {gcc_sessions} | {gcc_spaces} |",
        f"| **TOTAL** | **{len(classes)}** | **{total_sessions}** | **{total_spaces}** |",
        "",
        "---",
        "",
    ]

    # Process each location
    for location in ['GRC', 'GCC']:
        loc_info = location_info[location]
        lines.append(f"## {loc_info['name']}")
        lines.append("")
        lines.append(f"*{loc_info['address']}*")
        lines.append("")

        location_classes = [c for c in classes if c['location'] == location]

        for cls in sorted(location_classes, key=lambda x: x['class_name']):
            valid_sessions = [s for s in cls['sessions'] if s.get('date')]
            available = len([s for s in valid_sessions if not s['is_full']])
            upcoming_sessions = [s for s in valid_sessions if not s.get('is_past', False)]
            class_spaces = sum(s.get('spots_remaining', 0) for s in valid_sessions if not s.get('is_full', True))

            lines.append(f"### {cls['class_name']}")
            lines.append("")
            lines.append(f"**Location:** {loc_info['name']} — {loc_info['address']}")
            lines.append("")

            # Add catalog description if available
            catalog_info = class_catalog.get(cls['class_name'])
            if catalog_info:
                lines.append(f"*{catalog_info['description']}*")
                lines.append("")
                duration_req = f"**Duration:** {catalog_info['duration']}"
                if catalog_info.get('requirements'):
                    duration_req += f" | **Requirements:** {catalog_info['requirements']}"
                lines.append(duration_req)
                lines.append("")

            # Availability alert (matching PDF style)
            if len(valid_sessions) == 0:
                lines.append("> **📢 No sessions currently scheduled.** Check back soon!")
            elif class_spaces == 0:
                lines.append("> **📢 All sessions are currently full.** Check back for new openings!")
            else:
                lines.append(f"> **✅ Spaces available!** {class_spaces} total spots across {available} sessions")
            lines.append("")

            lines.append(f"**Sign-up URL:** {cls['form_url']}")
            lines.append("")
            lines.append(f"**Total Sessions:** {len(valid_sessions)} | **Available Spaces:** {class_spaces}")
            lines.append("")

            if valid_sessions:
                lines.append("| Date | Time | Instructor | Spaces | Status |")
                lines.append("|------|------|------------|--------|--------|")

                # Sort by date
                sorted_sessions = sorted(valid_sessions, key=lambda x: x.get('date', '') or '')

                for session in sorted_sessions:
                    date_str = session.get('date_display', 'TBD')
                    time_str = session.get('time_display', 'TBD') or 'TBD'
                    instructor = session.get('instructor', 'TBD') or 'TBD'
                    spots = session.get('spots_remaining', 0)
                    is_past = session.get('is_past', False)
                    is_full = session.get('is_full', False)

                    # Status column
                    if is_past:
                        status = "Past"
                    elif is_full:
                        status = "**Full**"
                    else:
                        status = "**Available**"

                    spots_str = str(spots)

                    # Format past sessions
                    if is_past:
                        date_str = f"~~{date_str}~~"
                        time_str = f"~~{time_str}~~"
                        spots_str = f"~~{spots}~~"

                    lines.append(f"| {date_str} | {time_str} | {instructor} | {spots_str} | {status} |")

                lines.append("")

            lines.append("---")
            lines.append("")

    # Footer
    lines.append("*This report is automatically generated from Goodwill Central Texas Wufoo registration forms.*")

    # Write to file
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Saved markdown report to {filename}")


def generate_pdf_report(classes, filename=None):
    """Generate PDF report from classes data"""
    try:
        # Import the PDF generator
        import sys
        import os

        # Add parent directory to path to import the PDF generator
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from generate_pdf_report import PDFReport

        now = datetime.now()

        # Generate filename with date format
        if filename is None:
            date_prefix = now.strftime('%m_%d_%y')
            filename = f'data/{date_prefix}_CAT_Classes.pdf'

        # Convert data to the format expected by PDFReport
        # Group by location
        locations_data = {}

        location_info = {
            'GRC': {
                'name': 'Goodwill Resource Center (South Austin)',
                'address': '1015 Norwood Park Blvd, Austin, TX 78753'
            },
            'GCC': {
                'name': 'Goodwill Community Center (North Austin)',
                'address': '6505 Burleson Rd, Austin, TX 78744'
            }
        }

        for cls in classes:
            loc_code = cls['location']
            loc_name = location_info.get(loc_code, {}).get('name', cls['location_full'])
            loc_addr = location_info.get(loc_code, {}).get('address', '')

            if loc_name not in locations_data:
                locations_data[loc_name] = {
                    'address': loc_addr,
                    'classes': {}
                }

            # Convert sessions to offerings format
            offerings = []
            total_spaces = 0
            valid_sessions = [s for s in cls['sessions'] if s.get('date')]

            for session in valid_sessions:
                date_time = session.get('date_display', '')
                if session.get('time_display'):
                    date_time += f", {session['time_display']}"

                offerings.append({
                    'date_time': date_time,
                    'trainer': session.get('instructor', 'TBD') or 'TBD',
                    'spaces_remaining': session.get('spots_remaining', 0)
                })

                if not session.get('is_full', True):
                    total_spaces += session.get('spots_remaining', 0)

            # Create availability message
            if len(valid_sessions) == 0:
                avail_msg = "No sessions currently scheduled. Check back soon!"
            elif total_spaces == 0:
                avail_msg = "All sessions are currently full. Check back for new openings!"
            else:
                avail_msg = f"Spaces available! Sign up at: {cls['form_url']}"

            locations_data[loc_name]['classes'][cls['class_name']] = {
                'url': cls['form_url'],
                'total_offerings': len(valid_sessions),
                'total_spaces': total_spaces,
                'offerings': offerings,
                'availability_message': avail_msg,
                'is_cat_class': True
            }

        # Save converted data to temp file for PDF generator
        pdf_data = {
            'scrape_date': now.date().isoformat(),
            'filter_note': 'Career Advancement Training Classes',
            'locations': locations_data
        }

        temp_json = 'data/cat_classes_pdf_temp.json'
        with open(temp_json, 'w') as f:
            json.dump(pdf_data, f, indent=2)

        # Generate PDF
        pdf_gen = PDFReport(temp_json)
        pdf_gen.generate_pdf(filename)

        # Clean up temp file
        os.remove(temp_json)

        print(f"✓ Saved PDF report to {filename}")

    except ImportError as e:
        print(f"⚠ Could not generate PDF (missing reportlab?): {e}")
    except Exception as e:
        print(f"⚠ Error generating PDF: {e}")


def main():
    classes = scrape_all_cat_classes()

    if classes:
        save_results(classes)
        save_markdown_report(classes)

        # Print summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)

        total_sessions = sum(len(c['sessions']) for c in classes)
        available_sessions = sum(len([s for s in c['sessions'] if not s['is_full']]) for c in classes)

        print(f"\nTotal Classes: {len(classes)}")
        print(f"Total Sessions: {total_sessions}")
        print(f"Available Sessions: {available_sessions}")

        print(f"\n✓ Successfully scraped {len(classes)} CAT classes!")
    else:
        print("\n✗ No classes found")


if __name__ == "__main__":
    main()
