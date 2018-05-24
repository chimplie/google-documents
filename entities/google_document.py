from googleapiclient.http import MediaFileUpload

from google_documents.entities.file import GoogleDriveFile
from google_documents.service import drive_service
from google_documents.settings import MIME_TYPES


class GoogleDocument(GoogleDriveFile):
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
