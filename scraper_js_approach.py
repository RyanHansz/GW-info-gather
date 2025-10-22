#!/usr/bin/env python3
"""
Alternative approach using JavaScript to extract job data including URLs
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

url = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter"

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch(headless=False)  # Visible for debugging
    page = browser.new_page()

    print(f"Navigating to {url}")
    page.goto(url, wait_until="networkidle")

    # Wait for job listings
    page.wait_for_selector('div.current-openings-list', timeout=15000)
    time.sleep(2)

    # Click "View all" button
    view_all_button = page.query_selector('sdf-button#recruitment_careerCenter_showAllJobs')
    if view_all_button:
        print("Clicking 'View all' button...")
        view_all_button.click()
        time.sleep(3)

    # Scroll to load all jobs
    print("Scrolling to load all jobs...")
    for _ in range(10):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

    # Try to extract job data using JavaScript
    print("\nTrying to extract job data via JavaScript...")

    # Check if there's any global variable or data we can access
    job_data_js = page.evaluate("""
    () => {
        // Try to find job elements and extract onclick or data attributes
        const jobs = [];
        const jobElements = document.querySelectorAll('div.current-openings-item');

        jobElements.forEach((el, idx) => {
            const job = {
                element_id: el.id
            };

            // Get title link
            const link = el.querySelector('sdf-link');
            if (link) {
                job.title = link.textContent.trim();
                // Check for onclick or any data attributes
                const attrs = link.attributes;
                for (let i = 0; i < attrs.length; i++) {
                    const attr = attrs[i];
                    job[`link_${attr.name}`] = attr.value;
                }
            }

            // Get all data attributes from the element
            const allAttrs = el.attributes;
            for (let i = 0; i < allAttrs.length; i++) {
                const attr = allAttrs[i];
                if (attr.name.startsWith('data-')) {
                    job[attr.name] = attr.value;
                }
            }

            jobs.push(job);
        });

        return jobs;
    }
    """)

    print(f"Found {len(job_data_js)} jobs")
    print("\nFirst job attributes:")
    print(json.dumps(job_data_js[0] if job_data_js else {}, indent=2))

    input("\nPress Enter to close browser...")
    browser.close()
