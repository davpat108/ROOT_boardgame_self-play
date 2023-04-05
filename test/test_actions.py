import sys
sys.path.append('.')
from actions import get_battle_damages, resolve_battle, priority_to_list
from map import build_regular_forest
from actors import Marquise, Eyrie, Alliance, Vagabond

def test_resolve_battle():
    # Setup

    map = build_regular_forest()
    place_name = 'H'
    marquise = Marquise()
    eyrie = Eyrie('Despot')
    alliance = Alliance()
    vagabond = Vagabond()
    attacker = 'cat'
    defender = 'bird'
    dice_rolls = [2, 1]
    map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    
    attacker_priorities = ['wood','sawmill', 'workshop', 'recruiter']
    defender_priorities = ['roost']
    attacker_chosen_pieces = priority_to_list(attacker_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_priorities, map.places['H'], defender)
    vagabond_items = None

    # Test
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map, place_name, attacker, defender, vagabond, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items)
    assert map.places['H'].soldiers['cat'] == 2
    assert map.places['H'].soldiers['bird'] == 0
    assert map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]

test_resolve_battle()

    
