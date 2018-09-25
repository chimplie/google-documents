from google_documents.entities.from_itemable import FromItemable


class Color(FromItemable):
    red: float
    green: float
    blue: float

    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.blue = blue
        self.green = green

    def to_item(self):
        return {
            "green": self.green,
            "blue": self.blue,
            "red": self.red
        }


class GridProperties(FromItemable):
    def __init__(self, row_count, column_count):
        self.row_count = row_count
        self.column_count = column_count

    def to_item(self):
        return {
            'rowCount': self.row_count,
            'columnCount': self.column_count
        }

    @classmethod
    def from_item(cls, item):
        return cls(item['rowCount'], item['columnCount'])


class Sheet(FromItemable):
    index: int
    title: str
    tab_color: Color = None
    grid_properties: GridProperties = None

    # Optional - if assigned, makes available sheet read/write methods
    spreadsheet = None

    def assign_spreadsheet(self, spreadsheet):
        self.spreadsheet = spreadsheet

    def _get_spreadsheet_range_name(self, sheet_range_name):
        """
        Returns range name in the sheet
        """
        return f"{self.title}!{sheet_range_name}"

    def read(self, range_name):
        """
        Reads data from the sheet
        :param range_name: Range to read
        """
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        return self.spreadsheet.read(
            self._get_spreadsheet_range_name(range_name)
        )

    def write(self, range_name, data, value_input_option="RAW"):
        """
        Writes data into the sheet
        :param range_name: Range to write in
        :param data: Data to write
        :param value_input_option: How to recognize input data
        :return:
        """
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        return self.spreadsheet.write(
            range_name=self._get_spreadsheet_range_name(range_name),
            data=data,
            value_input_option=value_input_option,
        )

    def clear(self, range_name):
        """
        Clears range in the sheet
        :param range_name: Range to clear
        :return:
        """
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        return self.spreadsheet.clear(
            self._get_spreadsheet_range_name(range_name)
        )

    def batch_read(self, ranges_names):
        """
        Reads multiple ranges from the spreasheet
        :param ranges_names:
        :return:
        """
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        # Convert everything to range names with the sheet name
        ranges_names = list(map(
            self._get_spreadsheet_range_name, ranges_names
        ))
        return self.spreadsheet.batch_read(ranges_names)

    def batch_write(self, value_ranges, value_input_option="RAW"):
        """
        Writes data tu the multiple ranges in the Google Sheet
        :param value_ranges: List of dicts like
        {"range": "A1:B2", data: [[data to write]]}
        :param value_input_option: How to recognize input data
        :return:
        """
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        # Convert ranges in value_ranges to the ranges with the sheet name
        value_ranges = list(map(
            lambda r: {
                **r,
                "range": self._get_spreadsheet_range_name(r["range"])
            },
            value_ranges
        ))

        return self.spreadsheet.batch_write(value_ranges, value_input_option)

    def batch_clear(self, ranges_names):
        """
        Clears multiple ranges in the Google Sheets
        :param ranges_names: Ranges to clear
        :return:
        """
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        ranges_names = list(map(
            self._get_spreadsheet_range_name, ranges_names
        ))

        return self.spreadsheet.batch_clear(ranges_names)

    def delete(self):
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."

        response = self.spreadsheet._sheets_api_service. \
            spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet.id,
                body={"requests": [{"deleteSheet": {"sheetId": self.id}}]}
            ).execute()

        # Delete spreadhseet from sheet
        self.spreadsheet = None

        return response

    @classmethod
    def from_item(cls, item):
        properties = item["properties"]

        grid_properties = None
        if properties.get("gridProperties"):
            grid_properties = GridProperties.from_item(
                properties["gridProperties"])

        tab_color = None
        if properties.get("tabColor"):
            tab_color = Color.from_item(properties["tabColor"])

        return cls(
            id=properties["sheetId"],
            index=properties["index"],
            title=properties["title"],
            tab_color=tab_color,
            grid_properties=grid_properties,
        )

    def to_item(self):
        return {
            "sheetId": self.id,
            "index": self.index,
            "title": self.title,
            "gridProperties": self.grid_properties.to_item()
            if self.grid_properties else None,
            "tabColor": self.tab_color and self.tab_color.to_item(),
        }

    def __getitem__(self, item):
        """
        Allows get data from the spreadsheet using sheet["A1:B2"]
        or batch get using sheet[["A1:B2", "A5:B6"]]
        """
        if isinstance(item, str):
            return self.read(item)
        else:
            return self.batch_read(item)

    set_item_value_input_option = "RAW"

    def __setitem__(self, item, value):
        """
        Allows writing data into the spreadsheet using
        sheet["A1:B2"] = [["l", "o"], ["l", "!"]]
        or using batch writing
        sheet[["A1:B2", "A5:B6]] = \
        ([["l", "o"], ["l", "!"]], [["f", "o"], ["o", "!"]])

        Value input option should be set here (if needed)
        via set_item_value_input_option
        """
        if isinstance(item, str):
            self.write(item, value, self.set_item_value_input_option)
        else:
            # There should be equal count of ranges and values to set
            if not len(item) == len(value):
                raise ValueError("Length of ranges and vales is not equal")

            value_ranges = [
                {"range": range_name,
                 "values": values}
                for range_name, values
                in zip(item, value)
            ]
            self.batch_write(value_ranges, self.set_item_value_input_option)

    def __init__(
            self,
            id=None,
            index=None,
            title=None,
            tab_color=None,
            grid_properties=None
    ):
        self.id = id
        self.index = index
        self.title = title
        self.tab_color = tab_color
        self.grid_properties = grid_properties

    def __eq__(self, other):
        assert self.spreadsheet, "Spreadsheet for the sheet is unknown."
        assert other.spreadsheet, "Spreadsheet for the sheet is unknown."

        return self.spreadsheet == other.spreadsheet and self.id == other.id

    def __repr__(self):
        return f'<Sheet title="{self.title}" index="{self.index}">'

    __str__ = __repr__
