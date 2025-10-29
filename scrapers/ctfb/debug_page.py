#!/usr/bin/env python3
"""
Debug script to capture the CTFB page structure for analysis
"""

import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_page():
    """Capture page info for debugging"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = "https://www.centraltexasfoodbank.org/food-assistance/get-food-now"
        print(f"Loading: {url}")
        driver.get(url)

        # Wait for page to fully load
        print("Waiting 10 seconds for page to load...")
        time.sleep(10)

        # Save screenshot
        driver.save_screenshot('data/ctfb_page_screenshot.png')
        print("✓ Saved screenshot to data/ctfb_page_screenshot.png")

        # Get page source
        with open('data/ctfb_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✓ Saved page source to data/ctfb_page_source.html")

        # Try to extract any data-* attributes that might contain location info
        print("\nSearching for elements with data attributes...")
        elements_with_data = driver.find_elements(By.XPATH, "//*[@data-*]")
        print(f"Found {len(elements_with_data)} elements with data attributes")

        # Look for common container IDs
        print("\nChecking common container IDs...")
        common_ids = ['locations', 'map', 'food-finder', 'locator', 'pantries', 'sites']
        for container_id in common_ids:
            try:
                element = driver.find_element(By.ID, container_id)
                print(f"  ✓ Found #{container_id}")
                print(f"    Classes: {element.get_attribute('class')}")
                print(f"    Data attributes: {[attr for attr in element.get_attribute('outerHTML').split() if 'data-' in attr][:5]}")
            except:
                pass

        # Check for iframes
        print("\nChecking for iframes...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"Found {len(iframes)} iframes")
        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute('src')
            if src:
                print(f"  {i+1}. {src}")

        # Try to execute JavaScript to find location data
        print("\nExecuting JavaScript to search for location data...")
        js_result = driver.execute_script("""
            // Search for location-related data in window object
            const results = {};

            // Check common variable names
            const varNames = ['locations', 'sites', 'pantries', 'markers', 'foodBanks', 'agencies'];
            for (const name of varNames) {
                if (window[name]) {
                    results[name] = window[name];
                }
            }

            // Check Drupal settings
            if (window.Drupal && window.Drupal.settings) {
                results.drupalSettings = window.Drupal.settings;
            }

            // Check for jQuery data
            if (window.jQuery) {
                const dataKeys = [];
                jQuery('*').each(function() {
                    const data = jQuery(this).data();
                    if (Object.keys(data).length > 0) {
                        dataKeys.push(Object.keys(data));
                    }
                });
                results.jqueryDataKeys = [...new Set(dataKeys.flat())];
            }

            // Get all script tags content (look for embedded JSON)
            const scripts = Array.from(document.querySelectorAll('script'));
            const scriptsWithJSON = scripts.filter(s =>
                s.textContent.includes('location') ||
                s.textContent.includes('pantry') ||
                s.textContent.includes('latitude')
            ).length;
            results.scriptsWithLocationKeywords = scriptsWithJSON;

            return results;
        """)

        print("\nJavaScript search results:")
        print(json.dumps(js_result, indent=2, default=str))

        driver.quit()

        print("\n" + "=" * 80)
        print("DEBUG COMPLETE")
        print("=" * 80)
        print("\nFiles saved:")
        print("  - data/ctfb_page_screenshot.png (visual snapshot)")
        print("  - data/ctfb_page_source.html (full HTML)")
        print("\nNext steps:")
        print("  1. Open the HTML file and search for 'location', 'pantry', 'latitude'")
        print("  2. Look at the screenshot to see what elements are visible")
        print("  3. Inspect the HTML structure to find the location list elements")

    except Exception as e:
        print(f"Error: {e}")
        driver.quit()

if __name__ == "__main__":
    debug_page()
