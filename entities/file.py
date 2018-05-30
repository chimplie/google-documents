import googleapiclient
from googleapiclient.http import MediaFileUpload

from google_documents.service import drive_service
from google_documents.settings import MIME_TYPES


class GoogleDriveFile:
    id: str
    name: str

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id} - {self.name}>"

    @property
    def parents(self):
        # TODO lazy loading of the all files attributes

        response = drive_service.files().get(
            fileId=self.id, fields='parents'
        ).execute()

        for parent in response["parents"]:
            yield GoogleDriveFolder(id=parent)

    @property
    def url(self):
        return f"https://docs.google.com/document/d/{self.id}"

    def __init__(self, id, name=None, mime_type=None, *args, **kwargs):
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

    @classmethod
    def get(cls, id):
        try:
            item = drive_service.files().get(
                fileId=id).execute()

            return cls.from_item(item)
        except googleapiclient.errors.HttpError:
            return None

    def copy(self, file_name: str):
        """
        Makes copy of the file
        :param file_name: Destination file name
        :return: GoogleDriveDocument copy
        """
        file_item = drive_service.files().copy(
            fileId=self.id, body={"name": file_name}
        ).execute()

        return self.from_item(file_item)

    def delete(self):
        """
        Delets file from the Google Drive
        """
        drive_service.files().delete(
            fileId=self.id
        )

    def put_to_folder(self, folder):
        """
        Puts the file into folder
        """
        # Calling API
        return drive_service.files().update(
            fileId=self.id,
            addParents=folder.id,
            fields='id, parents').execute()


class GoogleDriveFolder(GoogleDriveFile):
    def __contains__(self, item):
        return self in item.parents

    @property
    def children(self):
        children_items = drive_service.files().list(
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
        export_bytes = drive_service.files().export(
            fileId=self.id, mimeType=mime_type
        ).execute()

        open(file_name, "wb+").write(export_bytes)

    def update(self, file_name, mime_type=MIME_TYPES['docx']):
        # Making media body for the request
        media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)

        drive_service.files().update(
            fileId=self.id,
            media_body=media_body
        ).execute()


class GoogleDriveFilesFactory:
    file_classes = {
        MIME_TYPES['folder']: GoogleDriveFolder,
        MIME_TYPES['document']: GoogleDriveDocument,
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
