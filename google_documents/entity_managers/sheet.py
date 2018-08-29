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
            self._sheets_objects.append(Sheet.from_item(sheet_item))

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

        raise KeyError(f"Sheet with title `{item}` has not found at {self.spreadsheet}")

    def all(self):
        return self._sheets
