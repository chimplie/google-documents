import googleapiclient

from google_documents.service import drive_service
from google_documents.settings import MIME_TYPES


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
    def __init__(self, id, *args, **kwargs):
        super().__init__(id, mime_type=MIME_TYPES['folder'], *args, **kwargs)

    def __contains__(self, item):
        return self in item.parents
