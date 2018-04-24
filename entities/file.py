from googleapiclient.http import MediaFileUpload

from google_documents.entities.folder import GoogleDriveFolder
from google_documents.service import drive_service

DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class GoogleDriveFile:
    id: str
    name: str

    def __eq__(self, other):
        return self.id == other.id

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
        item = drive_service.files().get(
            fileId=id).execute()

        return cls.from_item(item)

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

    def export(self, file_name, mime_type=DOCX_MIME_TYPE):
        """
        Exports content of the file to format specified in the MimeType and writes it to the File
        """
        export_bytes = drive_service.files().export(
            fileId=self.id, mimeType=mime_type
        ).execute()

        open(file_name, "wb+").write(export_bytes)

    def update(self, file_name, mime_type=DOCX_MIME_TYPE):
        # Making media body for the request
        media_body = MediaFileUpload(file_name, mimetype=mime_type, resumable=True)

        drive_service.files().update(
            fileId=self.id,
            media_body=media_body
        ).execute()

    def put_to_folder(self, folder: GoogleDriveFolder):
        """
        Puts the file into folder
        """
        # Calling API
        return drive_service.files().update(
            fileId=self.id,
            addParents=folder.id,
            fields='id, parents').execute()
