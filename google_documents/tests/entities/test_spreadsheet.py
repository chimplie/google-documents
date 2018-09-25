import os
from unittest import TestCase

from google_documents.entities import GoogleDriveSpreadsheet

TEST_SPREADSHEET_ID = "10128RKfZ88P24kDMTlPvrblnQMqeEZPlgCq6Xtsjm-4"
TEST_DATA = [
    ['a', 'b', 'test', 'data'],
    ['1', '2', '3', 'hello']
]
TEST_DATA_2 = [
    ['c', 'd', 'data', 'test'],
    ['4', '5', '6', 'bye']
]

RANGE_NAME = "Sheet1!A1:D2"
RANGE_NAME_2 = "Sheet1!A5:D6"
SHEET_RANGE_NAME = "A1:D2"
SHEET_RANGE_NAME_2 = "A5:D6"
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

    def test_batch_write_read_clear(self):
        # Writing data
        self.spreadsheet.batch_write(
            [{"range": RANGE_NAME, "values": TEST_DATA},
             {"range": RANGE_NAME_2, "values": TEST_DATA_2}]
        )

        # Then reading it
        data = self.spreadsheet.batch_read(
            [RANGE_NAME, RANGE_NAME_2]
        )

        # Data should be equal to the data that we just written
        self.assertEqual(data, [TEST_DATA, TEST_DATA_2])

        # Clearing data
        self.spreadsheet.batch_clear([RANGE_NAME, RANGE_NAME_2])

        # Then reading data
        data = self.spreadsheet.batch_read([RANGE_NAME, RANGE_NAME_2])
        # Ranges should be empty
        self.assertEqual(data, [[], []])

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

    def test_sheet_batch_write_read_clear(self):
        """
        Tests all sheets operations
        """
        sheet = self.spreadsheet.sheets.create(title=SHEET_NAME)

        try:
            # Writing test data to the sheet
            sheet[[SHEET_RANGE_NAME, SHEET_RANGE_NAME_2]] = [TEST_DATA, TEST_DATA_2]
            # Reading
            data = sheet[[SHEET_RANGE_NAME, SHEET_RANGE_NAME_2]]

            # Data should be equal to the data that has been wrote
            self.assertEqual(data, [TEST_DATA, TEST_DATA_2])

            # Clearing data
            sheet.batch_clear([SHEET_RANGE_NAME, SHEET_RANGE_NAME_2])
            # There should be no data
            self.assertEqual(sheet[[SHEET_RANGE_NAME, SHEET_RANGE_NAME_2]], [[], []])

        finally:
            # Deleting sheet
            sheet.delete()
