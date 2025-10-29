# Central Texas Food Bank Scraper

Scrapes food assistance location data from the CTFB website.

## Website
https://www.centraltexasfoodbank.org/food-assistance/get-food-now

## Status
✅ **COMPLETE** - Working scraper implemented and tested with 421 locations.

## What We Know

The CTFB "Get Food Now" page uses an interactive map/location finder that:
- Shows food pantries, hot meal sites, and locations offering kid meals
- Allows filtering by service type (Groceries, Hot Meal, Kid Meals)
- Displays distance from current location
- Provides directions to each location

## Data Structure (Expected)

Each location should include:
- **Name**: Location/organization name
- **Address**: Street address, city, state, zip
- **Services**: Types of assistance (Groceries, Hot Meals, Kid Meals, Mobile)
- **Distance**: Distance from search location
- **Hours**: Operating hours (if available)
- **Contact**: Phone number (if available)

## Scraper Versions

### ✅ `scraper_ctfb_api.py` (WORKING - RECOMMENDED)
Production scraper using the REST API endpoint.

**API Endpoint:** `https://www.centraltexasfoodbank.org/rest/node/location/2`

**Usage:**
```bash
python3 scrapers/ctfb/scraper_ctfb_api.py
```

**Output:** `data/ctfb_locations.json` (421 locations)

**Data Quality:**
- 100% with address and coordinates
- 75% with phone numbers
- 65% with operating hours
- 39% with websites

### `scraper_ctfb.py` (Investigation Script)
Initial investigation script - not needed for production use.

### `scraper_ctfb_selenium.py` (Browser Automation)
Alternative approach using Selenium - slower but more robust if API changes.

## Manual Investigation Steps

If you need to find the data source manually:

1. **Open the page in Chrome:**
   ```
   https://www.centraltexasfoodbank.org/food-assistance/get-food-now
   ```

2. **Open Developer Tools** (F12 or Cmd+Option+I)

3. **Go to the Network tab**

4. **Clear the network log and refresh the page**

5. **Look for XHR/Fetch requests** that contain location data
   - Filter by "XHR" or "Fetch"
   - Look for requests with keywords like:
     - `location`, `pantry`, `food`, `site`, `agency`
     - JSON responses with arrays of locations
     - Geographic coordinates (lat/lon)

6. **Check for third-party services:**
   - Feeding America API
   - Google Maps with custom markers
   - Mapbox with data layers
   - Custom Drupal endpoints

7. **Inspect the page source** for:
   - Embedded JSON in `<script>` tags
   - JavaScript variables with location data
   - Data attributes on HTML elements

## Possible Data Sources

Based on common food bank locator implementations:

1. **Feeding America Network**: Many food banks use Feeding America's locator
2. **Link2Feed**: Food bank management system with location finder
3. **Custom Drupal Module**: CTFB appears to use Drupal CMS
4. **Google Maps API**: With custom markers loaded from a database

## Next Steps

- [ ] Use browser DevTools to identify the exact API endpoint
- [ ] Document the request parameters needed
- [ ] Create a working scraper with the correct endpoint
- [ ] Set up regular scraping schedule
- [ ] Add data validation and cleaning

## Output Format

Target output structure:

```json
{
  "scraped_at": "2025-10-29T...",
  "source": "Central Texas Food Bank",
  "total_locations": 150,
  "locations": [
    {
      "name": "Example Pantry",
      "address": "123 Main St, Austin, TX 78701",
      "city": "Austin",
      "state": "TX",
      "zip": "78701",
      "latitude": 30.2672,
      "longitude": -97.7431,
      "services": ["Groceries", "Hot Meal"],
      "is_mobile": false,
      "distance_miles": 2.5,
      "phone": "(512) 555-0100",
      "hours": "Mon-Fri 9am-5pm"
    }
  ]
}
```

## Contributing

If you find the API endpoint or data source, please update this README and the scraper!
