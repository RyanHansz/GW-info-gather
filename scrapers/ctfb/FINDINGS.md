# Central Texas Food Bank - Scraper Investigation Results

## Summary

The CTFB "Get Food Now" page uses a **React application** with **Google Maps** to display food assistance locations dynamically. The data is NOT embedded in the HTML but loaded via JavaScript.

## Key Findings

### Page Structure
- **Framework**: React-based single-page application
- **Map Service**: Google Maps JavaScript API
- **Total Locations**: Approximately **260 locations** (26 pages × ~10 per page)
- **Dynamic Loading**: Location data loads via JavaScript after page render

### Location Types Found
Based on the HTML source, locations include:
- Food Pantries (e.g., "Lord's Community Storehouse", "Caritas of Mexia")
- Mobile Food Pantries (e.g., "Mexia, TX - Mobile Food Pantry")
- Churches with food programs (e.g., "Glad Tidings Food Pantry", "Mart Church of Christ")
- Community organizations (e.g., "Fishes and Loaves")

### Filter Options Available
- **Service Types**:
  - Food Pantry
  - Delivered Grocery
  - Help paying for food/food vouchers
  - Mobile
  - Senior Program

- **Amenity Filters**:
  - Groceries
  - Hot Meal
  - Kid Meals

- **Time Filters**:
  - Open Now
  - Show All

### Technical Details
- **React Root**: `<div id="map">` and `<div id="map--inputbox">`
- **Sidebar Element**: `<ul class="sidebar--list"></ul>` (populated dynamically)
- **Pagination**: Shows "Page 1 of 26" with PREV/NEXT controls
- **Google Maps API Key**: Uses key `AIzaSyCo9gWqZ3SvNQlhBKGCkdR61mk3wi41I1w`

## What's Needed

To scrape this data successfully, we need to find the **API endpoint** that the React app calls to fetch location data.

### Method 1: Browser DevTools (RECOMMENDED)

1. **Open the page** in Chrome:
   ```
   https://www.centraltexasfoodbank.org/food-assistance/get-food-now
   ```

2. **Open DevTools** (F12 or Cmd+Option+I)

3. **Go to Network tab** → Filter by "Fetch/XHR"

4. **Refresh the page** and look for requests containing location data

5. **Look for**:
   - Endpoints with keywords: `location`, `food`, `pantry`, `site`, `map`, `markers`
   - JSON responses with arrays of locations
   - Geographic data (latitude/longitude coordinates)

6. **Common patterns to check**:
   - `/api/locations`
   - `/wp-json/` (if WordPress)
   - Google Maps data layer URLs
   - Third-party food bank locator services

### Method 2: Selenium with Network Interception

Use Selenium with Chrome DevTools Protocol to capture network requests:

```python
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Enable performance logging
caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}

driver = webdriver.Chrome(desired_capabilities=caps)
# ... capture network logs ...
```

### Method 3: Reverse Engineer JavaScript

1. Look at the page's JavaScript bundles
2. Search for API endpoint URLs in the minified code
3. Common variable names: `apiUrl`, `endpoint`, `baseUrl`

## Example Data Structure (Expected)

Based on the visible markers, each location should have:

```json
{
  "name": "Lord's Community Storehouse",
  "address": "123 Main St",
  "city": "Mexia",
  "state": "TX",
  "zip": "76667",
  "latitude": 31.6796,
  "longitude": -96.4828,
  "services": ["Food Pantry", "Groceries"],
  "is_mobile": false,
  "hours": "Mon-Fri 9am-5pm",
  "phone": "(254) 555-0100"
}
```

## Files Generated

1. **data/ctfb_page_screenshot.png** - Visual snapshot of the page
2. **data/ctfb_page_source.html** - Complete HTML source (176KB)
3. **scrapers/ctfb/scraper_ctfb.py** - Initial investigation script
4. **scrapers/ctfb/scraper_ctfb_selenium.py** - Browser automation approach
5. **scrapers/ctfb/debug_page.py** - Debug script used to capture page info

## Next Steps

### Immediate Actions

1. ✅ **Manual API Discovery** (5-10 minutes)
   - Use Chrome DevTools to find the API endpoint
   - Document the request format and parameters

2. **Create Working Scraper** (30 minutes)
   - Implement API calls with correct parameters
   - Handle pagination (26 pages)
   - Parse and clean the data

3. **Data Validation** (15 minutes)
   - Verify all locations are captured
   - Check for data quality issues
   - Format output consistently

### Long-term Considerations

- **Update Frequency**: How often do locations change?
- **Scheduling**: Set up automated scraping (daily/weekly?)
- **Data Storage**: Where should the data be saved?
- **Integration**: How will this data be used?

## Status

🔴 **BLOCKED** - Waiting for API endpoint discovery

Once the API endpoint is found, implementation should take less than 1 hour.

## Contact

If you find the API endpoint, please update this document and create a working scraper in `scraper_ctfb_api.py`.
