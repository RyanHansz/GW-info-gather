# Goodwill Central Texas Job Scraper

A Python script to scrape job postings from Goodwill Central Texas careers page.

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

## Usage

Run the scraper:
```bash
python scraper.py
```

The script will:
- Launch a headless browser
- Navigate to the Goodwill careers page
- Click "View all" to expand job listings
- Scroll to load all 90 jobs
- Extract job information
- Save results to `jobs.json`

## Output

`jobs.json` contains:
- `scraped_at`: Timestamp of when data was collected
- `total_jobs`: Number of jobs found
- `jobs`: Array of job objects with:
  - `title`: Job title
  - `location`: Store/office location
  - `job_type`: Employment type
  - `posted_date`: When the job was posted
  - `job_id`: Internal element ID

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
