#!/usr/bin/env python3
"""
Central Texas Food Bank - Food Assistance Locations Scraper (Selenium version)
Uses browser automation to extract location data from the interactive map
"""

import json
import time
from datetime import datetime
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠ Selenium not installed. Install with: pip install selenium")


def setup_driver():
    """Set up Chrome driver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("\nMake sure you have Chrome and chromedriver installed:")
        print("  macOS: brew install chromedriver")
        print("  Or download from: https://chromedriver.chromium.org/")
        return None


def scrape_locations_selenium():
    """Scrape food assistance locations using Selenium"""
    driver = setup_driver()
    if not driver:
        return None

    try:
        url = "https://www.centraltexasfoodbank.org/food-assistance/get-food-now"
        print(f"Loading page: {url}")
        driver.get(url)

        # Wait for page to load
        time.sleep(5)

        print("Waiting for location elements to load...")

        # Try to find location list elements
        wait = WebDriverWait(driver, 20)

        # Look for common location list patterns
        location_selectors = [
            "div.location-item",
            "div.location",
            "li.location",
            "div[class*='location']",
            "div[class*='pantry']",
            "div[class*='site']",
        ]

        locations = []
        for selector in location_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and len(elements) > 2:
                    print(f"✓ Found {len(elements)} elements with selector: {selector}")
                    locations = elements
                    break
            except:
                continue

        if not locations:
            print("⚠ Could not find location elements. Trying JavaScript extraction...")

            # Try to extract data from JavaScript variables
            js_data = driver.execute_script("""
                // Look for common variable names that might hold location data
                const possibleVars = ['locations', 'sites', 'pantries', 'foodSites', 'markers'];
                for (const varName of possibleVars) {
                    if (window[varName]) {
                        return {source: varName, data: window[varName]};
                    }
                }

                // Look in common frameworks
                if (window.Drupal && window.Drupal.settings) {
                    return {source: 'Drupal.settings', data: window.Drupal.settings};
                }

                return null;
            """)

            if js_data:
                print(f"✓ Found data in JavaScript variable: {js_data.get('source')}")
                driver.quit()
                return js_data.get('data')

        # Extract location data from elements
        print(f"\nExtracting data from {len(locations)} location elements...")
        extracted_locations = []

        for i, location in enumerate(locations[:100], 1):  # Limit to first 100
            try:
                # Extract text content
                text = location.text
                html = location.get_attribute('innerHTML')

                # Try to parse structured data
                location_data = {
                    'text': text,
                    'html_snippet': html[:200] if html else None
                }

                # Try to find specific fields
                try:
                    name_elem = location.find_element(By.CSS_SELECTOR, "h2, h3, h4, .name, .title, [class*='name']")
                    location_data['name'] = name_elem.text
                except:
                    pass

                try:
                    address_elem = location.find_element(By.CSS_SELECTOR, ".address, [class*='address']")
                    location_data['address'] = address_elem.text
                except:
                    pass

                extracted_locations.append(location_data)

                if i % 10 == 0:
                    print(f"  Processed {i}/{len(locations)} locations...")

            except Exception as e:
                continue

        driver.quit()
        return extracted_locations if extracted_locations else None

    except Exception as e:
        print(f"Error during scraping: {e}")
        driver.quit()
        return None


def save_locations(locations, filename='data/ctfb_locations.json'):
    """Save locations to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Central Texas Food Bank',
        'source_url': 'https://www.centraltexasfoodbank.org/food-assistance/get-food-now',
        'method': 'selenium',
        'locations': locations if isinstance(locations, list) else [locations],
        'total_locations': len(locations) if isinstance(locations, list) else 1
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {output['total_locations']} locations to {filename}")


def main():
    """Main function"""
    print("=" * 80)
    print("Central Texas Food Bank - Food Assistance Scraper (Selenium)")
    print("=" * 80)
    print()

    if not SELENIUM_AVAILABLE:
        print("Please install selenium: pip install selenium")
        sys.exit(1)

    locations = scrape_locations_selenium()

    if locations:
        save_locations(locations)
        print("\n✓ Scraping completed successfully!")

        # Show sample
        if isinstance(locations, list) and len(locations) > 0:
            print("\nSample location:")
            print(json.dumps(locations[0], indent=2))
    else:
        print("\n⚠ No locations extracted.")
        print("\nThe site may require manual inspection to determine the exact data structure.")


if __name__ == "__main__":
    main()
