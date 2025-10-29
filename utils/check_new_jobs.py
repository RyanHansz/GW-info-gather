#!/usr/bin/env python3
"""
Quick script to identify new jobs by comparing against known old job IDs
"""
import json

# Old job IDs from the October 24 scrape
old_job_ids = {
    "3758", "3756", "3754", "3717", "3753", "3751", "3750", "3749", "3748", "3744",
    "3742", "3741", "3740", "3735", "3739", "3738", "3737", "3736", "3734", "3733",
    "3731", "3728", "3727", "3726", "3724", "3723", "3721", "3720", "3714", "3708",
    "3719", "3716", "3715", "3713", "3710", "3711", "3709", "3702", "3701", "3700",
    "3699", "3698", "3695", "3693", "3691", "3686", "3683", "3653", "3680", "3678",
    "3673", "3659", "3657", "3656", "3651", "3652", "3648", "3647", "3640", "3635",
    "3634", "3629", "3628", "3625", "3622", "3612", "3601", "3594", "3586", "3584",
    "3576", "3565", "3528", "3539", "3529", "3531", "3526", "3476", "3461", "3395",
    "3388", "3381", "3377", "3357", "3353", "3344", "3343", "3271", "3161", "3160",
    "3159", "3153"
}

# Load current jobs
with open('data/jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new_jobs = []
for job in data['jobs']:
    if job['client_requisition_id'] not in old_job_ids:
        new_jobs.append(job)

# Sort by posted date (newest first)
new_jobs.sort(key=lambda x: x.get('posted_date', ''), reverse=True)

print("=" * 80)
print(f"NEW POSTINGS SINCE OCTOBER 24: {len(new_jobs)}")
print("=" * 80)

if new_jobs:
    for i, job in enumerate(new_jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Posted: {job.get('posted_date', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        if job.get('city'):
            print(f"   City: {job['city']}, {job.get('state', '')}")
        print(f"   Type: {job.get('job_type', 'N/A')}")
        if job.get('salary'):
            print(f"   Salary: {job['salary']}")
        print(f"   Req ID: {job.get('client_requisition_id', 'N/A')}")
        if job.get('url'):
            print(f"   URL: {job['url']}")
else:
    print("\nNo new postings found.")
