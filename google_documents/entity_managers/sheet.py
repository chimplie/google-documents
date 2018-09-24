from google_documents.entities.sheet import Sheet


class SheetsManager:
    """
    Provides managing of sheets in the Google Spreasheet
    """
    _sheets_objects: [Sheet] = None

    @property
    def _sheets(self):
        if self._sheets_objects is None:
            self._fetch()

        return self._sheets_objects

    def __init__(self, spreadsheet):
        self.spreadsheet = spreadsheet

    def _fetch(self):
        sheets_items = self.spreadsheet._sheets_api_service.spreadsheets().get(
            spreadsheetId=self.spreadsheet.id,
            fields='sheets.properties'
        ).execute().get("sheets", [])

        self._sheets_objects = []
        for sheet_item in sheets_items:
            sheet = Sheet.from_item(sheet_item)
            sheet.assign_spreadsheet(self.spreadsheet)
            self._sheets_objects.append(sheet)

    def __len__(self):
        return len(self._sheets)

    def __iter__(self):
        return self

    _current_index = 0

    def __next__(self):
        if self._current_index >= len(self._sheets):
            self._current_index = 0
            raise StopIteration
        else:
            sheet = self._sheets[self._current_index]
            self._current_index += 1
            return sheet

    def __getitem__(self, item):
        for sheet in self._sheets:
            if sheet.title == item:
                return sheet

        raise KeyError(f"Sheet with title `{item}` "
                       f"has not found at {self.spreadsheet}")

    def all(self):
        return self._sheets

    @staticmethod
    def _get_add_sheet_request(sheet: Sheet):
        return {
            "addSheet": {
                "properties": sheet.to_item()
            }
        }

    def _update_sheets_from_response(self, sheets, response):
        for reply in response['replies']:
            _sheet = Sheet.from_item(reply["addSheet"])
            sheet = list(filter(lambda s: s.title == _sheet.title, sheets))[0]

            # Copy all sheet properties from the response to the passed sheet
            sheet.__dict__ = _sheet.__dict__.copy()

            sheet.assign_spreadsheet(self.spreadsheet)
            self._sheets.append(sheet)

    def create(self, **kwargs):
        """
        Creates sheet in the spreadsheet
        """
        sheet = Sheet(**kwargs)

        self.batch_create([sheet])

        return sheet

    def batch_create(self, sheets: [Sheet]):
        """
        Creates sheets in the Spreadsheet from the Sheet objects
        """
        response = self.spreadsheet._sheets_api_service.\
            spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet.id,
                body={"requests": list(map(
                    self._get_add_sheet_request, sheets))}
            ).execute()

        # Append new sheets to sheets collection
        self._update_sheets_from_response(sheets, response)

        return response
