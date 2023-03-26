from map import build_regular_forest
from actors import Marquise, Vagabond
from deck import Card
from actions import Battle_DTO

def test_marguise_get_options_craft():
    map = build_regular_forest()
    marguise = Marquise()
    #give marquise a card that can be crafted
    marguise.deck.add_card(Card(*[11, "rabbit", "boot", 1, "rabbit"]))
    #give marquise a card that can be crafted but not enough resources
    marguise.deck.add_card(Card(*[12, "rabbit", "root_tea", 1, "mouse"]))
    marguise.deck.add_card(Card(*[5, "rabbit", "ambush", 0, "ambush"]))
    
    craft_options = marguise.get_options_craft(map)
    assert [craft_option.item for craft_option in craft_options] == ["boot"]
    marguise.get_ambushes()
    assert marguise.ambush == {
            "rabbit": 1,
            "mouse": 0,
            "fox": 0,
            "bird": 0,
        }
    
def test_marquise_battle():
    map = build_regular_forest()
    marguise = Marquise()
    vagabond = Vagabond()
    soldiers = {
			"cat" : 2,
			"bird" : 2,
			"alliance" : 0
		}
    map.places['A'].update_pieces(soldiers = soldiers)
    map.places['A'].update_pieces(tokens = ["sympathy"])
    battle_options = marguise.get_battles(map, vagabond)
    assert battle_options == [Battle_DTO(map.places['A'], "bird"), Battle_DTO(map.places['A'], "alliance")]

