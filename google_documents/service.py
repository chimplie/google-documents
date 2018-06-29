import os

from google.oauth2 import service_account

from googleapiclient import discovery


# Google account scopes

SCOPES = [
    'https://www.googleapis.com/auth/drive'  # Google Drive full access
]

# Path to service.json file
assert os.environ.get("GOOGLE_DOCUMENT_SERVICE_JSON"), "Google Documents Service account file not found. " \
                                                   "You should specify it in $GOOGLE_DOCUMENT_SERVICE_JSON " \
                                                   "environment variable."
SERVICE_ACCOUNT_FILE = os.environ["GOOGLE_DOCUMENT_SERVICE_JSON"]

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def get_drive_service():
    return discovery.build('drive', 'v3', credentials=credentials, cache_discovery=False)


def get_sheet_service():
    return discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)
