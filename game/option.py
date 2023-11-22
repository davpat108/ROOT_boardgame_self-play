class option():
    def __init__(self, name, **kwargs):
        self.name = name
        self.attributes = kwargs

    def __eq__(self, other):
        return self.name == other.name and self.attributes == other.attributes

