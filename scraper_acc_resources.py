#!/usr/bin/env python3
"""
ACC Basic Needs Resources Scraper
Scrapes community resources from Austin Community College social support page
"""

import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def scrape_acc_resources(headless=True):
    """
    Scrapes basic needs resources from ACC's social support page
    Handles pagination through all available pages
    """
    url = "https://students.austincc.edu/social-support/"
    resources = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print(f"Navigating to {url}")
        page.goto(url, wait_until="load", timeout=60000)
        time.sleep(5)

        # Wait for table to load
        print("Waiting for resources table to load...")
        try:
            page.wait_for_selector('table tbody tr', timeout=10000)
            print("Table found!")
        except PlaywrightTimeoutError:
            print("Warning: Could not find resources table")
            browser.close()
            return []

        current_page = 1
        total_pages = None

        while True:
            print(f"\nScraping page {current_page}...")

            # Wait for table rows to be visible
            time.sleep(2)

            # Extract rows from current page
            rows = page.query_selector_all('table tbody tr')
            print(f"Found {len(rows)} resources on page {current_page}")

            for idx, row in enumerate(rows, 1):
                try:
                    resource_data = {}

                    # Extract all cells from the row
                    cells = row.query_selector_all('td')

                    if len(cells) >= 4:  # Minimum expected columns
                        # Type
                        if len(cells) > 0:
                            resource_data['type'] = cells[0].inner_text().strip()

                        # Name
                        if len(cells) > 1:
                            resource_data['name'] = cells[1].inner_text().strip()

                        # Description
                        if len(cells) > 2:
                            resource_data['description'] = cells[2].inner_text().strip()

                        # Website - extract link if available
                        if len(cells) > 3:
                            website_cell = cells[3]
                            link = website_cell.query_selector('a')
                            if link:
                                resource_data['website'] = link.get_attribute('href')
                                resource_data['website_text'] = link.inner_text().strip()
                            else:
                                resource_data['website'] = website_cell.inner_text().strip()

                        # Phone
                        if len(cells) > 4:
                            resource_data['phone'] = cells[4].inner_text().strip()

                        # County
                        if len(cells) > 5:
                            resource_data['county'] = cells[5].inner_text().strip()

                        if resource_data.get('name'):
                            resources.append(resource_data)
                            print(f"  ✓ {len(resources)}. {resource_data.get('name')}")

                except Exception as e:
                    print(f"  ✗ Error extracting resource {idx}: {e}")
                    continue

            # Check if there's a next page (footable pagination)
            try:
                # Look for the next button (›) in footable pagination
                next_button = page.query_selector('ul.pagination a[data-page="next"]:not(.disabled), ul.pagination li.next:not(.disabled) a')

                # If no explicit next button, try to find the next page number
                if not next_button or not next_button.is_visible():
                    # Find the current active page
                    active_page = page.query_selector('ul.pagination li.active a, ul.pagination li.active span')
                    if active_page:
                        current_page_text = active_page.inner_text().strip()
                        if current_page_text.isdigit():
                            next_page_num = str(int(current_page_text) + 1)
                            # Find and click the next page number
                            pagination_links = page.query_selector_all('ul.pagination li:not(.disabled):not(.active) a')
                            for link in pagination_links:
                                link_text = link.inner_text().strip()
                                if link_text == next_page_num:
                                    next_button = link
                                    break

                if next_button and next_button.is_visible():
                    # Determine total pages if we haven't yet
                    if not total_pages:
                        # Get all page number links
                        page_numbers = page.query_selector_all('ul.pagination li:not(.disabled):not(.prev):not(.next):not(.first):not(.last) a')
                        if page_numbers:
                            # Look for the highest page number visible
                            max_visible = 0
                            for pn in page_numbers:
                                text = pn.inner_text().strip()
                                if text.isdigit():
                                    max_visible = max(max_visible, int(text))
                            if max_visible > 0:
                                # Check if there's a "..." which indicates more pages
                                if page.query_selector('ul.pagination li:has-text("...")'):
                                    print(f"Multiple pages detected (at least {max_visible}+)")
                                else:
                                    total_pages = max_visible
                                    print(f"Total pages detected: {total_pages}")

                    print(f"Navigating to page {current_page + 1}...")
                    next_button.click()
                    current_page += 1
                    time.sleep(3)  # Wait for new page to load
                else:
                    print("\nNo more pages found.")
                    break

            except Exception as e:
                print(f"\nError navigating to next page: {e}")
                print("Reached end of pagination.")
                break

        browser.close()

    return resources


def save_resources(resources, filename='acc_resources.json'):
    """Save resources to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Austin Community College - Basic Needs Resources',
        'url': 'https://students.austincc.edu/social-support/',
        'total_resources': len(resources),
        'resources': resources
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(resources)} resources to {filename}")


def main():
    print("=" * 60)
    print("ACC Basic Needs Resources Scraper")
    print("=" * 60)
    print()

    resources = scrape_acc_resources(headless=True)

    if resources:
        save_resources(resources)

        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total resources scraped: {len(resources)}")

        # Group by type
        types = {}
        for resource in resources:
            resource_type = resource.get('type', 'Unknown')
            types[resource_type] = types.get(resource_type, 0) + 1

        print("\nResources by type:")
        for resource_type, count in sorted(types.items()):
            print(f"  {resource_type}: {count}")

        print("\nFirst 5 resources:")
        for i, resource in enumerate(resources[:5], 1):
            print(f"\n{i}. {resource.get('name', 'N/A')}")
            print(f"   Type: {resource.get('type', 'N/A')}")
            print(f"   County: {resource.get('county', 'N/A')}")
            if resource.get('phone'):
                print(f"   Phone: {resource['phone']}")
            if resource.get('website'):
                print(f"   Website: {resource['website']}")
    else:
        print("\nNo resources found.")


if __name__ == "__main__":
    main()
