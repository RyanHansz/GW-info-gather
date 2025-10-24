#!/usr/bin/env python3
"""
Austin Affordable Housing Scraper
Fetches affordable housing property data from ATX Affordable Housing Portal
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


def fetch_housing_properties():
    """
    Fetches affordable housing properties from the ATX portal API

    Returns:
        Dict containing API response with properties data
    """
    url = "https://portal.atxaffordablehousing.net/get_all_properties"

    print(f"Fetching data from {url}...")

    try:
        # Make request to API
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get('success'):
            properties = data.get('data', [])
            print(f"✓ Successfully fetched {len(properties)} properties")
            return properties
        else:
            print("✗ API returned success: false")
            return []

    except urllib.error.URLError as e:
        print(f"✗ Network error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []


def analyze_properties(properties):
    """
    Analyze and print summary statistics about the properties

    Args:
        properties: List of property dictionaries
    """
    if not properties:
        return

    print("\n" + "=" * 60)
    print("PROPERTY STATISTICS")
    print("=" * 60)

    # Total units
    total_units = sum(p.get('total_units', 0) for p in properties if p.get('total_units'))
    restricted_units = sum(p.get('total_income_restricted_units', 0) for p in properties if p.get('total_income_restricted_units'))

    print(f"Total properties: {len(properties)}")
    print(f"Total units across all properties: {total_units}")
    print(f"Total income-restricted units: {restricted_units}")

    # Council districts
    districts = {}
    for prop in properties:
        district = prop.get('council_district')
        if district:
            districts[district] = districts.get(district, 0) + 1

    if districts:
        print(f"\nProperties by Council District:")
        for district in sorted(districts.keys()):
            print(f"  District {district}: {districts[district]} properties")

    # Pet-friendly properties
    pet_friendly = sum(1 for p in properties if p.get('allows_pet') == 'Yes')
    print(f"\nPet-friendly properties: {pet_friendly} ({pet_friendly/len(properties)*100:.1f}%)")

    # Section 8
    section8 = sum(1 for p in properties if p.get('accepts_section_8') == 'Yes')
    print(f"Accepts Section 8: {section8} ({section8/len(properties)*100:.1f}%)")

    # Community types
    elderly = sum(1 for p in properties if p.get('community_elderly') == 'Yes')
    disabled = sum(1 for p in properties if p.get('community_disabled') == 'Yes')
    military = sum(1 for p in properties if p.get('community_military') == 'Yes')

    print(f"\nSpecialized Communities:")
    print(f"  Elderly: {elderly}")
    print(f"  Disabled: {disabled}")
    print(f"  Military: {military}")

    # Amenities
    has_pool = sum(1 for p in properties if p.get('has_pool') == 'Yes')
    has_playground = sum(1 for p in properties if p.get('has_playground') == 'Yes')
    has_parking = sum(1 for p in properties if p.get('has_off_street_parking') == 'Yes')

    print(f"\nAmenities:")
    print(f"  Pool: {has_pool} properties")
    print(f"  Playground: {has_playground} properties")
    print(f"  Off-street parking: {has_parking} properties")


def save_properties(properties, filename='data/housing_properties.json'):
    """
    Save properties to JSON file

    Args:
        properties: List of property dictionaries
        filename: Output file path
    """
    output = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'ATX Affordable Housing Portal',
        'url': 'https://portal.atxaffordablehousing.net/get_all_properties',
        'total_properties': len(properties),
        'properties': properties
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved {len(properties)} properties to {filename}")


def main():
    print("=" * 60)
    print("Austin Affordable Housing Scraper")
    print("=" * 60)
    print()

    # Fetch properties
    properties = fetch_housing_properties()

    if not properties:
        print("\n✗ No properties retrieved. Exiting.")
        return

    # Analyze data
    analyze_properties(properties)

    # Save to file
    save_properties(properties)

    # Show sample properties
    print("\n" + "=" * 60)
    print("SAMPLE PROPERTIES")
    print("=" * 60)

    for i, prop in enumerate(properties[:5], 1):
        print(f"\n{i}. {prop.get('property_name', 'N/A')}")
        print(f"   Address: {prop.get('address', 'N/A')}, {prop.get('city', 'N/A')} {prop.get('zipcode', 'N/A')}")
        print(f"   Total Units: {prop.get('total_units', 'N/A')}")
        print(f"   Income Restricted: {prop.get('total_income_restricted_units', 'N/A')}")
        print(f"   Council District: {prop.get('council_district', 'N/A')}")

        if prop.get('accepts_section_8') == 'Yes':
            print(f"   Accepts Section 8: Yes")
        if prop.get('allows_pet') == 'Yes':
            print(f"   Pet-friendly: Yes")

        # Show contact info if available
        if prop.get('contact_phone'):
            print(f"   Phone: {prop.get('contact_phone')}")
        if prop.get('website'):
            print(f"   Website: {prop.get('website')}")

    if len(properties) > 5:
        print(f"\n... and {len(properties) - 5} more properties")

    print("\n" + "=" * 60)
    print("✓ Scraping complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
