import sys
sys.path.append('.')
from item import Item
from configs import total_common_card_info
from deck import Deck, Card
from dtos import MoveDTO, CraftDTO, OverworkDTO
from game import Game
from actors import Vagabond, Alliance, Marquise, Eyrie

def test_resolve_battle():
    # Setup
    game = Game(debug=True)

    place_name = 'H'
    attacker = 'cat'
    defender = 'bird'
    # CAT VS BIRD more bird, roost dead
    dice_rolls = [2, 1]
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    
    attacker_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_pice_lose_priorities = ['roost']

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('empty', 'No one')]

    # BIRDS VS CAT more cat
    defender_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker_pice_lose_priorities = ['roost']
    game.map.places['H'].update_pieces(soldiers ={'cat': 3, 'bird': 1, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    attacker = 'bird'
    defender = 'cat'

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['H'].soldiers['bird'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]

    # LOTS OF BIRDS + OWL BONUS VS 2 CATS
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    defender_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker_pice_lose_priorities = ['roost']
    attacker = 'bird'
    defender = 'cat'
    game.eyrie.change_role('Commander')
    dice_rolls = [3, 3]
    
    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.map.places['H'].building_slots == [('empty', 'No one'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens

    # CATS VS BIRDS + OWL BONUS (shouldn't apply)
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    attacker_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    defender_pice_lose_priorities = ['roost']
    attacker = 'cat'
    defender = 'bird'
    dice_rolls = [3, 3]

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)    
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens
    assert dmg_defender == 3

    # VAGABOND attacker VS CATS
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.map.move_vagabond('H')
    attacker_pice_lose_priorities = []
    defender_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('money'), Item('sack'), Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('sword')]

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == True


    # VAGABOND defender VS CATS
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird'),], tokens = ['wood'])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = ['wood','sawmill', 'workshop', 'recruiter', 'keep']
    attacker = 'cat'
    defender = 'vagabond'
    dice_rolls = [3, 3]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('money'), Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('sword')]

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].building_slots == [('sawmill', 'cat'), ('workshop', 'cat'), ('roost', 'bird')]
    assert 'wood' not in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == True
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].damaged == True


    # VAGABOND attacker VS alliance
    game.map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 0, 'alliance': 1}, buildings = [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')], tokens = ['sympathy'])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    attacker_pice_lose_priorities = []
    defender_pice_lose_priorities = ['sympathy','base']
    attacker = 'vagabond'
    defender = 'alliance'
    dice_rolls = [3, 0]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('money'), Item('sword'), Item('sword'), Item('sword')]
    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['alliance'] == 1
    assert game.map.places['H'].building_slots == [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')]
    assert 'sympathy' in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].damaged == True

    # GET SYMPATHY penalty
    game.map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 0, 'alliance': 1}, buildings = [('base', 'alliance'), ('empty', 'No one'), ('empty', 'No one')], tokens = ['sympathy'])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.alliance.supporter_deck = Deck(empty=True)
    game.map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = ['sympathy','base']
    attacker = 'alliance'
    defender = 'vagabond'
    dice_rolls = [3, 3]
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('sword'))
    game.vagabond.add_item(Item('money'))
    game.vagabond.items_to_damage = [Item('boot'), Item('root_tea'), Item('hammer'), Item('crossbow'), Item('torch'), Item('money'), Item('sword'), Item('sword'), Item('sword')]
    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])

    assert game.vagabond.other_items[game.vagabond.other_items.index(Item('money'))].damaged == False
    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['alliance'] == 0
    assert game.map.places['H'].building_slots == [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')]
    assert 'sympathy' not in game.map.places['H'].tokens
    assert sorted(game.vagabond.satchel) == sorted([Item('sword'), Item('sword'), Item('sword'),  Item('boot'), Item('torch')])
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].damaged == True
    assert len(game.vagabond.deck.cards) == 0
    assert game.alliance.supporter_deck.cards[0] == Card(*total_common_card_info[17])

    # VAGABOND attacker vs cat with bird allies turns hostile
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')], tokens = [])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = []
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    game.vagabond.relations['bird'] = "friendly"
    game.vagabond.allied_soldiers = ['bird', 'bird', 'bird']
    game.vagabond.items_to_damage = ['bird', 'bird',  Item('torch'), Item('sword')]

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 1
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == False
    assert game.vagabond.relations['bird'] == "hostile"

    # VAGABOND attacker vs cat with bird allies doesn't turn hostile
    game.map.places['H'].update_pieces(soldiers ={'cat': 2, 'bird': 3, 'alliance': 0}, buildings = [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')], tokens = [])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = []
    attacker = 'vagabond'
    defender = 'cat'
    dice_rolls = [3, 3]
    game.vagabond.relations['bird'] = "friendly"
    game.vagabond.allied_soldiers = ['bird', 'bird', 'bird']
    game.vagabond.items_to_damage = ['bird',  Item('torch'), 'bird', Item('sword')]

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['bird'] == 2
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == True
    assert game.vagabond.relations['bird'] == "friendly"

    # VAGABOND attacker vs cat with bird allies doesn't turn hostile
    game.map.places['H'].update_pieces(soldiers ={'cat': 0, 'bird': 3, 'alliance': 0}, buildings = [('empty', 'No one'), ('empty', 'No one'), ('empty', 'No one')], tokens = [])
    game.map.update_owners()
    game.vagabond = Vagabond(game.map)
    game.map.move_vagabond('H')
    defender_pice_lose_priorities = []
    attacker_pice_lose_priorities = []
    attacker = 'vagabond'
    defender = 'bird'
    dice_rolls = [3, 3]
    game.vagabond.relations['bird'] = "friendly"
    game.vagabond.allied_soldiers = ['bird', 'bird', 'bird']
    game.vagabond.items_to_damage = ['bird',  Item('torch'), 'bird', Item('sword'), Item('boot')]

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = [False, False])
    game.resolve_battle(game.map.places['H'], attacker, defender, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_no_sympathy)
    assert game.map.places['H'].soldiers['cat'] == 0
    assert game.map.places['H'].soldiers['bird'] == 2
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == True
    assert game.vagabond.relations['bird'] == "hostile"


def test_movement_slip():
    game = Game()

    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])


    game.slip(game.map.places['D'], card_to_give_if_no_sympathy)
    game.map.check_vagabond()
    assert game.map.places['D'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 5

    game.map.places['C'].update_pieces(tokens = ['sympathy'])
    game.slip(game.map.places['C'], card_to_give_if_no_sympathy)
    game.map.check_vagabond()
    assert game.map.places['C'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 4
    assert len(game.alliance.supporter_deck.cards) == 5

    game.slip(game.map.places['M'], card_to_give_if_no_sympathy)
    assert game.map.places['M'].vagabond_is_here == True

    game.vagabond = Vagabond(game.map)
    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])
    game.map.move_vagabond('C')
    game.move(game.map.places['C'], game.map.places['D'], 0, game.vagabond, card_to_give_if_no_sympathy, 1)
    assert game.map.places['D'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 1
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('boot'))].exhausted == True

    game.move(game.map.places['D'], game.map.places['C'], 0, game.vagabond, card_to_give_if_no_sympathy, 1)
    assert game.map.places['C'].vagabond_is_here == True
    assert len(game.vagabond.deck.cards) == 0
    assert len(game.alliance.supporter_deck.cards) == 6

    game.move(game.map.places['C'], game.map.places['H'], 1, game.marquise, card_to_give_if_no_sympathy, 1)
    assert game.map.places['H'].soldiers['cat'] == 2
    assert game.map.places['C'].soldiers['cat'] == 0 

    game.move(game.map.places['L'], game.map.places['I'], 6, game.eyrie, card_to_give_if_no_sympathy, 1)    
    assert game.map.places['I'].soldiers['bird'] == 6
    assert game.map.places['L'].soldiers['bird'] == 0

    # vagabond MOVE with allies



def test_craft():
    game = Game()
    game.eyrie = Eyrie(game.map, 'Despot')
    game.marquise = Marquise(game.map)
    game.alliance = Alliance(game.map)
    game.vagabond = Vagabond(game.map)

    game.vagabond.deck.add_card(Card(*total_common_card_info[17]))
    card_to_give_if_no_sympathy = Card(*total_common_card_info[17])

    game.eyrie.deck.add_card(Card(*total_common_card_info[11]))
    game.eyrie.deck.add_card(Card(*total_common_card_info[13]))
    
    # regular item regular cat
    game.marquise.deck.add_card(Card(*total_common_card_info[23]))
    game.marquise.deck.add_card(Card(*total_common_card_info[3]))
    game.marquise.refresh_craft_activations(game.map)
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise, options[0])
    assert len(game.marquise.deck.cards) == 1
    assert len(game.discard_deck.cards) == 1
    assert len(game.marquise.items) == 1
    assert game.marquise.victory_points == 1

    # favor regular cat
    game.map.places['D'].update_pieces(buildings = [("workshop", "cat"), ("workshop", "cat")])
    game.map.places['F'].update_pieces(buildings = [("workshop", "cat")])
    game.marquise.refresh_craft_activations(game.map)
    game.map.move_vagabond('D')

    game.marquise.deck.add_card(Card(*total_common_card_info[4]))
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise,options[options.index(CraftDTO(Card(*total_common_card_info[4])))])
    assert game.map.places['L'].soldiers['bird'] == 0
    assert game.vagabond.satchel[game.vagabond.satchel.index(Item('torch'))].damaged == True
    assert game.map.places['D'].soldiers['cat'] == 1

    # dominance persistents
    game.marquise.victory_points = 11
    game.marquise.deck.add_card(Card(*total_common_card_info[8]))
    options = game.marquise.get_options_craft(game.map)
    game.craft(game.marquise, options[options.index(CraftDTO(Card(*total_common_card_info[8])))])
    assert game.marquise.win_condition == "rabbit"

    # bird vps
    assert game.eyrie.victory_points == 0
    game.map.places['G'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.places['J'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.update_owners()
    game.eyrie.refresh_craft_activations(game.map)
    game.eyrie.deck.add_card(Card(*total_common_card_info[14]))
    options = game.eyrie.get_options_craft(game.map)
    game.craft(game.eyrie, options[options.index(CraftDTO(Card(*total_common_card_info[14])))])
    assert game.eyrie.victory_points == 1
    assert len(game.eyrie.deck.cards) == 2


    # Vagabond,
    assert game.vagabond.victory_points == 0
    game.vagabond.add_item(Item("hammer"))
    game.vagabond.add_item(Item("hammer"))
    game.vagabond.deck.add_card(Card(*total_common_card_info[3]))
    options = game.vagabond.get_options_craft(game.map)
    game.craft(game.vagabond, options[options.index(CraftDTO(Card(*total_common_card_info[3])))])
    assert game.vagabond.victory_points == 3
    assert Item("money") in game.vagabond.other_items

def test_bird_builder_craft():
    game = Game()
    game.eyrie = Eyrie(game.map, 'Builder')
    game.marquise = Marquise(game.map)
    game.alliance = Alliance(game.map)
    game.vagabond = Vagabond(game.map)

    game.eyrie.deck.add_card(Card(*total_common_card_info[11]))
    game.eyrie.deck.add_card(Card(*total_common_card_info[13]))
    

    assert game.eyrie.victory_points == 0
    game.map.places['G'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.places['J'].update_pieces(buildings = [("roost", "bird"), ("ruin", "No one")])
    game.map.update_owners()
    game.eyrie.refresh_craft_activations(game.map)
    game.eyrie.deck.add_card(Card(*total_common_card_info[14]))
    options = game.eyrie.get_options_craft(game.map)
    game.craft(game.eyrie, options[options.index(CraftDTO(Card(*total_common_card_info[14])))])
    assert game.eyrie.victory_points == 2
    assert len(game.eyrie.deck.cards) == 2


def test_build():
    game = Game()

    game.cat_birdsong_wood()

    options = game.marquise.get_build_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    game.build(place=options[0][0], building=options[0][1], actor=game.marquise, cost = options[0][2])
    assert game.marquise.victory_points == 1
    assert game.map.places['B'].building_slots == [('recruiter', 'cat'), ('empty', 'No one')]
    assert game.map.count_on_map(('token', "wood")) == 0


def test_recruit_and_add_to_resolve():
    game = Game()

    game.cat_birdsong_wood()

    options = game.marquise.get_can_recruit(game.map)
    if options:
        game.recruit_cat()
    assert game.map.places['E'].soldiers['cat'] == 2

    decree_options = game.eyrie.get_decree_options()
    game.add_card_to_decree("recruit", *sorted(decree_options["recruit"], key=lambda x: x[0])[0])

    options = game.eyrie.get_resolve_recruit(game.map)
    game.recruit(options[0][0], game.eyrie)
    assert game.map.places['L'].soldiers['bird'] == 7

    assert game.eyrie.victory_points == 0
    game.bird_turmoil("Charismatic")
    options = game.eyrie.get_resolve_recruit(game.map)
    game.recruit(options[0][0], game.eyrie)
    assert game.map.places['L'].soldiers['bird'] == 9
    assert game.eyrie.victory_points == 0
    
def test_overwork():
    game = Game()
    assert game.map.count_on_map(('token', 'wood')) == 0
    game.marquise.deck.add_card(Card(*total_common_card_info[49]))
    game.overwork(game.map.places['A'], 49)
    assert game.map.count_on_map(('token', 'wood')) == 1
    assert game.marquise.deck.get_the_card(49) == "Card not in the deck"

def test_revolt_sympathy():
    game = Game()
    options = game.alliance.get_spread_sympathy_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    assert options[0] == ("B", [])
    game.spread_sympathy(*options[0])
    assert game.map.places['B'].tokens == ["sympathy"]

    options = game.alliance.get_spread_sympathy_options(game.map)
    options.sort(key=lambda x: (x[0], x[1]))
    assert options[0] == ("C", [51])
    game.spread_sympathy(*options[0])
    assert game.map.places['C'].tokens == ["sympathy"]

    game.alliance.supporter_deck.add_card(Card(*total_common_card_info[15]))
    game.alliance.supporter_deck.add_card(Card(*total_common_card_info[16]))

    options = game.alliance.get_revolt_options(game.map)
    options.sort(key=lambda x: (x[0], x[1], x[2])) #place card1 card2 soldiers to gain
    assert options[0] == (game.map.places['C'], 15, 16, 1)

    game.revolt(*options[0])

    assert game.map.places['C'].soldiers['alliance'] == 1
    assert game.map.places['C'].tokens == ["sympathy"]
    assert game.alliance.supporter_deck.get_the_card(15) == "Card not in the deck"
    assert game.alliance.supporter_deck.get_the_card(16) == "Card not in the deck"
    assert game.map.places['C'].building_slots == [("base", "alliance"), ("empty", "No one")]
    assert game.discard_deck.get_the_card(15) == Card(*total_common_card_info[15])



