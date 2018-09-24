class FromItemable:
    @classmethod
    def from_item(cls, item):
        return cls(**item)
