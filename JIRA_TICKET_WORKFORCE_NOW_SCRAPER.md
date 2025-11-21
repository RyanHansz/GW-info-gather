# Jira Ticket: Replicate Goodwill Central Texas Job Scraper

## Summary
Replicate the Goodwill Central Texas job scraper using the existing ADP Workforce Now API implementation

## Description

This ticket covers replicating the Goodwill Central Texas job scraper in a new environment or for integration purposes. The scraper has been tested and confirmed working as of 2025-11-21, successfully fetching 107 jobs from Goodwill Central Texas.

### Background

The Goodwill Central Texas job scraper uses the ADP Workforce Now API to fetch job postings. The API-based approach offers:

- **10x faster** than DOM scraping (completes in 5-60 seconds vs 5-10 minutes)
- **More reliable** - No browser automation required
- **Rich data** - Includes salary ranges, direct URLs, full descriptions
- **Low maintenance** - Stable API endpoints

### Reference Implementation

**Implementation:** [scrapers/goodwill/scraper_api.py](https://github.com/RyanHansz/GW-info-gather/blob/6fe40acdb12f2507f95bf633323bcee63de16d3d/scrapers/goodwill/scraper_api.py)

**Documentation:** [scrapers/goodwill/README_API.md](https://github.com/RyanHansz/GW-info-gather/blob/6fe40acdb12f2507f95bf633323bcee63de16d3d/scrapers/goodwill/README_API.md)

**Career Page:** https://goodwillcentraltexas.org/jobs/

### Scope

**This ticket is ONLY for Goodwill Central Texas.** Other organizations using ADP Workforce Now are out of scope for this ticket and may be addressed in future work.

The focus is on replicating/deploying/integrating the existing Goodwill Central Texas scraper implementation.

---

## Technical Approach

### Understanding the Goodwill Central Texas Implementation

The scraper targets Goodwill Central Texas's career center hosted on ADP Workforce Now:

**Career Center URL:**
```
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
```

**Key Parameters:**
- **cid** (Company ID): `cf5674db-9e68-440d-9919-4e047e6a1415`
- **ccId** (Career Center ID): `19000101_000001`
- **lang**: `en_US`
- **locale**: `en_US`

### API Endpoints

The scraper uses two main ADP Workforce Now API endpoints:

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

### Verifying API Access

Test API access for Goodwill Central Texas:

```bash
# Test job list endpoint
curl -s "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&locale=en_US&\$skip=0&\$top=20"

# Test job details endpoint (example with jobId 569676)
curl -s "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/3835?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&locale=en_US"
```

### Job URL Construction

Goodwill Central Texas job URLs use the **ExternalJobID** (not clientRequisitionID):

```
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html
  ?cid=cf5674db-9e68-440d-9919-4e047e6a1415
  &ccId=19000101_000001
  &lang=en_US
  &selectedMenuKey=CareerCenter
  &jobId={ExternalJobID}
```

**Example:** https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter&jobId=569676

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
  "source": "Goodwill Central Texas (ADP Workforce Now API)",
  "total_jobs": 107,
  "jobs": [
    {
      "title": "Merchandise Processor",
      "item_id": "9201783161055_1",
      "client_requisition_id": "3835",
      "posted_date": "2025-11-17T12:53:00.000-05:00",
      "location": "South Park Meadows Store, Austin, TX, US",
      "city": "Austin",
      "state": "TX",
      "postal_code": "78748",
      "job_type": "Full Time",
      "salary": "$0.00 - $14.00",
      "salary_currency": "USD",
      "external_job_id": "569676",
      "url": "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter&jobId=569676",
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

Goodwill Central Texas configuration (already implemented in `scraper_api.py`):

```python
# Company-specific configuration
COMPANY_NAME = "Goodwill Central Texas"
COMPANY_ID = "cf5674db-9e68-440d-9919-4e047e6a1415"
CAREER_CENTER_ID = "19000101_000001"
LANGUAGE = "en_US"
LOCALE = "en_US"

# API Configuration
BASE_URL = "https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1"
JOBS_LIST_ENDPOINT = f"{BASE_URL}/job-requisitions"
JOB_DETAILS_ENDPOINT = f"{BASE_URL}/job-requisitions/{{id}}"

# Rate Limiting
REQUEST_DELAY = 0.3  # seconds between requests (0.5s for detail fetching)
REQUEST_TIMEOUT = 15  # seconds for list API, 10s for details API

# Pagination
PAGE_SIZE = 20  # ADP Workforce Now standard page size
```

---

## Edge Cases Handled by Current Implementation

The Goodwill Central Texas scraper already handles these edge cases:

1. **Missing Salary Data**: Some jobs (especially ESL Teacher positions) don't have salary ranges - handled gracefully
2. **Multiple Locations**: Jobs typically have one location, but code handles multiple requisitionLocations array
3. **Missing ExternalJobID**: Falls back to clientRequisitionID if ExternalJobID not found in customFieldGroup
4. **Rate Limiting**: Built-in 0.3-0.5s delays between requests prevent API throttling
5. **Partial Failures**: If individual job detail fetch fails, scraper continues with remaining jobs
6. **Empty Results**: Handles case where API returns 0 jobs (though Goodwill typically has 90-110 open positions)
7. **HTML in Descriptions**: Job descriptions contain HTML - preserved as-is for downstream processing
8. **Date Formats**: ISO 8601 dates with timezone offsets (e.g., "2025-11-17T12:53:00.000-05:00") are preserved
9. **Salary Ranges**: Some positions show "$0.00 - $14.00" format - both equal and range salaries are handled
10. **Network Timeouts**: 15s timeout for list API, 10s for details API with proper error handling

---

## Success Criteria

- [ ] Scraper successfully fetches all jobs from Goodwill Central Texas (currently ~107 jobs)
- [ ] All required data fields are populated correctly
- [ ] Job URLs are valid and link to correct job postings on workforcenow.adp.com
- [ ] Scraper completes in reasonable time:
  - Fast mode (--no-details): < 10 seconds
  - Full mode: < 2 minutes
- [ ] Error handling prevents crashes on API failures
- [ ] Code follows existing project structure and conventions
- [ ] Documentation is clear and complete
- [ ] Tests achieve >80% code coverage (if test suite is implemented)

---

## Deployment

1. Verify scraper is in `scrapers/goodwill/` directory
2. Ensure `scraper_api.py` is executable with correct permissions
3. Test both fast mode and full mode:
   ```bash
   python3 scrapers/goodwill/scraper_api.py --no-details
   python3 scrapers/goodwill/scraper_api.py
   ```
4. Verify output is saved to `data/jobs.json`
5. Configure scheduled runs (if applicable)
6. Set up monitoring/alerting for scraper failures

---

## References

- **Reference Implementation**: [scrapers/goodwill/scraper_api.py](https://github.com/RyanHansz/GW-info-gather/blob/6fe40acdb12f2507f95bf633323bcee63de16d3d/scrapers/goodwill/scraper_api.py) (312 lines)
- **Documentation**: [scrapers/goodwill/README_API.md](https://github.com/RyanHansz/GW-info-gather/blob/6fe40acdb12f2507f95bf633323bcee63de16d3d/scrapers/goodwill/README_API.md)
- **Repository**: https://github.com/RyanHansz/GW-info-gather
- **Test Command**: `python3 scrapers/goodwill/scraper_api.py --no-details`
- **API Documentation**: ADP Workforce Now OData-style API
- **Test Results**: Successfully scraped 107 jobs on 2025-11-21

---

## Notes

- The existing implementation at `scrapers/goodwill/scraper_api.py` is complete and working
- API endpoints are stable and rarely change (last tested 2025-11-21)
- No authentication required for public job listings
- The scraper respects API rate limits with built-in delays (0.3-0.5s between requests)
- Consider caching API responses during development/testing to reduce load
- Job count fluctuates as positions are posted/removed (currently ~107 jobs)

---

## Estimated Effort

Since the implementation already exists, replication effort depends on scope:

**For code review and documentation:**
- **Code Review**: 1-2 hours
- **Testing**: 1 hour
- **Documentation Updates**: 1 hour
- **Total**: 3-4 hours

**For creating a derivative or integration:**
- **Setup**: 1-2 hours
- **Adaptation**: 2-4 hours
- **Testing**: 2-3 hours
- **Documentation**: 1-2 hours
- **Total**: 6-11 hours

---

## Priority

**Medium** - Existing scraper is working; replication needed for [specify purpose: deployment, integration, backup, etc.]

---

## Labels

`scraper`, `goodwill-central-texas`, `adp-workforce-now`, `api-integration`, `jobs`, `replication`
