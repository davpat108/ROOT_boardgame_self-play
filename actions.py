
class ActionDTO:
    def __init__(self) -> None:
        pass

class Battle_DTO(ActionDTO):
    def __init__(self, place, against_whom:str) -> None:
        super().__init__()
        self.where = place
        self.against_whom = against_whom
    
    def __eq__(self, other) -> bool:
        if self.where == other.where and self.against_whom == other.against_whom:
            return True
        else:
            return False
    
class CraftDTO(ActionDTO):
    # Everything except ambush, ambush is a taken care of in Actor class
    def __init__(self, craft) -> None:
        super().__init__()
        self.what = craft
        self.get_item(craft)

    def get_item(self, craft):
        if craft == "sack" or "money" or "boot" or "sword" or "crossbow" or "torch" or "root_tea" or "hammer":
            self.item = craft
        else:
            self.item = None
    