import os

from google.oauth2 import service_account

from googleapiclient import discovery


# Google account scopes

SCOPES = [
    'https://www.googleapis.com/auth/drive'  # Google Drive full access
]

# Path to service.json file
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service.json')

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def get_drive_service():
    return discovery.build('drive', 'v3', credentials=credentials)


def get_sheet_service():
    return discovery.build('sheets', 'v4', credentials=credentials)
