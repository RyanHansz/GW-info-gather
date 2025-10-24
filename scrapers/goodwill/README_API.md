# Goodwill Scraper - API Version

## Overview

The **API-based scraper** (`scraper_api.py`) is a faster, more reliable alternative to the DOM-based scraper. It fetches job data directly from the ADP Workforce Now API instead of navigating through the web interface.

## Key Advantages

✅ **10x Faster** - Completes in seconds instead of minutes
✅ **More Reliable** - No browser automation or element reference issues
✅ **Direct URLs** - Each job has a working direct link
✅ **Salary Information** - Extracts salary ranges directly from API
✅ **Complete Data** - All 92 jobs with full details
✅ **No Browser Required** - Pure HTTP requests (except for full descriptions)

## How It Works

The scraper discovered that the ADP portal uses an OData-style API:

```
https://workforcenow.adp.com/.../job-requisitions?$skip=0&$top=20
```

### Key Findings:

1. **Job List API** - Returns paginated job listings with basic info
2. **clientRequisitionID** - This is the `jobId` used in URLs
3. **Job Detail API** - `/job-requisitions/{clientRequisitionID}` returns full job description
4. **Salary Data** - Included in the `payGradeRange` field

## Usage

### Fast Mode (Basic Info + Salary)
```bash
python scrapers/goodwill/scraper_api.py --no-details
```
- ⚡ Completes in ~5 seconds
- Includes: title, location, salary, job type, URLs
- Perfect for quick updates

### Full Mode (With Descriptions)
```bash
python scrapers/goodwill/scraper_api.py
```
- Takes ~60 seconds (1 API call per job)
- Includes everything from fast mode PLUS:
- Full job descriptions
- Additional details from job posting

## Data Structure

```json
{
  "title": "Retail Assistant Manager",
  "item_id": "9201772120306_1",
  "client_requisition_id": "3750",
  "posted_date": "2025-10-22T14:23:00.000-04:00",
  "location": "Lamar Oaks Store, Austin, TX, US",
  "city": "Austin",
  "state": "TX",
  "postal_code": "78704",
  "job_type": "Full Time",
  "salary": "$42,000.00 - $47,999.00",
  "salary_currency": "USD",
  "url": "https://workforcenow.adp.com/...&jobId=3750",
  "description": "Full job description text..."
}
```

## Comparison with DOM Scraper

| Feature | API Scraper | DOM Scraper |
|---------|-------------|-------------|
| Speed (92 jobs) | ~5-60 seconds | 5-10 minutes |
| Reliability | ✅ Very high | ⚠️ Fragile (element references) |
| Salary Data | ✅ Yes | ❌ No |
| Direct URLs | ✅ Yes | ⚠️ Requires clicking |
| Job Descriptions | ✅ Yes (opt-in) | ⚠️ Difficult to extract |
| Dependencies | urllib (standard lib) | Playwright (browser) |

## Technical Details

### API Endpoints

**List Jobs (Paginated):**
```
GET /careercenter/public/events/staffing/v1/job-requisitions
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
  &locale=en_US
  &$skip=0
  &$top=20
```

**Get Job Details:**
```
GET /careercenter/public/events/staffing/v1/job-requisitions/{clientRequisitionID}
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
  &locale=en_US
```

### URL Construction

Job URLs are constructed using the `clientRequisitionID`:

```
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
  &selectedMenuKey=CareerCenter
  &jobId={clientRequisitionID}
```

## Maintenance

The API endpoints are stable and unlikely to change frequently. If they do:

1. Check browser DevTools Network tab when visiting the careers page
2. Look for requests to `/job-requisitions`
3. Update the base URL and parameters in `scraper_api.py`

## Recommendation

**Use the API scraper as the primary scraper.** It's faster, more reliable, and provides better data quality. The DOM scraper can serve as a backup if the API changes unexpectedly.
