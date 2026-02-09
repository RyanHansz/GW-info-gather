#!/usr/bin/env python3
"""Upload today's scraper reports to Google Drive."""

import json
import os
import glob
from datetime import datetime, timezone, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_drive_service():
    key_json = os.environ['GOOGLE_SERVICE_ACCOUNT_KEY']
    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)


def upload_file(service, filepath, folder_id, upload_name=None):
    filename = upload_name or os.path.basename(filepath)
    mime = 'text/markdown' if filepath.endswith('.md') else 'application/json'

    # Check if file already exists in folder (update instead of duplicate)
    results = service.files().list(
        q=f"name='{filename}' and '{folder_id}' in parents and trashed=false",
        fields='files(id)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    media = MediaFileUpload(filepath, mimetype=mime)

    if results.get('files'):
        file_id = results['files'][0]['id']
        service.files().update(
            fileId=file_id, media_body=media, supportsAllDrives=True
        ).execute()
        print(f"Updated {filename}")
    else:
        metadata = {'name': filename, 'parents': [folder_id]}
        service.files().create(
            body=metadata, media_body=media, supportsAllDrives=True
        ).execute()
        print(f"Uploaded {filename}")


def main():
    folder_id = os.environ['GOOGLE_DRIVE_FOLDER_ID']
    service = get_drive_service()

    est = timezone(timedelta(hours=-5))
    today = datetime.now(est).strftime('%m_%d_%y')

    # Upload JSON files with date prefix so they don't overwrite
    for filepath, label in [('data/jobs.json', f'{today}_jobs.json'),
                            ('data/cat_classes.json', f'{today}_cat_classes.json')]:
        if os.path.exists(filepath):
            upload_file(service, filepath, folder_id, upload_name=label)

    # Upload today's markdown reports
    for pattern in [f'data/{today}_Goodwill_Jobs.md', f'data/{today}_CAT_Classes.md']:
        matches = glob.glob(pattern)
        for filepath in matches:
            upload_file(service, filepath, folder_id)
        if not matches:
            print(f"Skipping {pattern} (not found)")


if __name__ == '__main__':
    main()
