#!/usr/bin/env python3
"""
Goodwill Central Texas Job Scraper
Scrapes job postings from the ADP Workforce Now recruitment portal
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def scrape_goodwill_jobs(headless=True):
    """
    Scrapes job postings from Goodwill Central Texas careers page

    Args:
        headless: Whether to run browser in headless mode (default: True)

    Returns:
        List of job dictionaries containing job details
    """
    url = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter"

    jobs = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print(f"Navigating to {url}")
        page.goto(url, wait_until="networkidle")

        # Wait for job listings to load
        print("Waiting for job listings to load...")
        try:
            page.wait_for_selector('div.current-openings-list', timeout=15000)
            print("Job listings container found!")
        except PlaywrightTimeoutError:
            print("Warning: Could not find job listings container")

        # Click "View all" button to load all jobs
        print("Looking for 'View all' button to load all jobs...")
        try:
            view_all_button = page.query_selector('sdf-button#recruitment_careerCenter_showAllJobs')
            if view_all_button:
                print("Clicking 'View all' button...")
                view_all_button.click()
                time.sleep(3)  # Wait for navigation or load
        except Exception as e:
            print(f"Could not click 'View all' button: {e}")

        # Scroll to load more jobs (infinite scroll)
        print("Scrolling to load all jobs...")
        previous_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 20

        while scroll_attempts < max_scroll_attempts:
            # Get current count of jobs
            current_jobs = page.query_selector_all('div.current-openings-item')
            current_count = len(current_jobs)

            if current_count > previous_count:
                print(f"Loaded {current_count} jobs so far...")
                previous_count = current_count
                scroll_attempts = 0  # Reset if we're still loading
            else:
                scroll_attempts += 1

            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

            # Check if we've loaded all jobs (90 expected)
            if current_count >= 90:
                print("All jobs loaded!")
                break

        print(f"Finished scrolling. Total jobs loaded: {current_count}")

        # Find all job elements with the correct selector
        job_elements = page.query_selector_all('div.current-openings-item')

        if not job_elements:
            # Save HTML for debugging
            content = page.content()
            with open('page_debug.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Could not find job elements. Saved page HTML to page_debug.html for inspection")
        else:
            print(f"Found {len(job_elements)} job postings!")

        # First pass: Extract basic job information and click each to get jobId from URL
        print("\nExtracting job information and URLs...")
        basic_jobs = []
        base_url = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter"

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

                # Extract job type
                type_elem = element.query_selector('span.current-opening-worker-catergory')
                if type_elem:
                    job_data['job_type'] = element.inner_text().strip()

                # Extract job ID from element ID
                element_id = element.get_attribute('id')
                if element_id:
                    job_data['job_id'] = element_id

                # Click to get the actual URL with jobId
                if title_link and job_data.get('title'):
                    try:
                        element.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        title_link.click()
                        time.sleep(1.5)

                        # Get URL which now has jobId parameter
                        current_url = page.url
                        if 'jobId=' in current_url:
                            job_data['url'] = current_url
                            job_id = current_url.split('jobId=')[1].split('&')[0]
                            job_data['job_id_number'] = job_id
                            print(f"  {idx}. {job_data.get('title')[:50]} (JobID: {job_id})")
                        else:
                            print(f"  {idx}. {job_data.get('title')[:50]} (No jobId in URL)")

                        # Go back
                        page.go_back()
                        time.sleep(1)
                    except Exception as e:
                        print(f"  {idx}. {job_data.get('title')[:50]} - Error getting URL: {str(e)[:50]}")
                        # Try to go back
                        try:
                            page.go_back()
                            time.sleep(1)
                        except:
                            pass

                if job_data and job_data.get('title'):
                    basic_jobs.append(job_data)

            except Exception as e:
                print(f"Error extracting info for job {idx}: {e}")
                continue

        # Second pass: Visit each job URL directly to get detailed information
        print(f"\nExtracting detailed information for {len(basic_jobs)} jobs with URLs...")
        for idx, job_data in enumerate(basic_jobs, 1):
            try:
                job_url = job_data.get('url')
                if not job_url:
                    jobs.append(job_data)
                    continue

                print(f"→ [{idx}/{len(basic_jobs)}] {job_data.get('title')[:50]}...")

                # Navigate directly to the job URL
                page.goto(job_url, wait_until="networkidle")
                time.sleep(1)

                # Extract job details
                desc_container = page.query_selector('div.recruitment-container')
                if desc_container:
                    job_data['description'] = desc_container.inner_text().strip()

                # Extract requisition ID
                req_id_elem = page.query_selector('span[class*="requisition"], div[class*="requisition"]')
                if req_id_elem:
                    req_text = req_id_elem.inner_text().strip()
                    if req_text:
                        job_data['requisition_id'] = req_text

                # Extract salary range
                salary_elem = page.query_selector('span[class*="salary"], div[class*="alary"]')
                if salary_elem:
                    salary_text = salary_elem.inner_text().strip()
                    if salary_text and 'alary' in salary_text.lower():
                        job_data['salary_range'] = salary_text

                jobs.append(job_data)

            except Exception as e:
                print(f"  Warning: Could not extract details: {e}")
                jobs.append(job_data)

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
        print("\nNo jobs found. Check page_debug.html to inspect the page structure.")
        print("You may need to adjust the selectors in the script.")


if __name__ == "__main__":
    main()
