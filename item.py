class Item():
    def __init__(self, name, exhausted=False, damaged=False) -> None:
        self.name = name
        self.check_names()
        self.exhausted = False
        self.damaged = False

    def __eq__(self, other) -> bool:
        if isinstance(other, Item) and self.name == other.name:
            return True
        return False

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name
    
    def __key(self):
        return (self.name, self.exhausted, self.damaged)

    def __hash__(self):
        return hash(self.__key())

    def check_names(self):
        if not self.name in ["sack", "money", "boot", "sword", "crossbow", "torch", "root_tea", "hammer"]:
            raise ValueError("Item name not valid")
