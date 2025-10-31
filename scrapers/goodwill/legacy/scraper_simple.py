#!/usr/bin/env python3
"""
Goodwill Central Texas Job Scraper - Simple Version
Scrapes basic job information from all postings
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def scrape_goodwill_jobs(headless=True):
    """
    Scrapes job postings from Goodwill Central Texas careers page
    """
    url = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter"
    jobs = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print(f"Navigating to {url}")
        page.goto(url, wait_until="networkidle")

        # Wait for job listings
        try:
            page.wait_for_selector('div.current-openings-list', timeout=15000)
            print("Job listings container found!")
        except PlaywrightTimeoutError:
            print("Warning: Could not find job listings container")
            return []

        # Click "View all" button
        try:
            view_all_button = page.query_selector('sdf-button#recruitment_careerCenter_showAllJobs')
            if view_all_button:
                print("Clicking 'View all' button...")
                view_all_button.click()
                time.sleep(3)
        except Exception as e:
            print(f"Could not click 'View all' button: {e}")

        # Scroll to load all jobs
        print("Scrolling to load all jobs...")
        previous_count = 0
        scroll_attempts = 0

        while scroll_attempts < 20:
            current_jobs = page.query_selector_all('div.current-openings-item')
            current_count = len(current_jobs)

            if current_count > previous_count:
                print(f"Loaded {current_count} jobs so far...")
                previous_count = current_count
                scroll_attempts = 0
            else:
                scroll_attempts += 1

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

            if current_count >= 90:
                print("All jobs loaded!")
                break

        print(f"Finished scrolling. Total jobs loaded: {current_count}")

        # Extract job information
        job_elements = page.query_selector_all('div.current-openings-item')
        print(f"\nExtracting information from {len(job_elements)} jobs...")

        for idx, element in enumerate(job_elements, 1):
            try:
                job_data = {}

                # Extract job title
                title_link = element.query_selector('sdf-link')
                if title_link:
                    job_data['title'] = title_link.inner_text().strip()

                # Extract location
                location_elem = element.query_selector('label.current-opening-location-item span')
                if location_elem:
                    job_data['location'] = location_elem.inner_text().strip()

                # Extract posting date
                date_elem = element.query_selector('span.current-opening-post-date')
                if date_elem:
                    job_data['posted_date'] = date_elem.inner_text().strip()

                # Extract job type - FIX: use type_elem not element
                type_elem = element.query_selector('span.current-opening-worker-catergory')
                if type_elem:
                    job_data['job_type'] = type_elem.inner_text().strip()

                # Extract job ID from element ID
                element_id = element.get_attribute('id')
                if element_id:
                    job_data['job_id'] = element_id

                if job_data and job_data.get('title'):
                    jobs.append(job_data)
                    print(f"  ✓ {idx}. {job_data.get('title')}")

            except Exception as e:
                print(f"  ✗ Error extracting job {idx}: {e}")
                continue

        browser.close()

    return jobs


def save_jobs(jobs, filename='jobs.json'):
    """Save jobs to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'total_jobs': len(jobs),
        'jobs': jobs
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(jobs)} jobs to {filename}")


def main():
    print("=" * 60)
    print("Goodwill Central Texas Job Scraper")
    print("=" * 60)
    print()

    jobs = scrape_goodwill_jobs(headless=True)

    if jobs:
        save_jobs(jobs)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Type: {job.get('job_type', 'N/A')}")
            print(f"   Posted: {job.get('posted_date', 'N/A')}")
    else:
        print("\nNo jobs found.")


if __name__ == "__main__":
    main()
