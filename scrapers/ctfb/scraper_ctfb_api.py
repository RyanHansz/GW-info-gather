#!/usr/bin/env python3
"""
Central Texas Food Bank - Food Assistance Locations Scraper
Uses the REST API endpoint discovered via browser DevTools
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from taxonomy_mappings import map_services, map_amenities


def fetch_locations_page(page_num):
    """
    Fetch a page of locations from the API

    Args:
        page_num: Page number (0-indexed or 1-indexed, we'll test)

    Returns:
        List of location objects, or None if error
    """
    url = f"https://www.centraltexasfoodbank.org/rest/node/location/{page_num}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # End of pages
        print(f"HTTP Error {e.code} for page {page_num}: {e}")
        return None
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None


def parse_location(location_data):
    """
    Parse a location object from the API into a clean format

    Args:
        location_data: Raw location data from API

    Returns:
        Dictionary with cleaned location data
    """
    location = {
        'nid': location_data.get('nid'),
        'title': location_data.get('title'),
        'type': location_data.get('type'),
        'url': location_data.get('url'),
    }

    # Parse address
    field_address = location_data.get('field_address', {})
    if field_address:
        location['address_line1'] = field_address.get('thoroughfare', '')
        location['locality'] = field_address.get('locality', '')
        location['administrative_area'] = field_address.get('administrative_area', '')
        location['postal_code'] = field_address.get('postal_code', '')
        location['country'] = field_address.get('country', 'US')

        # Create formatted address
        parts = [
            location['address_line1'],
            location['locality'],
            location['administrative_area'],
            location['postal_code']
        ]
        location['formatted_address'] = ', '.join(filter(None, parts))

    # Parse coordinates
    field_geofield = location_data.get('field_geofield', {})
    if field_geofield:
        geom = field_geofield.get('geom', '')
        if geom:
            # Extract coordinates from POINT string
            # Format: "POINT (-98.4016792789 30.2732254881)"
            try:
                coords = geom.replace('POINT (', '').replace(')', '').split()
                location['longitude'] = float(coords[0])
                location['latitude'] = float(coords[1])
            except:
                pass

        location['geo_type'] = field_geofield.get('geo_type', '')
        location['lat'] = field_geofield.get('lat', '')
        location['lon'] = field_geofield.get('lon', '')

    # Parse amenities/services
    field_amenity = location_data.get('field_amenity', [])
    if field_amenity:
        amenity_ids = []
        for amenity in field_amenity:
            if isinstance(amenity, dict):
                amenity_ids.append(amenity.get('uri', '').split('/')[-1])
        location['amenity_ids'] = amenity_ids
        location['amenities'] = map_amenities(amenity_ids)

    # Parse services
    field_services = location_data.get('field_services', [])
    if field_services:
        service_ids = []
        for service in field_services:
            if isinstance(service, dict):
                service_ids.append(service.get('uri', '').split('/')[-1])
        location['service_ids'] = service_ids
        location['services'] = map_services(service_ids)

    # Parse hours
    field_hours = location_data.get('field_hours', [])
    if field_hours:
        location['hours'] = []
        for hour in field_hours:
            if isinstance(hour, dict):
                hour_info = {
                    'day': hour.get('day'),
                    'start': hour.get('starthours'),
                    'end': hour.get('endhours')
                }
                location['hours'].append(hour_info)

    location['hours_text'] = location_data.get('field_hours_text', '')

    # Other fields
    location['phone'] = location_data.get('field_phone', '')
    location['website'] = location_data.get('field_website', '')
    location['healthy_pantry'] = location_data.get('field_healthy_pantry', '')
    location['snap_benefits'] = location_data.get('field_help_applying_for_snap_ben', '')
    location['proximity'] = location_data.get('field_lat_long_proximity', '')
    location['language'] = location_data.get('langcode', 'en')

    return location


def scrape_all_locations():
    """
    Scrape all food assistance locations from CTFB API

    Note: The API returns all locations in a single request at page 2

    Returns:
        List of all location dictionaries
    """
    print("=" * 80)
    print("Central Texas Food Bank - Food Assistance Scraper (API)")
    print("=" * 80)
    print()

    print("Fetching all locations from API...")

    # The API returns all locations at page 2
    locations_data = fetch_locations_page(2)

    if not locations_data or not isinstance(locations_data, list):
        print("✗ Failed to fetch locations")
        return []

    print(f"✓ Received {len(locations_data)} locations from API")
    print("\nParsing location data...")

    all_locations = []
    for i, loc_data in enumerate(locations_data, 1):
        location = parse_location(loc_data)
        all_locations.append(location)

        if i % 50 == 0:
            print(f"  Processed {i}/{len(locations_data)} locations...")

    print(f"✓ Total locations processed: {len(all_locations)}")

    return all_locations


def save_locations(locations, filename='data/ctfb_locations.json'):
    """Save locations to JSON file"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'Central Texas Food Bank',
        'source_url': 'https://www.centraltexasfoodbank.org/food-assistance/get-food-now',
        'api_endpoint': 'https://www.centraltexasfoodbank.org/rest/node/location/{page}',
        'total_locations': len(locations),
        'locations': locations
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(locations)} locations to {filename}")


def main():
    """Main function"""
    locations = scrape_all_locations()

    if locations:
        save_locations(locations)

        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        # Show first 5 locations
        for i, loc in enumerate(locations[:5], 1):
            print(f"\n{i}. {loc.get('title', 'N/A')}")
            print(f"   Address: {loc.get('formatted_address', 'N/A')}")
            if loc.get('latitude') and loc.get('longitude'):
                print(f"   Coordinates: {loc.get('latitude')}, {loc.get('longitude')}")

            # Services display
            services = loc.get('services', [])
            if services and any(services):  # Check if list has non-empty values
                print(f"   Services: {', '.join(filter(None, services))}")
            else:
                print(f"   Services: No services listed")

            # Amenities display
            amenities = loc.get('amenities', [])
            if amenities and any(amenities):  # Check if list has non-empty values
                print(f"   Amenities: {', '.join(filter(None, amenities))}")

            if loc.get('hours_text'):
                print(f"   Hours: {loc.get('hours_text')}")
            if loc.get('phone'):
                print(f"   Phone: {loc.get('phone')}")
            if loc.get('url'):
                print(f"   URL: {loc.get('url')}")

        if len(locations) > 5:
            print(f"\n... and {len(locations) - 5} more locations")

        print(f"\n✓ Successfully scraped {len(locations)} food assistance locations!")
    else:
        print("\n✗ No locations found")


if __name__ == "__main__":
    main()
