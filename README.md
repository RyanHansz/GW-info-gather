# GW Info Gather

A collection of Python scrapers and reference data for workforce development in the Austin, TX area. Includes job postings, affordable housing data, community resources, and a comprehensive Texas professional credentials guide.

## Current Status

The scraper successfully extracts **all 90 jobs** with basic information:
- Job title
- Location (store name and city)
- Job type (Full Time/Part Time/Temporary)
- Posting date

## Known Limitation

Due to the dynamic nature of the ADP Workforce Now platform (single-page JavaScript application), extracting full job details and direct links requires clicking through each job individually, which causes element reference issues.

Each job has a unique URL in the format:
```
https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=cf5674db-9e68-440d-9919-4e047e6a1415&ccId=19000101_000001&lang=en_US&selectedMenuKey=CareerCenter&jobId=XXXXXX
```

Where `jobId` is dynamically generated when clicking a job listing.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
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

Run the main Goodwill scraper:
```bash
python scrapers/goodwill/scraper.py
```

Run other scrapers:
```bash
python scrapers/indeed/scraper_indeed.py                # Indeed jobs
python scrapers/gsg/scraper_gsg.py                      # GSG Talent Solutions
python scrapers/resources/scraper_acc_resources.py      # ACC resources
python scrapers/housing/scraper_atx_housing.py          # Austin housing (571 properties)
```

The scripts will:
- Launch a headless browser
- Navigate to the target careers page
- Extract job/resource information
- Save results to `data/` directory

## Output

All scraped data is saved in the `data/` directory:

### Scraped Data (JSON)
- `data/jobs.json` - Goodwill Central Texas jobs (92 current postings)
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

## Future Enhancements

To get full job descriptions and direct links, potential approaches:
1. Process jobs in smaller batches with page reloads between each
2. Use browser network interception to capture API calls
3. Extract requisition IDs and construct URLs programmatically
4. Run in non-headless mode with manual intervention checkpoints

## Features

- Handles dynamic JavaScript content loading
- Implements infinite scroll to load all 90 jobs
- Includes error handling and progress reporting
- Saves structured JSON data with timestamp

## Data Structures

### Goodwill Central Texas Jobs (`data/jobs.json`)

Basic job listing from ADP Workforce Now portal:

```json
{
  "title": "Merchandise Processor",
  "location": "San Marcos Store, San Marcos, TX, US",
  "posted_date": "2 days ago",
  "job_type": "Full Time",
  "job_id": "job_item_view_main_div_9201772224883_1"
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
