'''
Google drive API interface

Handles all the interactions with google drive
'''

import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

@dataclass
class File:
    "basic file properties"
    ID: str
    name: str
    mimeType: str


def getGdriveID() -> str:
    try:
        return os.getenv("EB_FOLDER_ID")

    except:
        raise KeyError


def getLocalPath() -> str:
    try:
        return os.getenv("EB_LOCAL_PATH")

    except:
        raise KeyError


def authorizeGdrive():
    "Authorizes the Gdrive API"
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def downloadFile(service, file_id: str, file_name: str, local_path: str):
    "Downloads a single file"
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()

    with open(local_path, 'wb') as f:
        f.write(fh.getbuffer())


def fetchFiles(local_path: str, folder_id: str, cur_items: list) -> list[File]:
    service = authorizeGdrive()

    # Check for local folder
    os.makedirs(local_path, exist_ok=True)

    # Query for all files in the specific folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query,
        pageSize=1000,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()


    drive_q_items = results.get('files', [])
    drive_items: list[File] = []
    for item in drive_q_items:
        drive_items.append(File(item['id'], item['name'], item['mimeType']))
    to_download = [item for item in drive_items if item not in cur_items]
    to_delete = [item for item in cur_items if item not in drive_items]


    if to_download:
        for item in to_download:
            file_id = item.ID
            file_name = item.name
            local_file_path = os.path.join(local_path, file_name)
            downloadFile(service, file_id, file_name, local_file_path)
    
    if to_delete:
        for item in to_delete:
            file_id = item.ID
            file_name = item.name
            local_file_path = os.path.join(local_path, file_name)
            if os.path.isfile(local_file_path): 
                os.remove(local_file_path)
    
    return drive_items
