from game.option import option

    # General actor options
def card_to_give_to_alliace_options(perpetrator, game):
    options = []
    for card in perpetrator.deck.cards:
        if card.card_suit == game.last_alliance_outrage_suit or card.card_suit == "bird":
            options.append(option(name="card_to_give_to_alliace", perpetrator=perpetrator.name, target_card=card.ID))
    return options

def codebreakers_options(perpetrator, game):
    if not perpetrator.codebreakers:
        return
    options = []
    for actor in game.actors:
        if actor != perpetrator:
            options.append(option(name="codebrakers", target_player=actor.name, perpetrator=perpetrator.name))
    return options

def stand_and_deliver_options(perpetrator, game):
    if not actor.stand_and_deliver:
        return [False]
    options = [False] # Maybe you can take from supporter deck but its not implemented
    for actor in game.actors:
        if actor != perpetrator and len(actor.deck.cards) > 0:
            options.append(option(name="stand_and_deliver", perpetrator=perpetrator.name, target_player=actor.name))
    return options

def bbb_options(actor, game):
    if not actor.better_burrow_bank:
        return
    options = []
    for actor in game.actors:
        if actor != actor:
            options.append(actor)
    return options

def discard_down_to_five_options(actor, game):
    if len(actor.deck.cards) <= 5:
        return
    card_IDs = []
    for card in actor.deck.cards:
        card_IDs.append(card.ID)
    return card_IDs
    
def get_sappers_options(actor):
    if not actor.sappers:
        return [False]
    return [True, False]

def get_armorers_options(actor):
    if not actor.armorers:
        return [False]
    return [True, False]

def get_ambush_options(actor, place):
    options = [False]
    for card in actor.deck.cards:
        if card.craft == "ambush" and card.card_suit == place.suit and "suit" not in options:
            options.append("suit")
        if card.craft == "ambush" and card.card_suit == 'bird' and "bird" not in options:
            options.append("bird")
    return options

def get_royal_claim_options(actor):
    if not actor.royal_claim:
        return
    return [True, False]
def get_tax_collector_options(actor, map):
    # Gets all places with soldiers on the map
    if not actor.tax_collector:
        return
    options = [False]
    for place in map.places.values():
        if place.soldiers[actor.name] > 0:
            options.append(place.name)
    return options
def swap_discarded_dominance_card_options(actor, dominance_deck):
    options = []
    for dcard in dominance_deck.cards:
        for card in actor.deck.cards:
            if card.card_suit == dcard.card_suit:
                options.append((card.ID, dcard.ID))
    return options

