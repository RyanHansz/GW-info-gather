# GW Info Gather

A collection of Python scrapers and reference data for workforce development in the Austin, TX area. Includes job postings, affordable housing data, community resources, and a comprehensive Texas professional credentials guide.

## Quick Links

- **Goodwill Scraper**: [scrapers/goodwill/scraper_api.py](https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/goodwill/scraper_api.py)
- **Scraper Documentation**: [scrapers/goodwill/README.md](https://github.com/RyanHansz/GW-info-gather/blob/main/scrapers/goodwill/README.md)
- **File Guide**: [docs/FILE_GUIDE.md](https://github.com/RyanHansz/GW-info-gather/blob/main/docs/FILE_GUIDE.md)
- **Jira Ticket (Replication)**: [JIRA_TICKET_WORKFORCE_NOW_SCRAPER.md](https://github.com/RyanHansz/GW-info-gather/blob/main/JIRA_TICKET_WORKFORCE_NOW_SCRAPER.md)

## Current Status

The **API-based scraper** successfully extracts **all ~107 jobs** with complete information:
- Job title, location (with city, state, ZIP)
- Job type (Full Time/Part Time/Temporary) and salary range
- Posting date and direct URLs
- **Full HTML job descriptions** (3,000-4,000+ characters each)
- All data extracted via pure HTTP requests (no browser needed!)

The scraper uses the ADP Workforce Now API to fetch job data directly, making it 10x faster and more reliable than DOM scraping.

## Setup

The API scraper uses only Python standard library (`urllib` and `json`), so no additional dependencies are required for the Goodwill scraper.

For other scrapers in this repository:
```bash
pip install -r requirements.txt
playwright install chromium  # Only needed for DOM-based scrapers
```

## Project Structure

```
GW-info-gather/
├── scrapers/           # All web scraper scripts
│   ├── goodwill/       # Goodwill Central Texas scrapers
│   ├── indeed/         # Indeed job board scraper
│   ├── gsg/            # GSG Talent Solutions scraper
│   ├── housing/        # Affordable housing data scraper
│   └── resources/      # Community resources scraper
├── data/               # Generated data files (JSON)
├── debug/              # Debug HTML dumps
├── utils/              # Utility scripts
└── docs/               # Documentation
```

See [docs/FILE_GUIDE.md](docs/FILE_GUIDE.md) for detailed explanation of each file.

## Usage

Run the Goodwill scraper:
```bash
python scrapers/goodwill/scraper_api.py              # Full mode with descriptions (~60 seconds)
python scrapers/goodwill/scraper_api.py --no-details # Fast mode without descriptions (~5 seconds)
```

Run other scrapers:
```bash
python scrapers/indeed/scraper_indeed.py                # Indeed jobs
python scrapers/gsg/scraper_gsg.py                      # GSG Talent Solutions
python scrapers/resources/scraper_acc_resources.py      # ACC resources
python scrapers/housing/scraper_atx_housing.py          # Austin housing (571 properties)
```

The Goodwill scraper uses direct API calls (no browser required). Other scrapers may use browser automation.

## Output

All scraped data is saved in the `data/` directory:

### Scraped Data (JSON)
- `data/jobs.json` - Goodwill Central Texas jobs (~107 current postings with full descriptions)
- `data/indeed_jobs.json` - Indeed job postings (3 listings from company page)
- `data/gsg_jobs.json` - GSG Talent Solutions jobs (15 current postings)
- `data/acc_resources.json` - ACC community resources (371 resources)
- `data/housing_properties.json` - Austin affordable housing properties (571 properties)

Each JSON file contains:
- `scraped_at`: Timestamp of when data was collected
- `total_jobs` or `total_resources`: Number of items found
- `jobs` or `resources`: Array of data objects

**Note:** The Indeed scraper pulls jobs from the Goodwill Central Texas company page and can extract detailed information when job URLs are available. The scraper includes deduplication to ensure unique listings.

### Reference Data (CSV)
- `data/texas_creds_final.csv` - Texas Professional Credentials & Certifications Guide

**77 credentials across 12 categories** including:
- Healthcare & Allied Health (17 credentials): CNA, LVN, RN, EMT, Phlebotomy, Medical Assistant, etc.
- Skilled Trades, Construction & Manufacturing (11 credentials): CDL, Electrician, HVAC/R, Plumber, Welding, OSHA, etc.
- Trades & Service Industries (14 credentials): Cosmetology, Barbering, Esthetician, Massage Therapy, etc.
- Real Estate, Insurance & Financial Services (7 credentials): Real Estate Agent/Broker, Insurance Agent, MLO, CPA, etc.
- Business, Technology & Office (6 credentials): Microsoft Office Specialist, CompTIA, PMP, QuickBooks, etc.
- And 7 more categories

Each credential entry includes:
- Credential name and issuing agency
- Official government/certification body links
- Whether Goodwill Central Texas offers training
- Requirements and pathways
- Austin-area training providers with links

## Features

- **API-based scraping** - No browser automation required
- **Complete data extraction** - Titles, locations, salaries, URLs, and full HTML descriptions
- **Fast & reliable** - 10x faster than DOM scraping (~5-60 seconds for all jobs)
- **Pagination handling** - Automatically fetches all available jobs
- **Rate limiting** - Respects API with appropriate delays between requests
- **Two modes** - Fast mode (no descriptions) or full mode (with descriptions)
- **Error handling** - Graceful handling of network issues and missing data
- **Structured output** - Clean JSON format with timestamps

## Data Structures

### Goodwill Central Texas Jobs (`data/jobs.json`)

Complete job listing from ADP Workforce Now API:

```json
{
  "title": "Merchandise Processor",
  "item_id": "9201784679752_1",
  "client_requisition_id": "3852",
  "posted_date": "2025-11-20T13:40:00.000-05:00",
  "location": "Pflugerville Store, Pflugerville, TX, US",
  "city": "Pflugerville",
  "state": "TX",
  "postal_code": "78660",
  "job_type": "Full Time",
  "salary": "$0.00 - $14.00",
  "salary_currency": "USD",
  "url": "https://workforcenow.adp.com/...&jobId=569954",
  "external_job_id": "569954",
  "description": "<div><p>Merchandise Processor – Start Strong...</p></div>"
}
```

### Indeed Jobs (`data/indeed_jobs.json`)

Detailed job listings from Indeed with salary and full descriptions:

```json
{
  "title": "Retail Assistant Manager",
  "company": "Goodwill Industries of Central Texas",
  "location": "Cedar Park, TX",
  "salary": "$42,000 - $47,999 a year",
  "employment_type": "Full-time",
  "job_key": "1db5c23c9b0ed3dc",
  "url": "https://www.indeed.com/viewjob?jk=1db5c23c9b0ed3dc",
  "description": "Assistant Store Manager – Lead With Purpose...",
  "benefits": "Benefits\nPaid parental leave\nHealth insurance...",
  "qualifications": "High School diploma or equivalent..."
}
```

### GSG Talent Solutions Jobs (`data/gsg_jobs.json`)

Contract and permanent positions with pay rates:

```json
{
  "title": "Risk Management Specialist IV, Expert",
  "location": "Austin, TX",
  "employment_type": "Contract",
  "job_number": "51440554",
  "category": "",
  "posted_date": "10/23/25",
  "url": "https://jobs.gsgtalentsolutions.com/?p=job%2F12850314",
  "pay_rate": "$58.62 / hour"
}
```

### ACC Community Resources (`data/acc_resources.json`)

Community support resources from Austin Community College:

```json
{
  "type": "Legal",
  "name": "ACC's Notary Service",
  "description": "Free on-campus notary services for students needing help with ACC-specific documents...",
  "website": "https://docs.google.com/spreadsheets/...",
  "website_text": "Visit Website",
  "phone": "",
  "county": "Bastrop, Blanco, Burnet, Caldwell, Hays, Lee, Williamson, Travis"
}
```

### Austin Affordable Housing (`data/housing_properties.json`)

Comprehensive property data from ATX Affordable Housing Portal:

```json
{
  "id": 2854,
  "property_name": "Green Doors",
  "address": "1503 S IH35",
  "city": "Austin",
  "state": "TX",
  "zipcode": "78741",
  "lat": 30.24270058,
  "longitude": -97.73490143,
  "unit_type": "Single Family",
  "council_district": 9,
  "phone": "512-469-9130",
  "total_units": 60,
  "total_income_restricted_units": 60,
  "accepts_section_8": null,
  "num_units_mfi_30": 60,
  "num_units_mfi_50": null,
  "num_units_mfi_60": null,
  "community_military": 1,
  "community_served_descriptions": "Scattered housing for veterans experiencing poverty"
}
```
