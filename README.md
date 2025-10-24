# GW Info Gather

A collection of Python scrapers to gather job postings, affordable housing data, and community resources in the Austin, TX area.

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

- `data/jobs.json` - Goodwill Central Texas jobs
- `data/indeed_jobs.json` - Indeed job postings
- `data/gsg_jobs.json` - GSG Talent Solutions jobs
- `data/acc_resources.json` - ACC community resources
- `data/housing_properties.json` - Austin affordable housing properties

Each file contains:
- `scraped_at`: Timestamp of when data was collected
- `total_jobs` or `total_resources`: Number of items found
- `jobs` or `resources`: Array of data objects

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

## Data Structure

Example job entry:
```json
{
  "title": "Merchandise Processor",
  "location": "San Marcos Store, San Marcos, TX, US",
  "posted_date": "Today",
  "job_type": "Full Time",
  "job_id": "job_item_view_main_div_9201772224883_1"
}
```
