#!/usr/bin/env python3
"""
GSG Talent Solutions Job Scraper - API Version
Scrapes job postings directly from the JSON API
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright


def scrape_gsg_jobs_api(headless=True):
    """
    Scrapes job postings by intercepting the API response
    """
    url = "https://jobs.gsgtalentsolutions.com/"
    jobs = []
    api_data = None

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        # Intercept API responses
        def handle_response(response):
            nonlocal api_data
            if 'json/index.smpl' in response.url and 'list_posts' in response.url:
                try:
                    data = response.json()
                    api_data = data
                    print(f"✓ Captured API response with job data")
                except:
                    pass

        page.on("response", handle_response)

        print(f"Navigating to {url}")
        page.goto(url, wait_until="networkidle")
        time.sleep(5)  # Wait for API call to complete

        browser.close()

    # Debug: save API data
    if api_data:
        with open('gsg_api_debug.json', 'w') as f:
            json.dump(api_data, f, indent=2)
        print("Saved API response to gsg_api_debug.json")

    # Process API data if we got it
    if api_data and 'ResultSet' in api_data and 'list' in api_data['ResultSet']:
        job_list = api_data['ResultSet']['list']
        print(f"\nProcessing {len(job_list)} jobs from API...")

        for idx, post in enumerate(job_list, 1):
            try:
                job_data = {
                    'title': post.get('POST_TITLE', '').strip(),
                    'location': post.get('POST_LOCATION', '').strip(),
                    'employment_type': post.get('POST_EMPLOYMENT_TYPE', '').strip(),
                    'job_number': post.get('POST_JOB_NUMBER', ''),
                    'category': post.get('POST_CATEGORY', '').strip(),
                    'posted_date': post.get('POST_DATE_F', '').strip(),
                }

                # Build job URL
                if post.get('POST_ID'):
                    job_data['url'] = f"https://jobs.gsgtalentsolutions.com/?p=job%2F{post['POST_ID']}"

                # Extract pay rate
                if post.get('POST_PAYRATE'):
                    job_data['pay_rate'] = post['POST_PAYRATE'].strip()
                elif post.get('POST_SALARY'):
                    job_data['pay_rate'] = post['POST_SALARY'].strip()

                if job_data['title']:
                    jobs.append(job_data)
                    print(f"  ✓ {idx}. {job_data['title']}")

            except Exception as e:
                print(f"  ✗ Error processing job {idx}: {e}")
                continue

    return jobs


def save_jobs(jobs, filename='gsg_jobs.json'):
    """Save jobs to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'GSG Talent Solutions',
        'url': 'https://jobs.gsgtalentsolutions.com/',
        'total_jobs': len(jobs),
        'jobs': jobs
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(jobs)} jobs to {filename}")


def main():
    print("=" * 60)
    print("GSG Talent Solutions Job Scraper (API)")
    print("=" * 60)
    print()

    jobs = scrape_gsg_jobs_api(headless=True)

    if jobs:
        save_jobs(jobs)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total jobs scraped: {len(jobs)}")
        print("\nFirst 10 jobs:")
        for i, job in enumerate(jobs[:10], 1):
            print(f"\n{i}. {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Pay Rate: {job.get('pay_rate', 'N/A')}")
            print(f"   Type: {job.get('employment_type', 'N/A')}")
            print(f"   Category: {job.get('category', 'N/A')}")

        if len(jobs) > 10:
            print(f"\n... and {len(jobs) - 10} more jobs")
    else:
        print("\nNo jobs found.")


if __name__ == "__main__":
    main()
