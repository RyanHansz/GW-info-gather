# Goodwill Central Texas Job Scraper

**Source Code**: [scraper_api.py](https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/goodwill/scraper_api.py) | **Repository**: [GW-info-gather](https://github.com/RyanHansz/GW-info-gather)

## Overview

This scraper fetches job data directly from the ADP Workforce Now API used by Goodwill Central Texas. It extracts complete job information including titles, locations, salaries, and full HTML descriptions through direct HTTP requests—no browser automation required.

## Key Features

✅ **Fast** - Completes in 5-60 seconds depending on mode
✅ **Reliable** - Direct API access, no browser automation needed
✅ **Complete Data** - Fetches all ~107 jobs with full details (as of Nov 2025)
✅ **Direct URLs** - Every job includes a working public URL
✅ **Salary Information** - Extracts salary ranges when available
✅ **Full Descriptions** - 3,000-4,000+ character HTML job descriptions
✅ **No Dependencies** - Uses only Python standard library (`urllib`, `json`)

## How It Works

The scraper uses ADP Workforce Now's OData-style API endpoints:

### API Structure

1. **Job List API** - Paginated endpoint returns basic job information
   - Endpoint: `/job-requisitions?$skip=0&$top=20`
   - Returns: Job titles, locations, salary ranges, posting dates
   - Pagination: 20 jobs per request

2. **Job Detail API** - Individual job endpoint returns full descriptions
   - Endpoint: `/job-requisitions/{ExternalJobID}`
   - Returns: Complete job data including `requisitionDescription` field
   - Required: Must use `ExternalJobID` (not `clientRequisitionID`)

3. **Key Data Fields**
   - `ExternalJobID` - Public job ID used in URLs (found in `customFieldGroup.stringFields`)
   - `requisitionDescription` - Full HTML job description (3,000-4,000+ chars)
   - `payGradeRange` - Salary information (min/max rates)
   - `clientRequisitionID` - Internal ID (not used for public access)

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
GET /careercenter/public/events/staffing/v1/job-requisitions/{ExternalJobID}
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
  &locale=en_US
```

**Response includes:** `requisitionDescription` field with full HTML job description

**Important:** Use `ExternalJobID` (e.g., 570073), NOT `clientRequisitionID` (e.g., 3856)

### URL Construction

Job URLs are constructed using the `ExternalJobID` (found in `customFieldGroup.stringFields`):

```
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
  &selectedMenuKey=CareerCenter
  &jobId={ExternalJobID}
```

**Example:** `jobId=570073` (ExternalJobID), not `3856` (clientRequisitionID)

## Maintenance

The API endpoints are stable and unlikely to change frequently. If they do:

1. Open browser DevTools Network tab when visiting https://goodwillcentraltexas.org/jobs/
2. Look for requests to `/job-requisitions`
3. Check if parameters (cid, ccId) have changed
4. Update the base URL and parameters in `scraper_api.py` if needed

## Troubleshooting

**No descriptions being fetched?**
- Verify you're using `ExternalJobID` not `clientRequisitionID`
- Check the API response includes `requisitionDescription` field
- Ensure the detail API endpoint is being called with correct parameters

**Job URLs not working?**
- Confirm URLs use `ExternalJobID` from `customFieldGroup.stringFields`
- Verify `jobId` parameter matches the public-facing job ID
