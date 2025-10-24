# File Structure Guide

This document explains the purpose of each file and directory in the project.

## Directory Structure

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
├── docs/               # Documentation
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
└── README.md           # Main project documentation
```

## Scraper Files

### Goodwill Central Texas Scrapers (`scrapers/goodwill/`)

#### `scraper.py`
**Purpose:** Main production scraper for Goodwill Central Texas jobs
**Features:**
- Scrapes from ADP Workforce Now recruitment portal
- Extracts full job details including descriptions
- Handles infinite scroll pagination
- Navigates to individual job pages to capture job IDs and URLs
- Saves complete job data with metadata

**Output:** `data/jobs.json`
**Usage:** `python scrapers/goodwill/scraper.py`

#### `scraper_simple.py`
**Purpose:** Simplified version that only extracts basic job information
**Features:**
- Faster execution time
- No navigation to individual job pages
- Extracts: title, location, job type, posted date
- Best for quick job listing snapshots

**Output:** `data/jobs.json`
**Usage:** `python scrapers/goodwill/scraper_simple.py`

#### `scraper_js_approach.py`
**Purpose:** Experimental scraper using JavaScript extraction
**Features:**
- Research/debugging tool
- Attempts to extract job data via JavaScript evaluation
- Runs in non-headless mode for observation
- Useful for exploring page structure and data attributes

**Output:** Console output only
**Usage:** `python scrapers/goodwill/scraper_js_approach.py`

### Indeed Scraper (`scrapers/indeed/`)

#### `scraper_indeed.py`
**Purpose:** Scrapes Goodwill Central Texas job postings from Indeed.com
**Features:**
- Searches Indeed for Goodwill Central Texas jobs in Austin, TX area
- Handles multiple pages of results
- Anti-detection measures (user agent spoofing, realistic browser settings)
- Extracts job title, company, location, salary, snippets, and URLs
- Duplicate detection across pages

**Output:** `data/indeed_jobs.json`
**Usage:** `python scrapers/indeed/scraper_indeed.py`

### GSG Talent Solutions Scraper (`scrapers/gsg/`)

#### `scraper_gsg.py`
**Purpose:** Scrapes job postings from GSG Talent Solutions career site
**Features:**
- API-based approach (intercepts network responses)
- More reliable than HTML parsing
- Extracts comprehensive job data from JSON API
- Includes pay rates, job numbers, categories
- Constructs direct job URLs from API data

**Output:** `data/gsg_jobs.json`
**Usage:** `python scrapers/gsg/scraper_gsg.py`

### ACC Resources Scraper (`scrapers/resources/`)

#### `scraper_acc_resources.py`
**Purpose:** Scrapes community support resources from Austin Community College
**Features:**
- Scrapes basic needs resources (food, housing, healthcare, etc.)
- Handles paginated tables with Footable plugin
- Extracts: resource type, name, description, website, phone, county
- Complete pagination traversal
- Groups resources by type in summary

**Output:** `data/acc_resources.json`
**Usage:** `python scrapers/resources/scraper_acc_resources.py`

### Austin Affordable Housing Scraper (`scrapers/housing/`)

#### `scraper_atx_housing.py`
**Purpose:** Fetches affordable housing property data from ATX Affordable Housing Portal
**Features:**
- API-based scraper (no browser automation required)
- Uses Python's built-in urllib for simple HTTP requests
- Fetches comprehensive property data including units, affordability levels, amenities
- Detailed statistics by council district
- Analyzes property features (Section 8, pet-friendly, specialized communities)
- Provides summary statistics on total units and income restrictions

**Output:** `data/housing_properties.json`
**Usage:** `python scrapers/housing/scraper_atx_housing.py`

**Data Includes:**
- Property name, address, and location details
- Total units and income-restricted units
- Affordability levels (30%, 40%, 50%, 60% MFI)
- Council district information
- Amenities (pool, playground, parking)
- Pet policies and Section 8 acceptance
- Contact information and websites
- Tenant criteria (criminal history, eviction history, etc.)

## Utility Scripts (`utils/`)

#### `check_data.py`
**Purpose:** Data validation and analysis tool
**Features:**
- Validates scraped job data completeness
- Checks for presence of descriptions and URLs
- Provides quick statistics on data quality
- Sample output for spot-checking

**Usage:** `python utils/check_data.py`
**Input:** Reads from `data/jobs.json`

#### `split_json.py`
**Purpose:** Splits large JSON files into smaller chunks
**Features:**
- Handles both array and object-based JSON structures
- Configurable number of output files
- Preserves metadata across split files
- Useful for processing large datasets
- Automatically detects common wrapper keys (data, results, properties, etc.)

**Usage:** Edit file to set input path and run: `python utils/split_json.py`

## Data Files (`data/`)

All JSON output files are stored here:

### Scraped Data (JSON)
- `jobs.json` - Goodwill Central Texas jobs (92 current postings)
- `indeed_jobs.json` - Indeed job postings (5 listings)
- `gsg_jobs.json` - GSG Talent Solutions jobs (15 current postings)
- `acc_resources.json` - ACC community resources (371 resources)
- `housing_properties.json` - Austin affordable housing properties (571 properties)

### Reference Data (CSV)
- `texas_creds_final.csv` - **Texas Professional Credentials & Certifications Guide**

**Purpose:** Comprehensive reference guide to professional credentials and certifications in Texas
**Content:** 77 credentials across 12 career categories
**Fields:**
- Group (career category)
- Credential name
- Issuing agency
- Official government/certification links
- GCTA (Goodwill Central Texas) training availability
- Requirements and key qualifications
- Austin-area training providers with direct links

**Categories Covered:**
1. Healthcare & Allied Health (17) - CNA, LVN, RN, EMT, Phlebotomy, Medical Assistant, etc.
2. Skilled Trades, Construction & Manufacturing (11) - CDL, Electrician, HVAC/R, Plumber, Welding, OSHA
3. Trades & Service Industries (14) - Cosmetology, Barbering, Esthetician, Massage Therapy
4. Real Estate, Insurance & Financial Services (7) - Real Estate Agent/Broker, Insurance, MLO, CPA
5. Business, Technology & Office (6) - Microsoft Office, CompTIA, PMP, QuickBooks
6. Hospitality, Food Service & Retail (3) - Food Manager, Food Handler, TABC
7. Transportation, Logistics & Warehousing (2) - CLT, CPIM
8. Childcare, Early Childhood & Education Support (3) - CDA, Educational Aide
9. Green & Emerging Fields (5) - Solar NABCEP, HERS Rater, Water/Wastewater Operator
10. Regulatory & Legal (4) - Notary, LPC, LMSW/LCSW
11. Foundational & Soft Skills (2) - GED/TxCHSE, ACT WorkKeys NCRC
12. Professional & Business (1) - Apartment Leasing Professional (CALP)

**Use Cases:**
- Career pathway planning
- Training program research
- Workforce development guidance
- Connecting job seekers to certification opportunities
- Identifying which credentials Goodwill Central Texas offers training for

**Note:** The JSON files in this directory contain live scraped data and are included in the repository. The `debug/` directory is git-ignored.

## Debug Files (`debug/`)

HTML snapshots saved during scraping for troubleshooting:

- `page_debug.html` - Goodwill page snapshot when errors occur
- `indeed_debug.html` - Indeed page snapshot for debugging selectors

**Note:** This directory is git-ignored as these are temporary debug artifacts.

## Configuration Files

#### `requirements.txt`
**Purpose:** Python package dependencies
**Contents:**
```
playwright
```

**Installation:** `pip install -r requirements.txt`
**Additional Setup:** `playwright install chromium`

#### `.gitignore`
**Purpose:** Specifies files/directories git should ignore
**Key exclusions:**
- Python cache files (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `env/`)
- Generated data (`data/`)
- Debug files (`debug/`)
- IDE files (`.vscode/`, `.idea/`)

## Documentation (`docs/`)

#### `FILE_GUIDE.md` (this file)
**Purpose:** Comprehensive guide to project file structure and purpose

## Common Patterns

### All Scrapers Follow This Pattern:
1. **Launch browser** - Uses Playwright for browser automation
2. **Navigate to target URL** - Handles dynamic content loading
3. **Extract data** - Uses CSS selectors to parse page elements
4. **Save to JSON** - Structured output with timestamps and metadata
5. **Print summary** - Console output showing scrape results

### Standard Output Format:
```json
{
  "scraped_at": "ISO timestamp",
  "source": "Data source name",
  "total_jobs": 123,
  "jobs": [...]
}
```

## Quick Reference

| Task | Command |
|------|---------|
| Scrape Goodwill jobs | `python scrapers/goodwill/scraper.py` |
| Scrape Indeed jobs | `python scrapers/indeed/scraper_indeed.py` |
| Scrape GSG jobs | `python scrapers/gsg/scraper_gsg.py` |
| Scrape ACC resources | `python scrapers/resources/scraper_acc_resources.py` |
| Scrape housing data | `python scrapers/housing/scraper_atx_housing.py` |
| Check data quality | `python utils/check_data.py` |
| Split large JSON | Edit `utils/split_json.py` then run |

## Technology Stack

- **Language:** Python 3
- **Browser Automation:** Playwright
- **Data Format:** JSON
- **Version Control:** Git/GitHub
