# Google account scopes
import json
import os
import re

import googleapiclient
from google.oauth2 import service_account
from googleapiclient import discovery

from google_documents.entities.from_itemable import FromItemable

SCOPES = [
    'https://www.googleapis.com/auth/drive'  # Google Drive full access
]


class GoogleDriveDocumentManager:
    def __init__(self, file_cls: type(FromItemable)):
        self.file_cls = file_cls

    # By default file name is getting from `GOOGLE_DOCUMENT_SERVICE_JSON`
    # enviroment variable
    default_service_account_file = os.environ.get(
        "GOOGLE_DOCUMENT_SERVICE_JSON")

    # You can use custom file name, specifying it using(...) method
    custom_service_account_file = None

    resource_name = 'drive'
    version = 3

    @classmethod
    def get_api_service(cls, credentials, resource_name=None, version=None):
        return discovery.build(
            resource_name or cls.resource_name,
            f"v{version or cls.version}",
            credentials=credentials
        )

    @property
    def _api_service(self):
        return self.get_api_service(self._get_api_credentials())

    def using(self, service_account_file):
        if not os.path.isfile(service_account_file):
            raise ValueError(f"`{service_account_file}` is not a file")
        self.custom_service_account_file = service_account_file
        return self

    @classmethod
    def _get_credentials_from_service_account_file(
            cls, service_account_file):
        assert service_account_file, \
            "Google Documents Service account file not found. " \
            "You should specify it via google_service_account_file or " \
            "in $GOOGLE_DOCUMENT_SERVICE_JSON " \
            "environment variable."

        return service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)

    @classmethod
    def get_default_api_credentials(cls):
        return cls._get_credentials_from_service_account_file(
            cls.default_service_account_file
        )

    @property
    def _service_account_file(self):
        return self.custom_service_account_file or \
               self.default_service_account_file

    def _get_api_credentials(self):
        return self._get_credentials_from_service_account_file(
            self._service_account_file
        )

    @property
    def service_account_credentials(self):
        return json.loads(open(self._service_account_file).read())

    def _get_item(self, id):
        return self._api_service.files().get(
            fileId=id).execute()

    def get(self, id):
        try:
            item = self._get_item(id)

            file_obj = self.file_cls.from_item(item)
            file_obj.set_api_credentials(self._get_api_credentials())
            return file_obj
        except googleapiclient.errors.HttpError:
            return None

    @staticmethod
    def _get_filter_folder_query(folder):
        return f"'{folder.id}' in parents"

    def all(self):
        return self.filter()

    def filter(self, **kwargs):
        """
        Filters files according to passed parameters
        """
        special_query_getters = {
            "folder": self._get_filter_folder_query
        }

        # Add mime type to search exactly files of the respective type
        # (Search only documents when we're calling
        # GoogleDocument.objects.filter(...)
        if self.file_cls.mime_type:
            kwargs['mime_type'] = self.file_cls.mime_type

        # Getting format query
        params_queries = []
        for param, value in kwargs.items():
            # Replace pythonic parameters like 'some_cool_parameter'
            # To google parameter like 'someCoolParameter'
            param_camel_case = re.sub(
                '_[a-z]', lambda p: p.group(0)[-1].upper(), param)

            # Getting search query for every parameter
            if param in special_query_getters:
                params_queries.append(
                    special_query_getters[param](value)
                )
            elif type(value) == bool:
                params_queries.append(
                    f"{param_camel_case} = {value}"
                )
            else:
                params_queries.append(
                    f"{param_camel_case} contains '{value}'"
                )

        # Getting total query
        q = ' and '.join(params_queries)

        response = self._api_service.files().list(
            q=q,
            spaces='drive',
            fields='files(id, name, mimeType, parents)').execute()

        files_items = response.get('files', [])

        result = []
        for file_item in files_items:
            result.append(self.file_cls.from_item(file_item))
        return result


class GoogleDriveSpreadsheetManager(GoogleDriveDocumentManager):
    sheets_resource_name = 'sheets'
    sheets_api_version = 4

    @property
    def _sheets_api_service(self):
        return self.get_api_service(
            self._get_api_credentials(),
            resource_name=self.sheets_resource_name,
            version=self.sheets_api_version
        )

    def create(self, title):
        item = self._sheets_api_service.spreadsheets().create(
            body={"properties": {"title": title}}
        ).execute()

        return self.file_cls.from_item(item)
