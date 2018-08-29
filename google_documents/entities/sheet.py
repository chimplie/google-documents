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

    @classmethod
    def from_item(cls, item):
        properties = item["properties"]

        grid_properties = None
        if properties.get("gridProperties"):
            grid_properties = GridProperties.from_item(properties["gridProperties"])

        tab_color = None
        if properties.get("tabColor"):
            tab_color = Color.from_item(properties["tabColor"])

        return cls(
            index=properties["index"],
            title=properties["title"],
            tab_color=tab_color,
            grid_properties=grid_properties,
        )

    def __init__(self, index, title, tab_color=None, grid_properties=None):
        self.index = index
        self.title = title
        self.tab_color = tab_color
        self.grid_properties = grid_properties

    def __repr__(self):
        return f'<Sheet title="{self.title}" index="{self.index}">'

    __str__ = __repr__
