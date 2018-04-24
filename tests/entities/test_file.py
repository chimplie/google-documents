# No any database operations - so we need SimpleTestCase
from unittest import TestCase

from google_documents.entities.file import GoogleDriveFile
from google_documents.entities.folder import GoogleDriveFolder

TEST_FOLDER_ID = "1JfrW_3hV3Sb7rWwtWUuOHddQcDiyQpBY"
TEST_DOCUMENT_ID = "1IoZdqldidkXHtXDxoURmuzmnxwaiCBZx9q1a9chnHVM"


class FileTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.file = GoogleDriveFile(TEST_DOCUMENT_ID)
        cls.folder = GoogleDriveFolder(TEST_FOLDER_ID)

    '''
    We need to start name of all test from the upper case
    because we need to setup order of tests running
    in test_all() method
    '''

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
        try:
            # Testing copying file
            self.Test_copy()

            # Testing putting file to the folder
            self.Test_put_to_folder()
        finally:
            # Removing file at the end of the test
            # even if test failed
            self.file.delete()
