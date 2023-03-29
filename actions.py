
class ActionDTO:
    def __init__(self) -> None:
        pass

class Battle_DTO(ActionDTO):
    def __init__(self, place, against_whom:str, card_ID = None) -> None:
        super().__init__()
        self.where = place
        self.against_whom = against_whom
        self.card_ID = card_ID
    
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
    
class MoveDTO(ActionDTO):
    def __init__(self, start, end, how_many, card_ID=None) -> None:
        super().__init__()
        self.how_many = how_many
        self.start = start
        self.end = end
        self.card_ID = card_ID

    def __eq__(self, other) -> bool:
        if self.start == other.start and self.end == other.end and self.how_many == other.how_many:
            return True
        else:
            return False
        
class OverworkDTO(ActionDTO):
    def __init__(self, place, cardID, card_suit) -> None:
        super().__init__()
        self.place = place
        self.cardID = cardID
        self.card_suit = card_suit
        self.check()

    def __eq__(self, other) -> bool:
        if self.place == other.place and self.card_suit == other.card_suit and self.cardID == other.cardID:
            return True
        else:
            return False
        
    def check(self):
        assert self.card_suit in ["rabbit", "mouse", "fox", "bird"]