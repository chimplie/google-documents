import warnings

from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials

from google_documents.entities.api_service_mixin import ApiServiceMixin
from google_documents.entities.from_itemable import FromItemable
from google_documents.entities.manager import GoogleDriveDocumentManager, GoogleDriveSpreadsheetManager
from google_documents.settings import MIME_TYPES


class GoogleDriveFile(FromItemable, ApiServiceMixin):
    id: str
    name: str

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.objects().get(*args, **kwargs)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id} - {self.name}>"

    @property
    def parents(self):
        # TODO lazy loading of the all files attributes

        response = self._api_service.files().get(
            fileId=self.id, fields='parents'
        ).execute()

        for parent in response["parents"]:
            yield GoogleDriveFolder(id=parent)

    @property
    def url(self):
        return f"https://docs.google.com/document/d/{self.id}"

    def __init__(self, id, name=None, mime_type=None, *args, **kwargs):
        super().__init__()

        self.id = id

        self.name = name
        self.mime_type = mime_type

    @classmethod
    def from_item(cls, item):
        """
        Constructs Google Document from the item, in which Google describe it
        """
        return cls(
            id=item["id"], name=item.get("name"), mime_type=item.get("mimeType")
        )

    def copy(self, file_name: str):
        """
        Makes copy of the file
        :param file_name: Destination file name
        :return: GoogleDriveDocument copy
        """
        file_item = self._api_service.files().copy(
            fileId=self.id, body={"name": file_name}
        ).execute()

        return self.from_item(file_item)

    def delete(self):
        """
        Delets file from the Google Drive
        """
        self._api_service.files().delete(
            fileId=self.id
        )

    def put_to_folder(self, folder):
        """
        Puts the file into folder
        """
        # Calling API
        return self._api_service.files().update(
            fileId=self.id,
            addParents=folder.id,
            fields='id, parents').execute()


class GoogleDriveFolder(GoogleDriveFile):
    def __contains__(self, item):
        return self in item.parents

    @property
    def url(self):
        return f"https://drive.google.com/drive/folders/{self.id}"

    @property
    def children(self):
        children_items = self._api_service.files().list(
          q=f"\"{self.id}\" in parents").execute()['files']

        for item in children_items:
            yield GoogleDriveFilesFactory.from_item(item)

    def __str__(self):
        return f"{self.name}"


class GoogleDriveDocument(GoogleDriveFile):
    def export(self, file_name, mime_type=MIME_TYPES['docx']):
        """
        Exports content of the file to format specified in the MimeType and writes it to the File
        """
        export_bytes = self._api_service.files().export(
            fileId=self.id, mimeType=mime_type
        ).execute()

        open(file_name, "wb+").write(export_bytes)

    def update(self, file_name, mime_type=MIME_TYPES['docx']):
        # Making media body for the request
        media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)

        self._api_service.files().update(
            fileId=self.id,
            media_body=media_body
        ).execute()


class GoogleDriveSpreadsheet(GoogleDriveDocument):
    @property
    def _sheet_api_service(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.objects().service_account_credentials)
        return GoogleDriveSpreadsheetManager(self.__class__).get_service_from_credentials(credentials)

    @classmethod
    def objects(cls):
        return GoogleDriveDocumentManager(cls)

    def read(self, range_name):
        """
        Returns data from the range in Google Spreadsheet
        :param range_name:
        :return:
        """
        response = self._sheet_api_service.spreadsheets().values().get(
            spreadsheetId=self.id, range=range_name).execute()
        values = response.get('values', [])

        return values

    def get_range(self, range_name):
        warnings.warn("`get_range()` has been renamed to `read()`", DeprecationWarning)
        return self.read(range_name)

    def clear(self, range_name):
        """
        Clears data on spreadsheet at the specified range
        :param range_name: Range to clear
        """
        return self._sheet_api_service.spreadsheets().values().clear(
            spreadsheetId=self.id, range=range_name, body={"range": range_name}).execute()

    def write(self, range_name, data, value_input_option="RAW"):
        """
        Write data into the Google Sheet
        :param range_name: Range to write
        :param data: Data to write
        :param value_input_option: How to recognize input data
        """
        return self._sheet_api_service.spreadsheets().values().update(
            spreadsheetId=self.id, range=range_name,
            body={"values": data}, valueInputOption=value_input_option).execute()


class GoogleDriveFilesFactory:
    file_classes = {
        MIME_TYPES['folder']: GoogleDriveFolder,
        MIME_TYPES['document']: GoogleDriveDocument,
        MIME_TYPES['spreadsheet']: GoogleDriveSpreadsheet
    }

    default_class = GoogleDriveFile

    @classmethod
    def get_file_class(cls, mime_type):
        return cls.file_classes.get(mime_type) or cls.default_class

    @classmethod
    def from_item(cls, item) -> GoogleDriveFile:
        """
        Returns the respective object of Google Drive file,
        depending on the item mime type
        :return:
        """
        return cls.get_file_class(item.get('mimeType')).from_item(item)
