#!/usr/bin/env python3
"""
Goodwill Central Texas Job Scraper - API Version
Uses the ADP Workforce Now API to fetch job data directly
Much faster and more reliable than DOM scraping
"""

import json
import re
import html
import time
import urllib.request
import urllib.error
from datetime import datetime


def clean_html_to_markdown(html_text):
    """
    Convert HTML job description to clean markdown

    Args:
        html_text: HTML string from API

    Returns:
        Clean markdown-formatted text
    """
    if not html_text:
        return ''

    text = html_text

    # Convert common HTML elements to markdown
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.DOTALL)
    text = re.sub(r'<i>(.*?)</i>', r'*\1*', text, flags=re.DOTALL)

    # Convert lists
    text = re.sub(r'<li[^>]*>', '- ', text)
    text = re.sub(r'</li>', '', text)
    text = re.sub(r'<ul[^>]*>', '\n', text)
    text = re.sub(r'</ul>', '\n', text)
    text = re.sub(r'<ol[^>]*>', '\n', text)
    text = re.sub(r'</ol>', '\n', text)

    # Convert paragraphs and line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<div[^>]*>', '\n', text)
    text = re.sub(r'</div>', '', text)

    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = html.unescape(text)

    # Clean up whitespace
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Leading whitespace per line
    text = text.strip()

    return text


def fetch_jobs_list(skip=0, top=20):
    """
    Fetch a page of jobs from the API

    Args:
        skip: Number of jobs to skip (for pagination)
        top: Number of jobs to return

    Returns:
        Dictionary with 'jobs' list and 'total' count
    """
    base_url = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions"
    params = f"?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&ccId=19000101_000001&locale=en_US&$skip={skip}&$top={top}"

    url = base_url + params

    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        jobs = data.get('jobRequisitions', [])
        total = data.get('meta', {}).get('totalNumber', 0)

        return {'jobs': jobs, 'total': total}

    except urllib.error.URLError as e:
        print(f"Error fetching jobs (skip={skip}): {e}")
        return {'jobs': [], 'total': 0}


def fetch_job_details(external_job_id):
    """
    Fetch detailed job information including description

    Args:
        external_job_id: The ExternalJobID for the job (not clientRequisitionID!)

    Returns:
        Dictionary with detailed job information
    """
    base_url = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions"
    params = f"/{external_job_id}?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&locale=en_US"

    url = base_url + params

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        # The API returns the data directly, not wrapped in 'jobRequisition'
        return data

    except urllib.error.URLError as e:
        print(f"  Error fetching details for job {external_job_id}: {e}")
        return {}


def extract_external_job_id(job_data):
    """
    Extract the ExternalJobID from customFieldGroup.stringFields
    This is the actual jobId used in URLs, not the clientRequisitionID

    Args:
        job_data: Raw job data from API

    Returns:
        ExternalJobID string or None
    """
    custom_field_group = job_data.get('customFieldGroup', {})
    string_fields = custom_field_group.get('stringFields', [])

    for field in string_fields:
        if field.get('nameCode', {}).get('codeValue') == 'ExternalJobID':
            return field.get('stringValue')

    return None


def parse_job_data(job_data, include_details=True):
    """
    Parse job data from API response into a clean format

    Args:
        job_data: Raw job data from API
        include_details: Whether to fetch full job description

    Returns:
        Dictionary with cleaned job data
    """
    job = {
        'title': job_data.get('requisitionTitle'),
        'item_id': job_data.get('itemID'),
        'client_requisition_id': job_data.get('clientRequisitionID'),
        'posted_date': job_data.get('postDate'),
    }

    # Parse location
    locations = job_data.get('requisitionLocations', [])
    if locations:
        location = locations[0]
        name_code = location.get('nameCode', {})
        job['location'] = name_code.get('shortName', '')

        # Parse address details
        address = location.get('address', {})
        if address:
            job['city'] = address.get('cityName')
            job['state'] = address.get('countrySubdivisionLevel1', {}).get('codeValue')
            job['postal_code'] = address.get('postalCode')

    # Parse job type
    work_level = job_data.get('workLevelCode', {})
    if work_level:
        job['job_type'] = work_level.get('shortName')

    # Parse salary range
    pay_grade = job_data.get('payGradeRange', {})
    if pay_grade:
        min_rate = pay_grade.get('minimumRate', {})
        max_rate = pay_grade.get('maximumRate', {})

        if min_rate and max_rate:
            min_amount = min_rate.get('amountValue')
            max_amount = max_rate.get('amountValue')
            currency = min_rate.get('currencyCode', 'USD')

            if min_amount == max_amount:
                job['salary'] = f"${min_amount:,.2f}"
            else:
                job['salary'] = f"${min_amount:,.2f} - ${max_amount:,.2f}"

            job['salary_currency'] = currency

    # Construct job URL using ExternalJobID (not clientRequisitionID!)
    external_job_id = extract_external_job_id(job_data)
    if external_job_id:
        base_url = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html"
        params = f"?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter&jobId={external_job_id}"
        job['url'] = base_url + params
        job['external_job_id'] = external_job_id

    # Fetch detailed information if requested (use external_job_id, not client_req_id!)
    if include_details and external_job_id:
        details = fetch_job_details(external_job_id)

        if details:
            # Add job description (field is 'requisitionDescription', not 'jobDescription')
            job_desc = details.get('requisitionDescription')
            if job_desc:
                job['description'] = job_desc

            # Add additional fields from details if not already present
            if not job.get('salary'):
                pay_grade_detail = details.get('payGradeRange', {})
                if pay_grade_detail:
                    min_rate = pay_grade_detail.get('minimumRate', {})
                    max_rate = pay_grade_detail.get('maximumRate', {})

                    if min_rate and max_rate:
                        min_amount = min_rate.get('amountValue')
                        max_amount = max_rate.get('amountValue')

                        if min_amount == max_amount:
                            job['salary'] = f"${min_amount:,.2f}"
                        else:
                            job['salary'] = f"${min_amount:,.2f} - ${max_amount:,.2f}"

    return job


def scrape_goodwill_jobs_api(fetch_details=True):
    """
    Scrape all Goodwill Central Texas jobs using the API

    Args:
        fetch_details: Whether to fetch full job descriptions (slower but more complete)

    Returns:
        List of job dictionaries
    """
    print("=" * 60)
    print("Goodwill Central Texas Job Scraper (API Version)")
    print("=" * 60)
    print()

    # First, get initial page to find total count
    print("Fetching job list...")
    result = fetch_jobs_list(skip=0, top=20)
    total_jobs = result['total']
    all_jobs_raw = result['jobs']

    print(f"Found {total_jobs} total jobs")
    print(f"Loaded {len(all_jobs_raw)} jobs")

    # Fetch remaining pages
    if total_jobs > 20:
        page_size = 20
        pages_needed = (total_jobs // page_size) + (1 if total_jobs % page_size else 0)

        for page in range(1, pages_needed):
            skip = page * page_size
            print(f"Fetching jobs {skip + 1} to {min(skip + page_size, total_jobs)}...")

            result = fetch_jobs_list(skip=skip, top=page_size)
            all_jobs_raw.extend(result['jobs'])
            time.sleep(0.5)  # Be respectful to the API

    print(f"\nTotal jobs fetched: {len(all_jobs_raw)}")

    # Parse job data
    print("\n" + "=" * 60)
    if fetch_details:
        print(f"Extracting detailed information from {len(all_jobs_raw)} jobs...")
    else:
        print(f"Parsing {len(all_jobs_raw)} jobs (basic info only)...")
    print("=" * 60)
    print()

    jobs = []
    for idx, job_raw in enumerate(all_jobs_raw, 1):
        job = parse_job_data(job_raw, include_details=fetch_details)
        jobs.append(job)

        if fetch_details:
            print(f"[{idx}/{len(all_jobs_raw)}] {job.get('title', 'N/A')[:50]}")
            if idx < len(all_jobs_raw):
                time.sleep(0.3)  # Be respectful to the API
        else:
            if idx % 10 == 0 or idx == len(all_jobs_raw):
                print(f"Processed {idx}/{len(all_jobs_raw)} jobs...")

    return jobs


def save_jobs(jobs, filename='data/jobs.json'):
    """Save jobs to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Goodwill Central Texas (ADP Workforce Now API)',
        'total_jobs': len(jobs),
        'jobs': jobs
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(jobs)} jobs to {filename}")


def save_jobs_markdown(jobs, filename=None):
    """Save jobs to markdown file"""
    now = datetime.now()

    # Generate filename with date format: MM_DD_YY_Goodwill_Jobs.md
    if filename is None:
        date_prefix = now.strftime('%m_%d_%y')
        filename = f'data/{date_prefix}_Goodwill_Jobs.md'

    # Group jobs by category
    categories = {}
    for job in jobs:
        title = job.get('title', 'Other')
        # Simplify title to category
        if 'Manager' in title or 'Director' in title or 'Supervisor' in title:
            category = 'Management & Leadership'
        elif 'Teacher' in title or 'Instructor' in title or 'Coordinator' in title:
            category = 'Education & Training'
        elif 'Sales Associate' in title or 'Outlet Sales' in title:
            category = 'Sales'
        elif 'Merchandise Processor' in title:
            category = 'Merchandise Processing'
        elif 'eCommerce' in title or 'E-Commerce' in title or 'E-commerce' in title:
            category = 'eCommerce'
        elif 'Custodian' in title or 'Custodial' in title:
            category = 'Custodial Services'
        elif 'Driver' in title or 'Material Handler' in title or 'ADC Attendant' in title:
            category = 'Warehouse & Transportation'
        elif 'Child' in title or 'Early Childhood' in title:
            category = 'Child Development'
        else:
            category = 'Other Positions'

        if category not in categories:
            categories[category] = []
        categories[category].append(job)

    # Build markdown content
    lines = [
        f"# Goodwill Central Texas Job Listings",
        f"",
        f"**Last Updated:** {now.strftime('%B %d, %Y at %I:%M %p')}",
        f"",
        f"**Total Positions:** {len(jobs)}",
        f"",
        f"---",
        f"",
    ]

    # Table of contents
    lines.append("## Quick Navigation")
    lines.append("")
    for category in sorted(categories.keys()):
        anchor = category.lower().replace(' ', '-').replace('&', '').replace('--', '-')
        count = len(categories[category])
        lines.append(f"- [{category}](#{anchor}) ({count})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Job listings by category
    for category in sorted(categories.keys()):
        anchor = category.lower().replace(' ', '-').replace('&', '').replace('--', '-')
        lines.append(f"## {category}")
        lines.append("")

        # Sort by posted date (newest first)
        cat_jobs = sorted(categories[category],
                         key=lambda x: x.get('posted_date', ''),
                         reverse=True)

        for job in cat_jobs:
            title = job.get('title', 'N/A')
            location = job.get('location', 'N/A')
            city = job.get('city', '')
            job_type = job.get('job_type', 'N/A')
            salary = job.get('salary', '')
            url = job.get('url', '')
            posted = job.get('posted_date', '')

            # Format posted date
            if posted:
                try:
                    dt = datetime.fromisoformat(posted.replace('Z', '+00:00'))
                    posted_fmt = dt.strftime('%b %d, %Y')
                except:
                    posted_fmt = posted[:10] if len(posted) >= 10 else posted
            else:
                posted_fmt = 'N/A'

            lines.append(f"### {title}")
            lines.append("")
            lines.append(f"- **Location:** {location}")
            lines.append(f"- **Type:** {job_type}")
            if salary:
                lines.append(f"- **Salary:** {salary}")
            lines.append(f"- **Posted:** {posted_fmt}")
            if url:
                lines.append(f"- **[Apply Here]({url})**")
            lines.append("")

            # Add full job description
            description = job.get('description', '')
            if description:
                clean_desc = clean_html_to_markdown(description)
                if clean_desc:
                    lines.append("#### Job Description")
                    lines.append("")
                    lines.append(clean_desc)
                    lines.append("")

        lines.append("---")
        lines.append("")

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ Saved markdown report to {filename}")


def main():
    import sys

    # Check for --no-details flag
    fetch_details = '--no-details' not in sys.argv

    if not fetch_details:
        print("Running in fast mode (no detailed descriptions)\n")

    jobs = scrape_goodwill_jobs_api(fetch_details=fetch_details)

    if jobs:
        save_jobs(jobs)
        save_jobs_markdown(jobs)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        # Show first 5 and last 5 jobs
        display_jobs = jobs[:5] + (jobs[-5:] if len(jobs) > 10 else [])

        for i, job in enumerate(display_jobs):
            if i == 5 and len(jobs) > 10:
                print(f"\n... ({len(jobs) - 10} more jobs) ...\n")

            actual_idx = i + 1 if i < 5 else len(jobs) - (len(display_jobs) - i - 1)
            print(f"\n{actual_idx}. {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Type: {job.get('job_type', 'N/A')}")
            print(f"   Posted: {job.get('posted_date', 'N/A')}")
            if job.get('salary'):
                print(f"   Salary: {job.get('salary')}")
            if job.get('url'):
                print(f"   URL: {job.get('url')}")
            if job.get('description'):
                desc_preview = job.get('description')[:150].replace('\n', ' ')
                print(f"   Description: {desc_preview}...")

        print(f"\n✓ Successfully scraped {len(jobs)} jobs!")
    else:
        print("\n✗ No jobs found")


if __name__ == "__main__":
    main()
