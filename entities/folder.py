class GoogleDriveFolder:
    def __init__(self, id):
        self.id = id

    @classmethod
    def from_item(cls, item):
        return cls(id=item["id"])

    def __eq__(self, other):
        return self.id == other.id

    def __contains__(self, item):
        return self in item.parents
