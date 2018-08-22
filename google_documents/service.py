import os

from oauth2client.service_account import ServiceAccountCredentials

from googleapiclient import discovery


# Google account scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive'  # Google Drive full access
]


def get_service_account_credentials(google_service_account_file=None):
    google_service_account_file = google_service_account_file or os.environ.get("GOOGLE_DOCUMENT_SERVICE_JSON")

    assert google_service_account_file, "Google Documents Service account file not found. " \
                                        "You should specify it via google_service_account_file or " \
                                        "in $GOOGLE_DOCUMENT_SERVICE_JSON " \
                                        "environment variable."

    return ServiceAccountCredentials.from_json_keyfile_name(google_service_account_file, scopes=SCOPES)


def get_drive_service(google_service_account_file=None):
    credentials = get_service_account_credentials(google_service_account_file)

    return discovery.build('drive', 'v3', credentials=credentials, cache_discovery=False)


def get_sheet_service(google_service_account_file=None):
    credentials = get_service_account_credentials(google_service_account_file)

    return discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)
