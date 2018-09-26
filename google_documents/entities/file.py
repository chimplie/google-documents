"""
Contains Google Drive file-like classes like file, document or Spreadsheet
"""
import os
import warnings

from googleapiclient.http import MediaFileUpload

from google_documents.entities.api_credentials_mixin import ApiCredentialsMixin
from google_documents.entities.from_itemable import FromItemable
from google_documents.entity_managers.file import GoogleDriveSpreadsheetManager
from google_documents.entity_managers.sheet import SheetsManager
from google_documents.settings import MIME_TYPES


class GoogleDriveFile(FromItemable, ApiCredentialsMixin):
    """
    Represents file at the Google Drive
    """
    id: str
    name: str
    mime_type = None

    @property
    def _api_service(self):
        return self.objects().get_api_service(
            credentials=self._api_credentials)

    @classmethod
    def get(cls, *args, **kwargs):
        """
        Returns file at the Google Drive by its properties like id or name
        """
        return cls.objects().get(*args, **kwargs)

    @classmethod
    def filter(cls, *args, **kwargs):
        """
        Searches file by some of theirs properties like id or name
        Returns list of files
        """
        return cls.objects().filter(*args, **kwargs)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id} - {self.name}>"

    @property
    def parents(self):
        """
        Returns folders that contains the file
        :return:
        """
        # TODO lazy loading of the all files attributes

        response = self._api_service.files().get(  # pylint: disable=no-member
            fileId=self.id, fields='parents'
        ).execute()

        for parent in response["parents"]:
            yield GoogleDriveFolder(id=parent)

    @property
    def url(self):
        """
        Returns url to the file
        """
        return f"https://docs.google.com/document/d/{self.id}"

    def __init__(self, id, name=None, mime_type=None, *args, **kwargs):
        super().__init__()

        self.id = id  # pylint: disable=invalid-name

        self.name = name
        self.mime_type = mime_type

    @classmethod
    def from_item(cls, item):
        """
        Constructs Google Document from the item, in which Google describe it
        """
        return cls(
            id=item["id"],
            name=item.get("name"),
            mime_type=item.get("mimeType")
        )

    def copy(self, file_name: str):
        """
        Makes copy of the file
        :param file_name: Destination file name
        :return: GoogleDriveDocument copy
        """
        file_item = self._api_service.files().copy(  # pylint: disable=no-member
            fileId=self.id, body={"name": file_name}
        ).execute()

        return self.from_item(file_item)

    def delete(self):
        """
        Delets file from the Google Drive
        """
        return self._api_service.files().delete(  # pylint: disable=no-member
            fileId=self.id
        ).execute()

    def put_to_folder(self, folder):
        """
        Puts the file into folder
        """
        # Calling API
        return self._api_service.files().update(  # pylint: disable=no-member
            fileId=self.id,
            addParents=folder.id,
            fields='id, parents').execute()


class GoogleDriveFolder(GoogleDriveFile):
    """
    Represents folder in the Google Drive
    """
    mime_type = MIME_TYPES['folder']

    def __contains__(self, item):
        return self in item.parents

    @property
    def url(self):
        return f"https://drive.google.com/drive/folders/{self.id}"

    @property
    def children(self):
        """
        Returns list of file inside the folder
        """
        children_items = self._api_service.files().list(  # pylint: disable=no-member
            q=f"\"{self.id}\" in parents").execute()['files']

        for item in children_items:
            yield GoogleDriveFilesFactory.from_item(item)

    def __str__(self):
        return f"{self.name}"


class GoogleDriveDocument(GoogleDriveFile):
    """
    Represents Google Document
    """
    mime_type = MIME_TYPES['document']

    def export(self, file_name, mime_type=MIME_TYPES['docx']):
        """
        Exports content of the file to format specified
        in the MimeType and writes it to the File
        """
        export_bytes = self._api_service.files().export(  # pylint: disable=no-member
            fileId=self.id, mimeType=mime_type
        ).execute()

        open(file_name, "wb+").write(export_bytes)

    def update(self, file_name, mime_type=MIME_TYPES['docx']):
        # Making media body for the request
        media_body = MediaFileUpload(file_name, mimetype=mime_type,
                                     resumable=True)

        self._api_service.files().update(  # pylint: disable=no-member
            fileId=self.id,
            media_body=media_body
        ).execute()


class GoogleDriveSpreadsheet(GoogleDriveDocument):
    mime_type = MIME_TYPES['spreadsheet']

    @classmethod
    def objects(cls):
        return GoogleDriveSpreadsheetManager(cls)

    @classmethod
    def from_item(cls, item):
        if 'id' in item:
            # Item from Google Drive API
            return super().from_item(item)

        # Item for Google Sheets API
        return cls(
            id=item["spreadsheetId"],
            name=item['properties'].get('title')
        )

    @property
    def _sheets_api_service(self):
        return self.objects()._sheets_api_service

    def read(self, range_name):
        """
        Returns data from the range in Google Spreadsheet
        :param range_name:
        :return:
        """
        response = self._sheets_api_service.spreadsheets().values().get(  # pylint: disable=no-member
            spreadsheetId=self.id, range=range_name).execute()
        values = response.get('values', [])

        return values

    def batch_read(self, ranges_names: [str]):
        """
        Reads multiple ranges from the spreadsheet
        :param ranges_names: List of ranges to get data from
        """
        response = self._sheets_api_service.spreadsheets().values().batchGet(  # pylint: disable=no-member
            spreadsheetId=self.id, ranges=ranges_names).execute()

        value_ranges = response.get('valueRanges', [])

        # Extract values from value_ranges
        values = []
        for value_range in value_ranges:
            values.append(value_range.get('values', []))
        return values

    def batch_write(self, value_ranges, value_input_option="RAW"):
        """
        Writes to the multiple ranges in the Google Sheet
        :param value_ranges: List of objects like
        {"range": "{sheet name}!{range name}":
        values: [[ 2 dimensional array]]}
        :param value_input_option: How to recognize input data
        """
        # TODO Support of the value
        body = {
            'valueInputOption': value_input_option,
            'data': value_ranges
        }

        return self._sheets_api_service.spreadsheets().values().batchUpdate(  # pylint: disable=no-member
            spreadsheetId=self.id,
            body=body).execute()

    def batch_clear(self, ranges_names: [str]):
        """
        Clears data in spreadsheet ranges
        :param ranges_names: Ranges to clear
        """
        return self._sheets_api_service.spreadsheets().values().batchClear(  # pylint: disable=no-member
            spreadsheetId=self.id,
            body={"ranges": ranges_names}).execute()

    def get_range(self, range_name):
        warnings.warn("`get_range()` has been renamed to `read()`",
                      DeprecationWarning)
        return self.read(range_name)

    def clear(self, range_name):
        """
        Clears data on spreadsheet at the specified range
        :param range_name: Range to clear
        """
        return self._sheets_api_service.spreadsheets().values().clear(  # pylint: disable=no-member
            spreadsheetId=self.id, range=range_name,
            body={"range": range_name}).execute()

    def write(self, range_name, data, value_input_option="RAW"):
        """
        Write data into the Google Sheet
        :param range_name: Range to write in
        :param data: Data to write
        :param value_input_option: How to recognize input data
        """
        return self._sheets_api_service.spreadsheets().values().update(  # pylint: disable=no-member
            spreadsheetId=self.id, range=range_name,
            body={"values": data}, valueInputOption=value_input_option
        ).execute()

    @property
    def sheets(self):
        return SheetsManager(self)

    @classmethod
    def create(cls, *args, **kwargs):
        return cls.objects().create(*args, **kwargs)

    def __getitem__(self, item):
        """
        Allows get data from the spreadsheet
        using sph["Sheet1!A1:B2"]
        or batch reading
        using sph[["Sheet1!A1:B2", "Sheet1!A5:B6"]]
        """
        if isinstance(item, str):
            return self.read(item)
        else:
            return self.batch_read(item)

    set_item_value_input_option = "RAW"

    def __setitem__(self, item, value):
        """
        Allows writing data into the spreadsheet
        using sph["Sheet1!A1:B2"] = [["l", "o"], ["l", "!"]]
        or batch writing
        using sph[["Sheet1!A1:B2", "Sheet1!A5:B6"]] = \
        ([["l", "o"], ["l", "!"]], [["f", "o"], ["o", "!"]])
        Value input option should be set here (if needed)
        via set_item_value_input_option
        """
        if isinstance(item, str):
            self.write(item, value, self.set_item_value_input_option)
        else:
            # There should be equal count of ranges and values to set
            if not len(item) == len(value):
                raise ValueError("Length of ranges and vales is not equal")

            value_ranges = [
                {"range": range_name,
                 "values": values}
                for range_name, values
                in zip(item, value)
            ]
            self.batch_write(value_ranges, self.set_item_value_input_option)


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
