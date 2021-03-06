from unittest import TestCase

from google_documents.entities.file import GoogleDriveFile, GoogleDriveFolder

TEST_FOLDER_ID = "1JfrW_3hV3Sb7rWwtWUuOHddQcDiyQpBY"
TEST_DOCUMENT_ID = "1IoZdqldidkXHtXDxoURmuzmnxwaiCBZx9q1a9chnHVM"


class FileTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.file = GoogleDriveFile.get(TEST_DOCUMENT_ID)
        cls.folder = GoogleDriveFolder.get(TEST_FOLDER_ID)

    '''
    We need to start name of all test from the upper case
    because we need to setup order of tests running
    in test_all() method
    '''
    def Test_init(self):
        """
        Checking that name and mime_type automatically assigned to the file
        """
        item = GoogleDriveFile.files()._get_item(TEST_DOCUMENT_ID)

        self.assertIsNotNone(self.file.name, item["name"])
        self.assertIsNotNone(self.file.mime_type, item["mimeType"])

    def Test_filter(self):
        search_results = GoogleDriveFile.files().filter(
            name=self.file.name
        )
        self.assertIn(self.file, search_results)

    def Test_copy(self):
        self.copy = self.file.copy("Test copy file name")

        # Checking file copy by id
        correct_copy = GoogleDriveFile.get(id=self.copy.id)

        self.assertEqual(self.copy.id, correct_copy.id)
        self.assertEqual(self.copy.name, correct_copy.name)

    def Test_put_to_folder(self):
        folder = GoogleDriveFolder(TEST_FOLDER_ID)
        self.copy.put_to_folder(folder)

        self.assertIn(self.copy, folder)

    def test_all(self):
        # Testing correct initialization
        self.Test_init()

        # Test correct filtering
        self.Test_filter()

        # Testing copying file
        self.Test_copy()

        # Testing putting file to the folder
        self.Test_put_to_folder()
