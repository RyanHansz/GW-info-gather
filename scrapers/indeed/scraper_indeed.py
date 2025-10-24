#!/usr/bin/env python3
"""
Indeed Job Scraper for Goodwill Central Texas
Scrapes job postings from Indeed.com
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def extract_job_details(page, job_url):
    """
    Extracts detailed information from a job page

    Args:
        page: Playwright page object
        job_url: URL of the job to extract details from

    Returns:
        Dictionary with job details
    """
    details = {}

    try:
        print(f"    → Visiting job page...")
        page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
        time.sleep(2)

        # Extract full job description
        desc_container = page.query_selector('div#jobDescriptionText')
        if desc_container:
            details['description'] = desc_container.inner_text().strip()

        # Extract job type details
        job_type_elem = page.query_selector('div[data-testid="job-details-job-type"]')
        if job_type_elem:
            details['job_type'] = job_type_elem.inner_text().strip()

        # Extract benefits (if available)
        benefits_section = page.query_selector('div[id*="benefits"], div[class*="benefits"]')
        if benefits_section:
            details['benefits'] = benefits_section.inner_text().strip()

        # Try to extract qualifications/requirements section
        # Look for sections with common headings
        all_text = page.query_selector('div#jobDescriptionText')
        if all_text:
            full_text = all_text.inner_text()

            # Try to identify qualifications section
            if 'Qualifications' in full_text or 'Requirements' in full_text:
                # Extract sections if identifiable
                sections = full_text.split('\n\n')
                for i, section in enumerate(sections):
                    if 'Qualifications' in section or 'Requirements' in section:
                        details['qualifications'] = section.strip()
                        break

        print(f"    ✓ Extracted job details")

    except PlaywrightTimeoutError:
        print(f"    ✗ Timeout loading job page")
    except Exception as e:
        print(f"    ✗ Error extracting job details: {str(e)[:50]}")

    return details


def scrape_indeed_jobs(headless=True, use_company_page=True):
    """
    Scrapes Goodwill Central Texas job postings from Indeed with detailed information

    Args:
        headless: Whether to run browser in headless mode
        use_company_page: If True, scrape from company page; if False, use search results
    """
    if use_company_page:
        url = "https://www.indeed.com/cmp/Goodwill-Central-Texas/jobs"
    else:
        url = "https://www.indeed.com/q-goodwill-central-texas-l-austin,-tx-jobs.html?vjk=1db5c23c9b0ed3dc"

    jobs = []

    with sync_playwright() as p:
        print("Launching browser...")
        # Launch with more realistic browser settings
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = context.new_page()

        # Remove webdriver property
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print(f"Navigating to {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
        except PlaywrightTimeoutError:
            # Try one more time with load instead
            page.goto(url, wait_until="load", timeout=45000)
        time.sleep(3)

        # Close any popups that might appear
        try:
            popup_close = page.query_selector('button[aria-label="Close"]')
            if popup_close:
                popup_close.click()
                time.sleep(1)
        except:
            pass

        # Wait for job listings to load
        print("Waiting for job listings to load...")
        try:
            page.wait_for_selector('div.job_seen_beacon', timeout=10000)
            print("Job listings found!")
        except PlaywrightTimeoutError:
            print("Warning: Could not find job listings")
            # Save HTML for debugging
            with open('indeed_debug.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            print("Saved page HTML to indeed_debug.html")

        # Extract job cards
        job_cards = page.query_selector_all('div.job_seen_beacon')
        print(f"\nFound {len(job_cards)} job postings")

        for idx, card in enumerate(job_cards, 1):
            try:
                job_data = {}

                # Extract job title - try multiple selectors
                title_elem = card.query_selector('h2.jobTitle a span')
                if not title_elem:
                    title_elem = card.query_selector('h2.jobTitle span[title]')
                if not title_elem:
                    title_elem = card.query_selector('h2.jobTitle a')
                if not title_elem:
                    title_elem = card.query_selector('a[data-jk]')  # Company page format
                if title_elem:
                    job_data['title'] = title_elem.inner_text().strip()

                # Extract company name - company pages may not show it
                company_elem = card.query_selector('span[data-testid="company-name"]')
                if company_elem:
                    job_data['company'] = company_elem.inner_text().strip()
                elif use_company_page:
                    job_data['company'] = 'Goodwill Industries of Central Texas'

                # Extract location
                location_elem = card.query_selector('div[data-testid="text-location"]')
                if not location_elem:
                    location_elem = card.query_selector('div.companyLocation')  # Company page format
                if location_elem:
                    job_data['location'] = location_elem.inner_text().strip()

                # Extract salary if available
                salary_elem = card.query_selector('div[data-testid="attribute_snippet_testid"]')
                if not salary_elem:
                    salary_elem = card.query_selector('div.salary-snippet')
                if salary_elem:
                    salary_text = salary_elem.inner_text().strip()
                    if salary_text:
                        job_data['salary'] = salary_text

                # Extract job snippet/description
                snippet_elem = card.query_selector('div.underShelfFooter ul li')
                if not snippet_elem:
                    snippet_elem = card.query_selector('div.job-snippet')
                if snippet_elem:
                    job_data['snippet'] = snippet_elem.inner_text().strip()

                # Extract job URL - handle both search and company page formats
                link_elem = card.query_selector('h2.jobTitle a')
                if not link_elem:
                    link_elem = card.query_selector('a[data-jk]')  # Company page format
                if not link_elem:
                    link_elem = card.query_selector('a.jcs-JobTitle')  # Alternative format
                if not link_elem:
                    # Try to find any link with jobTitle
                    link_elem = card.query_selector('a[href*="viewjob"]')

                # Try to get data-jk first (most reliable on company pages)
                data_jk = None
                if link_elem:
                    data_jk = link_elem.get_attribute('data-jk')

                # If we found data-jk, construct URL from it
                if data_jk:
                    job_data['job_key'] = data_jk
                    job_data['url'] = f"https://www.indeed.com/viewjob?jk={data_jk}"
                elif link_elem:
                    # Fallback to href attribute
                    href = link_elem.get_attribute('href')
                    if href and href != '#':
                        if href.startswith('/'):
                            job_data['url'] = f"https://www.indeed.com{href}"
                        elif href.startswith('http'):
                            job_data['url'] = href
                        else:
                            job_data['url'] = f"https://www.indeed.com/viewjob?jk={href}"

                        # Extract job key from URL
                        if 'jk=' in href:
                            job_key = href.split('jk=')[1].split('&')[0]
                            job_data['job_key'] = job_key

                # Extract posted date
                date_elem = card.query_selector('span[data-testid="myJobsStateDate"]')
                if not date_elem:
                    date_elem = card.query_selector('span.date')
                if date_elem:
                    job_data['posted_date'] = date_elem.inner_text().strip()

                if job_data and job_data.get('title'):
                    # Check for duplicates based on title and location
                    is_duplicate = any(
                        j.get('title') == job_data.get('title') and
                        j.get('location') == job_data.get('location')
                        for j in jobs
                    )
                    if not is_duplicate:
                        jobs.append(job_data)
                        print(f"  ✓ {idx}. {job_data.get('title')} - {job_data.get('company', 'N/A')}")
                    else:
                        print(f"  ⚠ {idx}. {job_data.get('title')} - Duplicate, skipping")

            except Exception as e:
                print(f"  ✗ Error extracting job {idx}: {e}")
                continue

        # Try to get more pages if they exist
        print("\nChecking for additional pages...")
        page_count = 1
        max_pages = 5  # Limit to prevent infinite loops

        while page_count < max_pages:
            try:
                # Look for next page button
                next_button = page.query_selector('a[data-testid="pagination-page-next"]')
                if not next_button:
                    print("No more pages found")
                    break

                print(f"Loading page {page_count + 1}...")
                next_button.click()
                time.sleep(3)

                # Wait for new jobs to load
                page.wait_for_selector('div.job_seen_beacon', timeout=10000)

                # Extract jobs from this page
                job_cards = page.query_selector_all('div.job_seen_beacon')
                print(f"Found {len(job_cards)} job postings on page {page_count + 1}")

                for idx, card in enumerate(job_cards, 1):
                    try:
                        job_data = {}

                        title_elem = card.query_selector('h2.jobTitle span[title]')
                        if not title_elem:
                            title_elem = card.query_selector('h2.jobTitle a span')
                        if title_elem:
                            job_data['title'] = title_elem.inner_text().strip()

                        company_elem = card.query_selector('span[data-testid="company-name"]')
                        if company_elem:
                            job_data['company'] = company_elem.inner_text().strip()

                        location_elem = card.query_selector('div[data-testid="text-location"]')
                        if location_elem:
                            job_data['location'] = location_elem.inner_text().strip()

                        salary_elem = card.query_selector('div[data-testid="attribute_snippet_testid"]')
                        if salary_elem:
                            salary_text = salary_elem.inner_text().strip()
                            if salary_text:
                                job_data['salary'] = salary_text

                        snippet_elem = card.query_selector('div.underShelfFooter ul li')
                        if snippet_elem:
                            job_data['snippet'] = snippet_elem.inner_text().strip()

                        link_elem = card.query_selector('h2.jobTitle a')
                        if link_elem:
                            href = link_elem.get_attribute('href')
                            if href:
                                if href.startswith('/'):
                                    job_data['url'] = f"https://www.indeed.com{href}"
                                else:
                                    job_data['url'] = href

                                if 'jk=' in href:
                                    job_key = href.split('jk=')[1].split('&')[0]
                                    job_data['job_key'] = job_key

                        date_elem = card.query_selector('span[data-testid="myJobsStateDate"]')
                        if date_elem:
                            job_data['posted_date'] = date_elem.inner_text().strip()

                        if job_data and job_data.get('title'):
                            # Check for duplicates
                            is_duplicate = any(
                                j.get('job_key') == job_data.get('job_key')
                                for j in jobs if j.get('job_key')
                            )
                            if not is_duplicate:
                                jobs.append(job_data)
                                print(f"  ✓ {len(jobs)}. {job_data.get('title')} - {job_data.get('company', 'N/A')}")

                    except Exception as e:
                        continue

                page_count += 1

            except Exception as e:
                print(f"Error loading additional pages: {e}")
                break

        # Now visit each job page to get detailed information
        print(f"\n{'=' * 60}")
        print(f"Extracting detailed information from {len(jobs)} jobs...")
        print(f"{'=' * 60}\n")

        for idx, job in enumerate(jobs, 1):
            if job.get('url'):
                print(f"[{idx}/{len(jobs)}] {job.get('title', 'N/A')[:50]}")
                try:
                    details = extract_job_details(page, job['url'])
                    job.update(details)
                    time.sleep(2)  # Be respectful to the server
                except Exception as e:
                    print(f"    ✗ Error: {str(e)[:50]}")
                    continue
            else:
                print(f"[{idx}/{len(jobs)}] {job.get('title', 'N/A')[:50]} - No URL available")

        context.close()
        browser.close()

    return jobs


def save_jobs(jobs, filename='indeed_jobs.json'):
    """Save jobs to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Indeed.com',
        'search_query': 'Goodwill Central Texas - Austin, TX',
        'total_jobs': len(jobs),
        'jobs': jobs
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(jobs)} jobs to {filename}")


def main():
    print("=" * 60)
    print("Indeed Job Scraper - Goodwill Central Texas")
    print("=" * 60)
    print()

    jobs = scrape_indeed_jobs(headless=True)  # Headless mode often works better with timeouts

    if jobs:
        save_jobs(jobs)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   Company: {job.get('company', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            if job.get('salary'):
                print(f"   Salary: {job.get('salary')}")
            if job.get('job_type'):
                print(f"   Type: {job.get('job_type')}")
            if job.get('posted_date'):
                print(f"   Posted: {job.get('posted_date')}")
            if job.get('description'):
                desc_preview = job.get('description')[:150].replace('\n', ' ')
                print(f"   Description: {desc_preview}...")
            if job.get('url'):
                print(f"   URL: {job.get('url')}")
    else:
        print("\nNo jobs found.")


if __name__ == "__main__":
    main()
