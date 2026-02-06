#!/usr/bin/env python3
"""Upload today's scraper reports to Google Drive."""

import json
import os
import glob
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service():
    key_json = os.environ['GOOGLE_SERVICE_ACCOUNT_KEY']
    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)


def upload_file(service, filepath, folder_id):
    filename = os.path.basename(filepath)
    mime = 'text/markdown' if filepath.endswith('.md') else 'application/json'

    # Check if file already exists in folder (update instead of duplicate)
    results = service.files().list(
        q=f"name='{filename}' and '{folder_id}' in parents and trashed=false",
        fields='files(id)'
    ).execute()

    media = MediaFileUpload(filepath, mimetype=mime)

    if results.get('files'):
        file_id = results['files'][0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"Updated {filename}")
    else:
        metadata = {'name': filename, 'parents': [folder_id]}
        service.files().create(body=metadata, media_body=media).execute()
        print(f"Uploaded {filename}")


def main():
    folder_id = os.environ['GOOGLE_DRIVE_FOLDER_ID']
    service = get_drive_service()

    today = datetime.now().strftime('%m_%d_%y')

    # Upload today's markdown reports and the JSON files
    files_to_upload = [
        f'data/{today}_Goodwill_Jobs.md',
        f'data/{today}_CAT_Classes.md',
        'data/jobs.json',
        'data/cat_classes.json',
    ]

    for filepath in files_to_upload:
        if os.path.exists(filepath):
            upload_file(service, filepath, folder_id)
        else:
            print(f"Skipping {filepath} (not found)")


if __name__ == '__main__':
    main()
