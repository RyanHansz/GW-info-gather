#!/usr/bin/env python3
"""
Indeed Job Scraper for Goodwill Central Texas
Scrapes job postings from Indeed.com
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def scrape_indeed_jobs(headless=True):
    """
    Scrapes Goodwill Central Texas job postings from Indeed
    """
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
        page.goto(url, wait_until="networkidle")
        time.sleep(2)

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

                # Extract job title
                title_elem = card.query_selector('h2.jobTitle a span')
                if not title_elem:
                    title_elem = card.query_selector('h2.jobTitle span[title]')
                if title_elem:
                    job_data['title'] = title_elem.inner_text().strip()

                # Extract company name
                company_elem = card.query_selector('span[data-testid="company-name"]')
                if company_elem:
                    job_data['company'] = company_elem.inner_text().strip()

                # Extract location
                location_elem = card.query_selector('div[data-testid="text-location"]')
                if location_elem:
                    job_data['location'] = location_elem.inner_text().strip()

                # Extract salary if available
                salary_elem = card.query_selector('div[data-testid="attribute_snippet_testid"]')
                if salary_elem:
                    salary_text = salary_elem.inner_text().strip()
                    if salary_text:
                        job_data['salary'] = salary_text

                # Extract job snippet/description
                snippet_elem = card.query_selector('div.underShelfFooter ul li')
                if snippet_elem:
                    job_data['snippet'] = snippet_elem.inner_text().strip()

                # Extract job URL
                link_elem = card.query_selector('h2.jobTitle a')
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            job_data['url'] = f"https://www.indeed.com{href}"
                        else:
                            job_data['url'] = href

                        # Extract job key from URL
                        if 'jk=' in href:
                            job_key = href.split('jk=')[1].split('&')[0]
                            job_data['job_key'] = job_key

                # Extract posted date
                date_elem = card.query_selector('span[data-testid="myJobsStateDate"]')
                if date_elem:
                    job_data['posted_date'] = date_elem.inner_text().strip()

                if job_data and job_data.get('title'):
                    jobs.append(job_data)
                    print(f"  ✓ {idx}. {job_data.get('title')} - {job_data.get('company', 'N/A')}")

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

    jobs = scrape_indeed_jobs(headless=False)  # Use visible browser to avoid detection

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
            if job.get('posted_date'):
                print(f"   Posted: {job.get('posted_date')}")
            if job.get('url'):
                print(f"   URL: {job.get('url')}")
    else:
        print("\nNo jobs found.")


if __name__ == "__main__":
    main()
