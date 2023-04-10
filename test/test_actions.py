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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    game.eyrie.change_role('Commander')
    dice_rolls = [3, 3]

    attacker_chosen_pieces = game.priority_to_list(attacker_pice_lose_priorities, game.map.places['H'], attacker)
    defender_chosen_pieces = game.priority_to_list(defender_pice_lose_priorities, game.map.places['H'], defender)    
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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
    dmg_attacker, dmg_defender = game.get_battle_damages(attacker, defender, dice_rolls, place_name, armorers = False)
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


def test_move():
    pass


test_movement_slip()