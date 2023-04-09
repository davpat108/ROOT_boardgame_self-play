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

    def crafting_reward(self):
        if self.name == "sack":
            return 1
        elif self.name == "money":
            return 3
        elif self.name == "boot":
            return 1
        elif self.name == "sword":
            return 2
        elif self.name == "crossbow":
            return 1
        elif self.name == "torch":
            raise ValueError("Someone tried to craft a torch")
        elif self.name == "root_tea":
            return 2
        elif self.name == "hammer":
            return 2

    def check_names(self):
        if not self.name in ["sack", "money", "boot", "sword", "crossbow", "torch", "root_tea", "hammer"]:
            raise ValueError("Item name not valid")
