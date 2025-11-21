# Jira Ticket: Replicate ADP Workforce Now Job Scraper

## Summary
Create a reusable job scraper for organizations using ADP Workforce Now career centers (similar to the Goodwill Central Texas implementation)

## Description

This ticket covers creating a new job scraper based on the successful Goodwill Central Texas scraper that uses the ADP Workforce Now platform. The scraper has been tested and confirmed working as of 2025-11-21, successfully fetching 107 jobs.

### Background

Many organizations use ADP Workforce Now for their career centers. This creates an opportunity to replicate the scraping approach for other organizations using the same platform. The API-based approach is:

- **10x faster** than DOM scraping (completes in 5-60 seconds vs 5-10 minutes)
- **More reliable** - No browser automation required
- **Rich data** - Includes salary ranges, direct URLs, full descriptions
- **Low maintenance** - Stable API endpoints

### Reference Implementation

Location: `scrapers/goodwill/scraper_api.py`
Documentation: `scrapers/goodwill/README_API.md`

---

## Technical Approach

### Step 1: Identify Target Organization

Find an organization using ADP Workforce Now. These can be identified by:

1. Career page URLs containing `workforcenow.adp.com`
2. Example URL pattern:
   ```
   https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid={COMPANY_ID}&ccId={CENTER_ID}
   ```

### Step 2: Extract Company Parameters

Open the target career center in a browser and extract these key parameters from the URL:

- **cid** (Company ID): e.g., `cf5674db-9e68-440d-9919-4e047e6a1415`
- **ccId** (Career Center ID): e.g., `19000101_000001`
- **lang**: Usually `en_US`
- **locale**: Usually `en_US`

### Step 3: Discover API Endpoints

The ADP Workforce Now platform uses two main API endpoints:

#### Job List API (Paginated)
```
GET https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions
```

**Query Parameters:**
- `cid`: Company ID from Step 2
- `ccId`: Career Center ID from Step 2
- `lang`: Language code
- `locale`: Locale code
- `$skip`: Pagination offset (0, 20, 40, etc.)
- `$top`: Results per page (typically 20)

**Response Structure:**
```json
{
  "jobRequisitions": [
    {
      "itemID": "...",
      "clientRequisitionID": "3750",
      "requisitionTitle": "Retail Assistant Manager",
      "postDate": "2025-10-22T14:23:00.000-04:00",
      "requisitionLocations": [...],
      "workLevelCode": {...},
      "payGradeRange": {...},
      "customFieldGroup": {
        "stringFields": [
          {
            "nameCode": {"codeValue": "ExternalJobID"},
            "stringValue": "3750"
          }
        ]
      }
    }
  ],
  "meta": {
    "totalNumber": 107
  }
}
```

#### Job Details API
```
GET https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/{clientRequisitionID}
```

**Query Parameters:**
- Same as Job List API (cid, ccId, lang, locale)
- Path parameter: `{clientRequisitionID}` from job list response

**Response Structure:**
```json
{
  "jobRequisition": {
    "jobDescription": "Full HTML job description...",
    ... (same fields as list API plus additional details)
  }
}
```

### Step 4: Verify API Access

Test API access using curl or Python:

```bash
# Test job list endpoint
curl -s "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid={YOUR_CID}&ccId={YOUR_CCID}&lang=en_US&locale=en_US&\$skip=0&\$top=20"

# Test job details endpoint (use clientRequisitionID from above)
curl -s "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/{JOB_ID}?cid={YOUR_CID}&ccId={YOUR_CCID}&lang=en_US&locale=en_US"
```

### Step 5: Construct Job URLs

Job URLs are constructed using the **ExternalJobID** (not clientRequisitionID!):

```
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html
  ?cid={COMPANY_ID}
  &ccId={CENTER_ID}
  &lang=en_US
  &selectedMenuKey=CareerCenter
  &jobId={ExternalJobID}
```

**Important:** The ExternalJobID is found in `customFieldGroup.stringFields` array, where `nameCode.codeValue == 'ExternalJobID'`.

---

## Implementation Requirements

### Core Functions to Implement

1. **`fetch_jobs_list(skip, top)`**
   - Fetches paginated job listings
   - Returns: `{'jobs': [...], 'total': N}`
   - Error handling for network issues
   - Recommended timeout: 15 seconds

2. **`fetch_job_details(client_req_id)`**
   - Fetches full job description
   - Returns: job detail dictionary
   - Error handling for missing/invalid IDs
   - Recommended timeout: 10 seconds

3. **`extract_external_job_id(job_data)`**
   - Extracts ExternalJobID from customFieldGroup
   - Used for constructing public job URLs
   - Returns: string or None

4. **`parse_job_data(job_data, include_details)`**
   - Parses raw API response into clean format
   - Handles location, salary, job type extraction
   - Optionally fetches full description
   - Returns: standardized job dictionary

5. **`scrape_jobs(fetch_details)`**
   - Main orchestration function
   - Handles pagination through all results
   - Respects API rate limits (0.3-0.5s delays)
   - Progress logging
   - Returns: list of all jobs

### Data Fields to Extract

**Required Fields:**
- `title`: Job title
- `item_id`: Internal item ID
- `client_requisition_id`: Client requisition ID
- `posted_date`: ISO 8601 date string
- `location`: Location name
- `city`: City name
- `state`: State code
- `postal_code`: ZIP code
- `job_type`: Full Time / Part Time
- `url`: Direct link to job posting
- `external_job_id`: External job ID for URL construction

**Optional Fields:**
- `salary`: Formatted salary range (e.g., "$42,000.00 - $47,999.00")
- `salary_currency`: Currency code (e.g., "USD")
- `description`: Full HTML job description (requires details API call)

### Output Format

```json
{
  "scraped_at": "2025-11-21T10:30:00",
  "source": "Organization Name (ADP Workforce Now API)",
  "total_jobs": 107,
  "jobs": [
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
      "external_job_id": "3750",
      "url": "https://workforcenow.adp.com/...",
      "description": "Full job description..."
    }
  ]
}
```

---

## Testing Checklist

### Unit Tests

- [ ] Test `fetch_jobs_list()` with valid parameters
- [ ] Test `fetch_jobs_list()` with invalid CID (should handle gracefully)
- [ ] Test `fetch_job_details()` with valid clientRequisitionID
- [ ] Test `fetch_job_details()` with invalid ID
- [ ] Test `extract_external_job_id()` with various job data formats
- [ ] Test `parse_job_data()` with complete data
- [ ] Test `parse_job_data()` with missing optional fields
- [ ] Test pagination logic (verify all jobs fetched)

### Integration Tests

- [ ] Run scraper in fast mode (`--no-details`)
- [ ] Verify total job count matches API meta.totalNumber
- [ ] Verify all jobs have required fields
- [ ] Run scraper in full mode (with descriptions)
- [ ] Verify descriptions are populated
- [ ] Test job URLs open to correct postings
- [ ] Verify salary data is correctly formatted
- [ ] Test error handling with network disconnected

### Performance Tests

- [ ] Fast mode completes in under 10 seconds for ~100 jobs
- [ ] Full mode completes in under 2 minutes for ~100 jobs
- [ ] No rate limiting errors from API
- [ ] Memory usage stays reasonable for large job sets

---

## Configuration

Create a configuration file or constants section:

```python
# Company-specific configuration
COMPANY_NAME = "Your Organization Name"
COMPANY_ID = "..."  # Extract from career center URL
CAREER_CENTER_ID = "..."  # Extract from career center URL
LANGUAGE = "en_US"
LOCALE = "en_US"

# API Configuration
BASE_URL = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1"
JOBS_LIST_ENDPOINT = f"{BASE_URL}/job-requisitions"
JOB_DETAILS_ENDPOINT = f"{BASE_URL}/job-requisitions/{{id}}"

# Rate Limiting
REQUEST_DELAY = 0.3  # seconds between requests
REQUEST_TIMEOUT = 15  # seconds

# Pagination
PAGE_SIZE = 20  # ADP Workforce Now standard page size
```

---

## Edge Cases to Handle

1. **Missing Salary Data**: Some jobs may not have salary information
2. **Multiple Locations**: Jobs may have multiple requisitionLocations
3. **Missing ExternalJobID**: Fallback to clientRequisitionID if ExternalJobID not found
4. **Rate Limiting**: Implement exponential backoff if API returns 429
5. **Partial Failures**: Continue scraping even if individual job details fail
6. **Empty Results**: Handle case where organization has zero open positions
7. **HTML in Descriptions**: Job descriptions may contain HTML tags
8. **Date Formats**: Posted dates may have different timezone formats

---

## Success Criteria

- [ ] Scraper successfully fetches all jobs from target organization
- [ ] All required data fields are populated
- [ ] Job URLs are valid and open to correct postings
- [ ] Scraper completes in reasonable time (< 2 minutes for 100 jobs)
- [ ] Error handling prevents crashes on API failures
- [ ] Code follows existing project structure and conventions
- [ ] Documentation includes setup and usage instructions
- [ ] Tests achieve >80% code coverage

---

## Deployment

1. Add new scraper to `scrapers/{organization_name}/` directory
2. Create README.md with organization-specific details
3. Update main project README with new scraper
4. Add scraper to CI/CD pipeline
5. Configure scheduled runs (if applicable)
6. Set up monitoring/alerting for scraper failures

---

## References

- **Reference Implementation**: `scrapers/goodwill/scraper_api.py` (lines 1-312)
- **Documentation**: `scrapers/goodwill/README_API.md`
- **Test Command**: `python3 scrapers/goodwill/scraper_api.py --no-details`
- **API Documentation**: ADP Workforce Now OData-style API
- **Test Results**: Successfully scraped 107 jobs on 2025-11-21

---

## Notes

- ADP Workforce Now is a widely-used platform - many organizations can use this approach
- API endpoints are stable and rarely change
- No authentication required for public job listings
- Consider caching API responses during development to reduce load
- Be respectful of API rate limits - add appropriate delays between requests

---

## Estimated Effort

- **Research/Setup**: 2-4 hours
- **Implementation**: 4-6 hours
- **Testing**: 2-3 hours
- **Documentation**: 1-2 hours
- **Total**: 9-15 hours

---

## Priority

**Medium** - This is a reusable pattern that can be applied to multiple organizations using ADP Workforce Now.

---

## Labels

`scraper`, `adp-workforce-now`, `api-integration`, `reusable-pattern`, `jobs`
