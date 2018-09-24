import os
from unittest import TestCase

from google_documents.entities import GoogleDriveSpreadsheet

TEST_SPREADSHEET_ID = "10128RKfZ88P24kDMTlPvrblnQMqeEZPlgCq6Xtsjm-4"
TEST_DATA = [
    ['a', 'b', 'test', 'data'],
    ['1', '2', '3', 'hello']
]

RANGE_NAME = "Sheet1!A1:D2"
SHEET_RANGE_NAME = "A1:D2"
SHEET_NAME = "test sheet"


class GoogleDriveSpreadsheetTestCase(TestCase):
    def setUp(self):
        self.spreadsheet = GoogleDriveSpreadsheet(TEST_SPREADSHEET_ID)

    def test_write_read_clear(self):
        # Writing data
        self.spreadsheet.write(range_name=RANGE_NAME, data=TEST_DATA)
        # Then reading it
        data = self.spreadsheet.read(range_name=RANGE_NAME)

        # Data should be equal
        self.assertEqual(data, TEST_DATA)

        # Clearing data
        self.spreadsheet.clear(range_name=RANGE_NAME)
        # Checking that there is no data anymore
        data = self.spreadsheet.read(range_name=RANGE_NAME)
        self.assertEqual(data, [])

    def test_sheet_create_write_read_clear_delete(self):
        """
        Tests all sheets operations
        """
        sheet_count_initial = len(self.spreadsheet.sheets)

        sheet = self.spreadsheet.sheets.create(title=SHEET_NAME)

        try:
            # There should be sheet in the spreadsheet sheets
            sheet_count_after_create = len(self.spreadsheet.sheets)
            self.assertEqual(sheet_count_after_create - 1, sheet_count_initial)

            # Get item method should work
            self.assertEqual(self.spreadsheet.sheets[SHEET_NAME], sheet)

            # Writing test data to the sheet
            sheet[SHEET_RANGE_NAME] = TEST_DATA
            # Reading
            data = sheet[SHEET_RANGE_NAME]

            # Data should be equal to the data that has beed wrote
            self.assertEqual(data, TEST_DATA)

            # Clearing data
            sheet.clear(SHEET_RANGE_NAME)
            # There should be no data
            self.assertEqual(sheet[SHEET_RANGE_NAME], [])

        finally:
            # Deleting sheet
            sheet.delete()

            # Fetching sheets again
            self.spreadsheet.sheets._sheets_objects = None
            # There should be no sheet anymore
            self.assertEqual(len(self.spreadsheet.sheets), sheet_count_initial)
