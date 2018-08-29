import os
from unittest import TestCase

from google_documents.entities import GoogleDriveSpreadsheet

TEST_SPREADSHEET_ID = "10128RKfZ88P24kDMTlPvrblnQMqeEZPlgCq6Xtsjm-4"
TEST_DATA = [
    ['a', 'b', 'test', 'data'],
    ['1', '2', '3', 'hello']
]

RANGE_NAME = "Sheet1!A1:D2"


class GoogleDriveSpreadsheetTestCase(TestCase):
    def setUp(self):
        self.spreadsheet = GoogleDriveSpreadsheet(TEST_SPREADSHEET_ID)

    def test_write_read(self):
        # Writing data
        self.spreadsheet.write(range_name=RANGE_NAME, data=TEST_DATA)
        # Then reading it
        data = self.spreadsheet.read(range_name=RANGE_NAME)

        # Data should be equal
        self.assertEqual(data, TEST_DATA)
