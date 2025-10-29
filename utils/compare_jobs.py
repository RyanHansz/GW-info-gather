#!/usr/bin/env python3
"""
Compare two job scrapes and identify new postings
"""
import json
import sys
from datetime import datetime

def load_jobs(filepath):
    """Load jobs from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def compare_jobs(old_file, new_file):
    """Compare two job files and find new postings"""
    old_data = load_jobs(old_file)
    new_data = load_jobs(new_file)

    # Extract job IDs from old data
    old_job_ids = set()
    for job in old_data['jobs']:
        old_job_ids.add(job['client_requisition_id'])

    # Find new jobs
    new_jobs = []
    for job in new_data['jobs']:
        if job['client_requisition_id'] not in old_job_ids:
            new_jobs.append(job)

    # Sort by posted date (newest first)
    new_jobs.sort(key=lambda x: x.get('posted_date', ''), reverse=True)

    return {
        'old_scrape_time': old_data['scraped_at'],
        'new_scrape_time': new_data['scraped_at'],
        'old_job_count': old_data['total_jobs'],
        'new_job_count': new_data['total_jobs'],
        'new_postings': new_jobs,
        'new_postings_count': len(new_jobs)
    }

if __name__ == '__main__':
    # Use hardcoded paths for this comparison
    old_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/jobs_old.json'
    new_file = sys.argv[2] if len(sys.argv) > 2 else 'data/jobs.json'

    result = compare_jobs(old_file, new_file)

    print("=" * 80)
    print("JOB COMPARISON REPORT")
    print("=" * 80)
    print(f"Old scrape: {result['old_scrape_time']} ({result['old_job_count']} jobs)")
    print(f"New scrape: {result['new_scrape_time']} ({result['new_job_count']} jobs)")
    print(f"\nNEW POSTINGS: {result['new_postings_count']}")
    print("=" * 80)

    if result['new_postings']:
        for i, job in enumerate(result['new_postings'], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Posted: {job.get('posted_date', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            if job.get('city'):
                print(f"   City: {job['city']}, {job.get('state', '')}")
            print(f"   Type: {job.get('job_type', 'N/A')}")
            if job.get('salary'):
                print(f"   Salary: {job['salary']}")
            print(f"   Job ID: {job.get('client_requisition_id', 'N/A')}")
            if job.get('url'):
                print(f"   URL: {job['url']}")
    else:
        print("\nNo new postings found.")
