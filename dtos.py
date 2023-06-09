from item import Item
class ActionDTO:
    def __init__(self) -> None:
        pass

class Battle_DTO(ActionDTO):
    def __init__(self, place:str, against_whom:str, armorer_usage: bool = False, brutal_tactics_usage: bool = False, card_ID = None) -> None:
        super().__init__()
        self.where = place
        self.against_whom = against_whom
        self.card_ID = card_ID
        self.armorer_usage = armorer_usage
        self.brutal_tactics_usage = brutal_tactics_usage
    
    def __eq__(self, other) -> bool:
        if self.where == other.where and self.against_whom == other.against_whom and self.card_ID == other.card_ID:
            return True
        else:
            return False


class CraftDTO(ActionDTO):
    # Everything except ambush, ambush is a taken care of in Actor class
    def __init__(self, card) -> None:
        super().__init__()
        self.what = card.craft
        self.card = card
        self.get_cost((card.craft_suit, card.craft_cost))
        self.get_item(card.craft)

    def get_item(self, craft): # Probably not necessary
        if craft in [Item("sack"), Item("money"), Item("boot"), Item("sword"), Item("crossbow"), Item("torch"), Item("root_tea"), Item("hammer")]:
            self.item = craft
        else:
            self.item = None

    def __eq__(self, other) -> bool:
        if isinstance(other, CraftDTO):
            if self.card.ID == other.card.ID:
                return True
        return False

    def get_cost(self, cost):
        if cost[0] == "all":
            self.cost = {
                "rabbit": 1,
                "mouse": 1,
                "fox": 1
            }
        if cost[0] == "anything":
            self.cost = "anything"
        else:
            self.cost = {
                "rabbit": 0,
                "mouse": 0,
                "fox": 0
            }
            if cost[0] in ["rabbit", "mouse", "fox"]:
                self.cost[cost[0]] = cost[1]
class MoveDTO(ActionDTO):
    def __init__(self, start, end, how_many, who, card_ID=None, vagabond_allies = (0, None)) -> None:
        super().__init__()
        self.how_many = how_many
        self.start = start
        self.end = end
        self.card_ID = card_ID
        self.vagabond_allies = vagabond_allies
        self.who = who

    def __eq__(self, other) -> bool:
        if self.start == other.start and self.end == other.end and self.how_many == other.how_many and self.card_ID == other.card_ID and self.vagabond_allies == other.vagabond_allies:
            return True
        else:
            return False
        
class OverworkDTO(ActionDTO):
    def __init__(self, place, cardID) -> None:
        super().__init__()
        self.place = place
        self.cardID = cardID
        
    def __eq__(self, other) -> bool:
        if self.place == other.place and self.cardID == other.cardID:
            return True
        else:
            return False
        
