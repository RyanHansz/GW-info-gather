#!/usr/bin/env python3
"""
Central Texas Food Bank - Food Assistance Locations Scraper
Scrapes food assistance locations from the CTFB "Get Food Now" page
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
import re


def fetch_page_source():
    """Fetch the main page to look for embedded data or API endpoints"""
    url = "https://www.centraltexasfoodbank.org/food-assistance/get-food-now"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        return html
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None


def extract_api_endpoint(html):
    """Try to find API endpoints or embedded data in the HTML"""

    # Look for common patterns
    patterns = [
        r'"apiUrl":\s*"([^"]+)"',
        r'"endpoint":\s*"([^"]+)"',
        r'data-api[^=]*=\s*["\']([^"\']+)["\']',
        r'fetch\(["\']([^"\']+food[^"\']+)["\']',
        r'axios\.[get|post]+\(["\']([^"\']+)["\']',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"Found potential API endpoint(s) with pattern '{pattern}':")
            for match in matches:
                print(f"  - {match}")

    # Look for embedded JSON data
    json_patterns = [
        r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',
        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        r'var\s+locations\s*=\s*(\[.*?\]);',
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        if matches:
            print(f"\nFound embedded JSON data with pattern '{pattern}'")
            for i, match in enumerate(matches[:3]):  # Show first 3 matches
                print(f"  Match {i+1} (first 200 chars): {match[:200]}...")

    return html


def search_for_iframe_or_widget(html):
    """Check if the food finder is embedded as an iframe or widget"""

    # Look for iframes
    iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
    iframes = re.findall(iframe_pattern, html, re.IGNORECASE)

    if iframes:
        print("\nFound iframe(s):")
        for iframe in iframes:
            if 'food' in iframe.lower() or 'location' in iframe.lower() or 'map' in iframe.lower():
                print(f"  - {iframe}")

    # Look for widget/plugin indicators
    widget_patterns = [
        r'data-widget[^=]*=["\']([^"\']+)["\']',
        r'class=["\'][^"\']*widget[^"\']*["\']',
    ]

    for pattern in widget_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"\nFound widget indicator: {matches[:5]}")


def try_common_api_endpoints():
    """Try common API endpoint patterns for food bank location finders"""

    base_url = "https://www.centraltexasfoodbank.org"

    # Common patterns for food bank APIs
    potential_endpoints = [
        "/api/locations",
        "/api/food-locations",
        "/api/pantries",
        "/wp-json/wp/v2/locations",
        "/food-assistance/locations",
        "/locations.json",
        "/api/agencies",
    ]

    print("\n" + "=" * 80)
    print("Trying common API endpoints...")
    print("=" * 80)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    for endpoint in potential_endpoints:
        url = base_url + endpoint
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    data = response.read().decode('utf-8')

                    print(f"\n✓ Found: {url}")
                    print(f"  Content-Type: {content_type}")
                    print(f"  Response size: {len(data)} bytes")

                    # Try to parse as JSON
                    try:
                        json_data = json.loads(data)
                        print(f"  Valid JSON with {len(json_data)} items" if isinstance(json_data, list) else "  Valid JSON object")
                        return url, json_data
                    except:
                        print(f"  Not JSON, first 200 chars: {data[:200]}")

        except urllib.error.HTTPError as e:
            pass  # Silent fail for 404s
        except Exception as e:
            pass  # Silent fail for other errors

    print("\nNo common API endpoints found.")
    return None, None


def main():
    """Main scraper function"""
    print("=" * 80)
    print("Central Texas Food Bank - Food Assistance Scraper")
    print("=" * 80)
    print()

    # Step 1: Fetch and analyze page
    print("Step 1: Fetching and analyzing page source...")
    html = fetch_page_source()

    if html:
        print(f"✓ Fetched page ({len(html)} bytes)")

        # Step 2: Look for API endpoints in HTML
        print("\nStep 2: Searching for API endpoints in HTML...")
        extract_api_endpoint(html)

        # Step 3: Check for iframes/widgets
        print("\nStep 3: Checking for iframes or embedded widgets...")
        search_for_iframe_or_widget(html)

    # Step 4: Try common API endpoints
    print("\nStep 4: Trying common API endpoint patterns...")
    endpoint, data = try_common_api_endpoints()

    if endpoint and data:
        print(f"\n✓ Successfully found data at: {endpoint}")

        # Save the data
        output = {
            'scraped_at': datetime.now().isoformat(),
            'source': 'Central Texas Food Bank',
            'source_url': 'https://www.centraltexasfoodbank.org/food-assistance/get-food-now',
            'api_endpoint': endpoint,
            'locations': data if isinstance(data, list) else [data],
            'total_locations': len(data) if isinstance(data, list) else 1
        }

        with open('data/ctfb_locations.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved {output['total_locations']} locations to data/ctfb_locations.json")
    else:
        print("\n⚠ Could not automatically find data source.")
        print("The site may use:")
        print("  - A third-party widget (like Google Maps with custom data)")
        print("  - Client-side JavaScript that loads data dynamically")
        print("  - A more complex API that requires authentication or specific parameters")
        print("\nNext steps:")
        print("  1. Inspect the network tab in browser DevTools while loading the page")
        print("  2. Look for XHR/Fetch requests that load location data")
        print("  3. Check if it uses a service like Mapbox, Google Maps API, or similar")


if __name__ == "__main__":
    main()
