import sys
sys.path.append('.')
from actions import get_battle_damages, resolve_battle, priority_to_list
from map import build_regular_forest
from actors import Marquise, Eyrie, Alliance, Vagabond, Item
from configs import total_common_card_info
from deck import Deck, Card
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
    vagabond_items_to_remove = None
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    map.update_owners()
    
    attacker_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_pice_lose_priorities = ['roost']

    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove)
    assert map.places['H'].soldiers['cat'] == 2
    assert map.places['H'].soldiers['bird'] == 0
    assert map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]

    # BIRDS VS CAT more cat
    defender_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker_pice_lose_priorities = ['roost']
    map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    map.update_owners()
    attacker = 'bird'
    defender = 'cat'

    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove)
    assert map.places['H'].soldiers['cat'] == 2
    assert map.places['H'].soldiers['bird'] == 0
    assert map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]

    # LOTS OF BIRDS + OWL BONUS VS 2 CATS
    map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    map.update_owners()
    defender_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker_pice_lose_priorities = ['roost']
    attacker = 'bird'
    defender = 'cat'
    eyrie.change_role('Commander')
    dice_rolls = [3, 3]
    
    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove)
    assert map.places['H'].soldiers['cat'] == 0
    assert map.places['H'].soldiers['bird'] == 1
    assert map.places['H'].building_slots == [('empty', 'No one'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in map.places['H'].tokens

    # CATS VS BIRDS + OWL BONUS (shouldn't apply)
    map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    map.update_owners()
    attacker_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_pice_lose_priorities = ['roost']
    attacker = 'cat'
    defender = 'bird'
    eyrie.change_role('Commander')
    dice_rolls = [3, 3]

    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)    
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove)
    assert map.places['H'].soldiers['cat'] == 0
    assert map.places['H'].soldiers['bird'] == 1
    assert map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in map.places['H'].tokens
    assert dmg_defender == 3

    # VAGABOND attacker VS CATS
    map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    map.update_owners()
    map.move_vagabond('H')
    attacker_pice_lose_priorities = []
    defender_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('money'))
    vagabond_items_to_remove = [Item('money'), Item('sack'), Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('sword')]

    assert vagabond.other_items[vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove)
    assert map.places['H'].soldiers['cat'] == 0
    assert map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in map.places['H'].tokens
    assert sorted(vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert vagabond.other_items[vagabond.other_items.index(Item('money'))].damaged == True


    # VAGABOND defender VS CATS
    map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    map.update_owners()
    vagabond = Vagabond()
    map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker = 'cat'
    defender = 'vagabond'
    dice_rolls = [3, 3]
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('money'))
    vagabond_items_to_remove = [Item('money'), Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('sword')]

    assert vagabond.other_items[vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove)
    assert map.places['H'].soldiers['cat'] == 0
    assert map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in map.places['H'].tokens
    assert sorted(vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert vagabond.other_items[vagabond.other_items.index(Item('money'))].damaged == True
    assert vagabond.satchel[vagabond.satchel.index(Item('boot'))].damaged == True


    # VAGABOND attacker VS alliance
    map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 0, 'alliance': 1}, buildings = [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')], tokens = ['sympathy'])
    map.update_owners()
    vagabond = Vagabond()
    map.move_vagabond('H')
    attacker_pice_lose_priorities = []
    defender_pice_lose_priorities = ['sympathy','base']
    attacker = 'vagabond'
    defender = 'alliance'
    dice_rolls = [3, 0]
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('money'))
    vagabond_items_to_remove = [Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('money'), Item('sword'), Item('sword'), Item('sword')]
    vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])

    assert vagabond.other_items[vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove, card_to_give_if_no_sympathy)
    assert map.places['H'].soldiers['alliance'] == 1
    assert map.places['H'].building_slots == [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')]
    assert 'sympathy' in map.places['H'].tokens
    assert sorted(vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert vagabond.satchel[vagabond.satchel.index(Item('boot'))].damaged == True

    # GET SYMPATHY penalty
    map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 0, 'alliance': 1}, buildings = [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')], tokens = ['sympathy'])
    map.update_owners()
    vagabond = Vagabond()
    map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = ['sympathy','base']
    attacker = 'alliance'
    defender = 'vagabond'
    dice_rolls = [3, 3]
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('sword'))
    vagabond.add_item(Item('money'))
    vagabond_items_to_remove = [Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('money'), Item('sword'), Item('sword'), Item('sword')]
    vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])

    assert vagabond.other_items[vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = priority_to_list(attacker_pice_lose_priorities, map.places['H'], attacker)
    defender_chosen_pieces = priority_to_list(defender_pice_lose_priorities, map.places['H'], defender)
    dmg_attacker, dmg_defender = get_battle_damages(attacker, defender, dice_rolls, map, place_name, eyrie, vagabond, marquise, alliance, armorers = False)
    resolve_battle(map.places['H'], attacker, defender, eyrie, vagabond, marquise, alliance, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, vagabond_items_to_remove, card_to_give_if_no_sympathy)
    assert map.places['H'].soldiers['alliance'] == 0
    assert map.places['H'].building_slots == [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')]
    assert 'sympathy' not in map.places['H'].tokens
    assert sorted(vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert vagabond.satchel[vagabond.satchel.index(Item('boot'))].damaged == True
    assert len(vagabond.deck.cards) == 0
    assert alliance.deck.cards[0] == Card(*total_common_card_info[17])

test_resolve_battle()
