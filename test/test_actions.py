from actions import resolve_battle
from map import Map
from actors import Vagabond

def test_resolve_battle():
    # Setup
    map = Map()
    map.build_regular_forest()
    place_name = 'place'
    attacker = 'cat'
    defender = 'bird'
    vagabond = Vagabond()
    dmg_attacker = 2
    dmg_defender = 1
    attacker_chosen_pieces = None
    defender_chosen_pieces = None
    vagabond_items = None

    # Test
    resolve_battle(map, place_name, attacker, defender, vagabond, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items)

    
