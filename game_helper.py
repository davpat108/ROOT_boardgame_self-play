import random
from dtos import Battle_DTO, OverworkDTO, MoveDTO, CraftDTO, Item
from deck import Deck
import logging
def random_choose(options):
    return random.choice(options)

# ALLIANCE PICK AND CHOOSE CARD
def alliance_choose_card(options):
    return random_choose(options)

def choose_card_prios(card_IDS):
    return random.shuffle(card_IDS)

# BATTLE HELPER FUNCTIONS
def get_loss_prios(actor_name):
    if actor_name == 'bird':
        return ['roost']
    if actor_name == 'cat':
        options = ['sawmill', 'workshop', 'recruiter', 'wood', 'keep']
        random.shuffle(options)
        return options
    if actor_name == 'alliance':
        return ['sympathy', "base"]
    if actor_name == 'vagabond':
        return []
    
def roll_dice():
    dice1 = random.randint(0,3)
    dice2 = random.randint(0,3)
    return [dice1, dice2]

def get_sappers_usage(defender_name, game):
    for actor in [game.marquise, game.alliance, game.eyrie, game.vagabond]:
        if actor.name == defender_name:
            return actor.get_sappers_options()
    
def get_ambush_usage(defender_name, game, placename):
    for actor in [game.marquise, game.alliance, game.eyrie, game.vagabond]:
        if actor.name == defender_name:
            ambush_options = actor.get_ambush_options(game.map.places[placename])
    return ambush_options


def battle_cat(game, option):
    # AMBUSH
    logging.debug(f"Cat initiated a battler agaisnt{option.against_whom}")
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        logging.debug(f"{option.against_whom} has ambushed!")
        options_attacker = game.marquise.get_ambush_options(game.map.places[option.where])
        counterambush_choice = random_choose(options_attacker)
        logging.debug(f"Cat counterambushed? {counterambush_choice}")
        game.ambush(place = option.where, attacker=game.marquise, defender=option.against_whom, bird_or_suit_defender=ambush_option, bird_or_suit_attacker=counterambush_choice)
    # BATTLE
    if option.against_whom == 'vagabond':
        game.vagabond.get_item_dmg_options()
    dice_rolls = roll_dice()
    logging.debug(f"Rolls {dice_rolls[0], {dice_rolls[1]}}")
    card_to_give_if_sympathy = game.marquise.card_to_give_to_alliace_options(game.map.places[option.where].suit)
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('cat'), option.where, 'cat')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('cat', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage)
    logging.debug(f"Cat dmg: {dmg_attacker},{option.against_whom} dmg {dmg_defender}")
    game.resolve_battle(option.where, 'cat', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def battle_bird(game, option):
    # AMBUSH
    logging.debug(f"Bird initiated a battler agaisnt{option.against_whom}")
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        logging.debug(f"{option.against_whom} has ambushed!")
        options_attacker = game.eyrie.get_ambush_options(game.map.places[option.where])
        counterambush_choice = random_choose(options_attacker)
        logging.debug(f"Bird counterambushed? {counterambush_choice}")
        game.ambush(place = option.where, attacker=game.eyrie, defender=option.against_whom, bird_or_suit_defender=ambush_option, bird_or_suit_attacker=counterambush_choice)
    # BATTLE
    if option.against_whom == 'vagabond':
        game.vagabond.get_item_dmg_options()
    dice_rolls = roll_dice()
    logging.debug(f"Rolls {dice_rolls[0], {dice_rolls[1]}}")
    card_to_give_if_sympathy = game.eyrie.card_to_give_to_alliace_options(game.map.places[option.where].suit)
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('bird'), option.where, 'bird')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('bird', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage, card_ID = option.card_ID)
    game.resolve_battle(option.where, 'bird', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def battle_alliance(game, option):
    # AMBUSH
    logging.debug(f"Alliance initiated a battler agaisnt{option.against_whom}")
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        logging.debug(f"{option.against_whom} has ambushed!")
        options_attacker = game.alliance.get_ambush_options(game.map.places[option.where])
        counterambush_choice = random_choose(options_attacker)
        logging.debug(f"Alliance counterambushed? {counterambush_choice}")
        game.ambush(place = option.where, attacker=game.alliance, defender=option.against_whom, bird_or_suit_defender=ambush_option, bird_or_suit_attacker=counterambush_choice)
    # BATTLE
    if option.against_whom == 'vagabond':
        game.vagabond.get_item_dmg_options()
    dice_rolls = roll_dice()
    logging.debug(f"Rolls {dice_rolls[0], {dice_rolls[1]}}")
    card_to_give_if_sympathy = None
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('alliance'), option.where, 'alliance')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('alliance', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage)
    game.resolve_battle(option.where, 'alliance', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def battle_vagabond(game, option):
    # AMBUSH
    logging.debug(f"Vagabond initiated a battler agaisnt{option.against_whom}")
    ambush_options_defender = get_ambush_usage(option.against_whom, game, option.where)
    ambush_option = random_choose(ambush_options_defender)
    if ambush_option:
        logging.debug(f"{option.against_whom} has ambushed!")
        options_attacker = game.vagabond.get_ambush_options(game.map.places[option.where])
        counterambush_choice = random_choose(options_attacker)
        logging.debug(f"Vagabond counterambushed? {counterambush_choice}")
        game.ambush(place = option.where, attacker=game.vagabond, defender=option.against_whom, bird_or_suit_defender=ambush_option, bird_or_suit_attacker=counterambush_choice)
    # BATTLE
    dice_rolls = roll_dice()
    logging.debug(f"Rolls {dice_rolls[0], {dice_rolls[1]}}")
    card_to_give_if_sympathy = game.vagabond.card_to_give_to_alliace_options(game.map.places[option.where].suit)
    attacker_chosen_pieces = game.priority_to_list(get_loss_prios('vagabond'), option.where, 'vagabond')
    defender_chosen_pieces = game.priority_to_list(get_loss_prios(option.against_whom), option.where, option.against_whom)
    dmg_attacker, dmg_defender = game.get_battle_damages('vagabond', option.against_whom, dice_rolls, option.where, sappers = get_sappers_usage(option.against_whom, game), armorers = option.armorer_usage, brutal_tactics = option.brutal_tactics_usage)
    game.resolve_battle(option.where, 'vagabond', option.against_whom, dmg_attacker, dmg_defender, attacker_chosen_pieces, defender_chosen_pieces, card_to_give_if_sympathy)

def get_all_daylight_option_cat(game, recruited_already=False):
    options = []
    options += game.marquise.get_battles(game.map)
    options += game.marquise.get_moves(game.map)
    if not recruited_already:
        options += game.marquise.get_can_recruit(game.map)
    options += game.marquise.get_build_options(game.map)
    options += game.marquise.get_overwork(game.map)
    return options

def get_all_daylight_actions_vagabond(game):
    options = [False]
    options += game.vagabond.get_options_craft(game.map)
    options += game.vagabond.get_moves(game.map)
    options += game.vagabond.get_repair_options()
    options += game.vagabond.get_battle_options(game.map)
    options += game.vagabond.get_quest_options(game.map)
    if game.vagabond.role == "Thief":
        options += game.vagabond.get_thief_ability(game.map)
    elif game.vagabond.role == "Tinkerer":
        raise NotImplementedError("Tinkerer not implemented")
    elif game.vagabond.role == "Ranger":
        raise NotImplementedError("Ranger not implemented")
    else:
        raise ValueError("Wrong role")
    options += game.vagabond.get_ruin_explore_options(game.map)
    options += game.vagabond.get_strike_options(game.map)
    options += game.vagabond.get_aid_options()
    return options


def get_all_daylight_option_alliance(game):
    options = [False]
    options += game.alliance.get_options_craft(game.map)
    options += game.alliance.get_mobilize_options()
    options += game.alliance.get_train_options(game.map)
    return options

def get_all_evening_option_alliance(game):
    options = []
    options += game.alliance.get_moves(game.map)
    options += game.alliance.get_battles(game.map)
    options += game.alliance.get_recruits(game.map)
    options += game.alliance.get_organize_options(game.map)
    return options

def move_and_account_to_sympathy(game, choice):
    logging.debug(f"{choice.who} moved to {choice.where} with {choice.how_many} pieces")
    for actor in [game.marquise, game.eyrie, game.vagabond]:
        if actor.name == choice.who: 
            card_to_give_if_sympathy = game.actor.card_to_give_to_alliace_options(game.map.places[choice.where].suit)
    game.move(choice, card_to_give_if_sympathy)

def cat_daylight_actions(game, choice, recruited_already=False):
    recruited = recruited_already
    moved = False
    # BATTLE
    if isinstance(choice, Battle_DTO):
        logging.debug(f"Cat battled {choice.against_whom} at {choice.where}")
        battle_cat(game, choice)
    # RECRUIT
    elif choice[1] == 'recruit' and not recruited_already:
        recruited = True
        logging.debug(f"Cat recruited")
        game.recruit_cat()
    # MOVE
    elif isinstance(choice, MoveDTO):
        move_and_account_to_sympathy(game, choice)
        moved = True
    # BUILD
    elif len(choice) == 3:
        logging.debug(f"Cat built {choice[1]} at {choice[0]}")
        game.build(place=choice[0], building=choice[1], actor=game.marquise, cost = choice[2])
    # OVERWORK
    elif isinstance(choice, OverworkDTO):
        logging.debug(f"Cat overworked {choice.place} with {choice.cardID}")
        game.overwork(choice.place, choice.cardID)
    
    return recruited, moved


def alliance_daylight_actions(game, choice):
    # CRAFT
    if isinstance(choice, CraftDTO):
        logging.debug(f"Alliance crafted {choice.card.craft}")
        game.craft(game.alliance, choice)
    # MOBILIZE
    elif isinstance(choice, int):
        logging.debug(f"Alliance mobilized with {choice}")
        game.mobilize(choice)
    # TRAIN
    elif choice[1] == 'train':
        logging.debug(f"Alliance trained with {choice[0]}")
        game.train(choice[0])
    else:
        raise ValueError("Wrong choice in alliance daylight")
    
def alliance_evening_actions(game, choice):
    # BATTLE
    if isinstance(choice, Battle_DTO):
        battle_alliance(game, choice)
    # MOVE
    elif isinstance(choice, MoveDTO):
        logging.debug(f"Alliance moved to {choice.where} with {choice.how_many} pieces")
        game.move(choice)
    # RECRUIT
    elif choice[1] == 'recruit':
        logging.debug(f"Alliance recruited at {choice[0]}")
        game.recruit(place = choice[0], actor = game.alliance)
    # ORGANIZE
    elif choice[1] == 'organize':
        logging.debug(f"Alliance organized at {choice[0]}")
        game.organize(placename = choice[0])
    else:
        raise ValueError("Wrong choice in alliance evening")
    
def vagabond_daylight_actions(game, choice, consequitive_aids):
    # CRAFT
    if isinstance(choice, CraftDTO):
        logging.debug(f"Vagabond crafted {choice.card.craft}")
        game.craft(game.vagabond, choice)
    # MOVE
    elif isinstance(choice, MoveDTO):
        move_and_account_to_sympathy(game, choice)
    # BATTLE
    elif isinstance(choice, Battle_DTO):
        battle_vagabond(game, choice)
    # REPAIR
    elif isinstance(choice, Item):
        logging.debug(f"Vagabond repaired {choice}")
        game.vagabond.repair_item(choice)
    # QUEST
    elif choice[1] == 'draw' or choice[1] == 'VP':
        logging.debug(f"Vagabond completed quest {choice[0]}")
        game.complete_quest(*choice)
    # STEAL
    elif choice == 'cat' or choice == 'bird' or choice == 'alliance':
        logging.debug(f"Vagabond stole from {choice}")
        game.steal(choice)
    # RUIN EXPLORATION
    elif choice[1] == 'explore':
        logging.debug(f"Vagabond explored ruin at {game.map.vagabond_position}")
        game.explore_ruin(game.map.vagabond_position)
    # STRIKE
    elif isinstance(choice[2], str):
        logging.debug(f"Vagabond striked at {choice[0]} and destroyed {choice[2]}")
        card_to_give_if_sympathy = game.vagabond.card_to_give_to_alliace_options(game.map.places[game.map.vagabond_position].suit)
        game.strike(choice[0], choice[1], choice[2], card_to_give_if_sympathy)
    # AID
    elif isinstance(choice[1], int):
        logging.debug(f"Vagabond aided at {choice[0]}")
        game.aid(choice[0], choice[1], choice[2], consequitive_aids)
        consequitive_aids += 1
    else:
        raise ValueError("Wrong choice in vagabond daylight")
    return consequitive_aids

def birdsong_card_actions(game, actor):
    # Better burrow bank
    options = actor.bbb_options((game.marquise, game.eyrie, game.alliance, game.vagabond))
    if options:
        choice = random_choose(options)
        logging.debug(f"{actor.name} used Better burrow bank with {choice}")
        game.better_burrow_bank(actor, choice)
    # Stand and deliver
    options = actor.stand_and_deliver_options((game.marquise, game.eyrie, game.alliance, game.vagabond))
    if options:
        choice = random_choose(options)
        logging.debug(f"{actor.name} used stand and deliver with {choice}")
        game.stand_and_deliver(actor, choice)
    # Royal claim
    options = actor.get_royal_claim_options()
    choice = random_choose(options)
    if choice:
        logging.debug(f"{actor.name} used royal heir")
        game.activate_royal_claim(actor)



def daylight_card_actions(game, actor):
    # Command warren
    if actor.name == "cat" and actor.command_warren:
        options = actor.get_battles(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used command warren")
            battle_cat(game, choice)
    if actor.name == "bird" and actor.command_warren:
        options = actor.get_command_warren_battle(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used command warren")
            battle_bird(game, choice)
    if actor.name == "alliance" and actor.command_warren:
        options = actor.get_battles(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used command warren")
            battle_alliance(game, choice)
    if actor.name == "vagabond" and actor.command_warren:
        options = actor.get_battle_options(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used command warren")
            battle_vagabond(game, choice)
    
    # Codebreakers
    if actor.codebreakers:
        options = actor.codebreakers_options(game.map)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used Codebreakers")
            actor.known_hands[choice] = True

    # TAX COLLECTOR TODO anytime during daylight
    if actor.tax_collector:
        options = actor.get_tax_collector_options(game.map)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used tax collector")
            game.tax_collection(actor, choice)
    

def evening_card_actions(game, actor):
    # COBBLER
    if actor.cobbler and actor != 'bird':
        options = actor.get_moves(game.map)
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used cobbler")
            move_and_account_to_sympathy(game, choice)
            
    elif actor.cobbler and actor == 'bird':
        options = actor.get_cobbler_move_options
        choice = random_choose(options)
        if choice:
            logging.debug(f"{actor.name} used cobbler")
            move_and_account_to_sympathy(game, choice)
        
def marquise_birdsong(game):
    birdsong_card_actions(game, game.marquise)
    game.cat_birdsong_wood()

def marquise_daylight(game):
    daylight_card_actions(game, game.marquise)
    # CRAFT
    game.marquise.refresh_craft_activations(game.map)
    craft_options = game.marquise.get_options_craft()
    choice = random_choose(craft_options)
    if choice:
        logging.debug(f"{game.marquise.name} crafted {choice.card.craft}")
        game.marquise.craft(choice)
    # ACTIONS
    recruited_already = False
    actions = 3
    for _ in range(actions):
        # MAIN MOVES
        options = game.get_all_daylight_option_cat(game, recruited_already)
        choice = random_choose(options)
        recruited_already, moved = cat_daylight_actions(game, choice, recruited_already)
        # IF MARCH, MOVE AGAIN
        if moved == True:
            move_options = game.marquise.get_moves(game.map)
            move_choice = random_choose(move_options)
            move_and_account_to_sympathy(game, move_choice)
        
        # IF BIRD CARD, 1 MORE ACTION
        more_move_options = game.marquise.get_use_bird_card_to_gain_moves()
        more_moves_choice = random_choose(more_move_options)
        if more_moves_choice:
            logging.debug(f"Cat used bird card to gain a move")
            game.marquise.cat_use_bird_card_to_gain_move(more_moves_choice)
            actions += 1

def marquise_evening(game):
    evening_card_actions(game, game.marquise)
    draws = game.marquise.count_for_card_draw()
    for _ in range(draws):
        game.marquise.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) >= 0: # DECK ONE LINER
            game.deck = game.discard_deck
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    discard_options = True
    while discard_options:
        discard_options = game.marquise.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.marquise.deck.get_the_card(choice))


def eyrie_birdsong(game):
    birdsong_card_actions(game, game.eyrie)
    # DRAW IF HAND EMPTY
    if len(game.eyrie.deck.cards) == 0:
        game.eyrie.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) >= 0: # DECK ONE LINER
            game.deck = game.discard_deck
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    
    # ADD UP TO TWO CARDS TO DECREE
    options = game.eyrie.get_decree_options()
    choice = random_choose(options)
    logging.debug(f"{game.eyrie.name} added {choice[0].card.name} to decree")
    game.eyrie.add_card_to_decree(*choice)
    options = game.eyrie.get_decree_options()
    options.append(False)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.eyrie.name} added {choice[0].card.name} to decree")
        game.eyrie.add_card_to_decree(*choice)
    options = game.eyrie.get_no_roosts_left_options(game.map)
    if options:
        logging.debug(f"{game.eyrie.name} Has no roosts left")
        choice = random_choose(options)
        game.place_roost_if_zero_roost(choice)
        
def eyrie_daylight(game):
    daylight_card_actions(game, game.eyrie)
    choice = True
    game.eyrie.refresh_craft_activations(game.map)
    while choice:
        options = game.eyrie.get_options_craft(game.map)
        options.append(False)
        choice = random_choose(options)
        if choice:
            game.craft(game.eyrie, choice)

    game.eyrie.refresh_temp_decree()
    turmoil = False

    for _ in range(len(game.eyrie.decrees['recruit'])):
        options = game.eyrie.get_resolve_recruit(game.map)
        if options:
            choice = random_choose(options)
            logging.debug(f"{game.eyrie.name} recruited at {choice[0]}")
            game.recruit(place = choice[0], actor = game.eyrie, card_ID=choice[1])
        else:
            turmoil = True
            logging.debug(f"{game.eyrie.name} fell into turmoil")
            break
    if not turmoil:
        for _ in range(len(game.eyrie.decrees['move'])):
            options = game.eyrie.get_resolve_move(game.map)
            if options:
                choice = random_choose(options)
                move_and_account_to_sympathy(game, choice)
            else:
                turmoil = True
                logging.debug(f"{game.eyrie.name} fell into turmoil")
                break
    if not turmoil:  
        for _ in range(len(game.eyrie.decrees['battle'])):
            options = game.eyrie.get_resolve_battle(game.map)
            if options:
                choice = random_choose(options)
                battle_bird(game, choice)
            else:
                logging.debug(f"{game.eyrie.name} fell into turmoil")
                turmoil = True
                break
    if not turmoil:
        for _ in range(len(game.eyrie.decrees['build'])):
            options = game.eyrie.get_resolve_build(game.map)
            if options:
                choice = random_choose(options)
                logging.debug(f"{game.eyrie.name} built at {choice[0]}")
                game.build(place=choice[0], building="roost", actor=game.eyrie, card_ID = choice[1])
            else:
                logging.debug(f"{game.eyrie.name} fell into turmoil")
                turmoil = True
                break
    
    if turmoil:
        options = game.eyrie.get_turmoil_options()
        choice = random_choose(options)
        logging.debug(f"{game.eyrie.name} chose {choice} as its new leader")
        game.bird_turmoil(choice)
    
def eyrie_eveing(game):
    evening_card_actions(game, game.eyrie)
    game.eyrie_get_points()
    draws = game.eyrie.count_for_card_draw()
    for _ in range(draws):
        game.eyrie.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) >= 0: # DECK ONE LINER
            game.deck = game.discard_deck
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    discard_options = True
    while discard_options:
        discard_options = game.eyrie.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.eyrie.deck.get_the_card(choice))

def alliance_birsong(game):
    birdsong_card_actions(game, game.alliance)
    options = game.alliance.get_revolt_options(game.map)
    options.append(False)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.alliance.name} revolted at {choice[0]}")
        game.revolt(*choice)
    options = game.alliance.get_spread_sympathy_options(game.map)
    options.append(False)
    choice = random_choose(options)
    if choice:
        logging.debug(f"{game.alliance.name} spread sympathy to {choice[0]}")
        game.spread_sympathy(*choice)

def alliance_daylight(game):
    daylight_card_actions(game, game.alliance)
    game.alliance.refresh_craft_activations(game.map)
    choice = True
    while choice:
        options = get_all_daylight_option_alliance(game)
        choice = random_choose(options)
        if choice:
            alliance_daylight_actions(game, choice)

def alliance_evening(game):
    evening_card_actions(game, game.alliance)
    for _ in range(game.alliance.total_officers):
        options = get_all_evening_option_alliance(game)
        if choice:
            choice = random_choose(options)
            alliance_evening_actions(game, choice)
        else:
            break
    draws = game.alliance.count_for_card_draw()
    for _ in range(draws):
        game.alliance.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) >= 0: # DECK ONE LINER
            game.deck = game.discard_deck
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)
    
    discard_options = True
    while discard_options:
        discard_options = game.alliance.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.alliance.deck.get_the_card(choice))
    
    discard_options = True
    while discard_options:
        discard_options = game.alliance.discard_down_to_five_supporters_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.alliance.supporter_deck.get_the_card(choice))

    
def vagabond_birdsong(game):
    birdsong_card_actions(game, game.vagabond)
    for _ in range(game.vagabond.other_items.count(Item("root_tea"))*2 + 3):
        options = game.vagabond.get_refresh_options()
        if options:
            choice = random_choose(options)
            logging.debug(f"{game.vagabond.name} refreshed {choice}")
            game.vagabond.refresh_item(choice)
        else:
            break
    options = game.vagabond.get_slip_options(game.map)
    choice = random_choose(options)
    card_to_give_if_sympathy = game.vagabond.card_to_give_to_alliace_options(game.map.places[choice.where].suit)
    logging.debug(f"{game.vagabond.name} slipped to {choice.where}")
    game.slip(choice.where, card_to_give_if_sympathy)

def vagabond_daylight(game):
    daylight_card_actions(game, game.vagabond)
    choice = True
    consequitive_aids = 0
    while choice:
        options = get_all_daylight_actions_vagabond(game)
        choice = random_choose(options)
        if choice:
            consequitive_aids = vagabond_daylight_actions(game, choice, consequitive_aids)

def vagabond_evening(game):
    evening_card_actions(game, game.vagabond)
    game.vagabond.repair_and_refresh_all()
    draws = game.vagabond.count_for_card_draw()
    for _ in range(draws):
        game.vagabond.deck.add_card(game.deck.draw_card())
        if len(game.deck.cards) >= 0: # DECK ONE LINER
            game.deck = game.discard_deck
            game.deck.shuffle_deck()
            game.discard_deck = Deck(empty=True)

    discard_options = True
    while discard_options:
        discard_options = game.vagabond.discard_down_to_five_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.discard_deck.add_card(game.alliance.deck.get_the_card(choice))
    
    discard_options = True
    while discard_options:
        discard_options = game.vagabond.get_discard_items_down_to_sack_options()
        if discard_options:
            choice = random_choose(discard_options)
            game.vagabond.satchtel.remove(choice)