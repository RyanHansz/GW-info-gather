import json

data = json.load(open('jobs.json'))
jobs_with_desc = [j for j in data['jobs'] if 'description' in j]
jobs_with_url = [j for j in data['jobs'] if 'url' in j]

print(f'Total jobs: {len(data["jobs"])}')
print(f'Jobs with descriptions: {len(jobs_with_desc)}')
print(f'Jobs with URLs: {len(jobs_with_url)}')
print('\nSample check:')
for i in [0, 10, 30, 50, 89]:
    job = data['jobs'][i]
    print(f"{i+1}. {job.get('title')[:40]:40} - URL: {'url' in job:5} - Desc: {'description' in job:5}")
