

def get_options_craft(self, map):
    craft_options = []
    activations = 0
    for item in self.satchel + self.other_items:
        if item.name == "hammer" and not item.exhausted and not item.damaged:
            activations += 1
    for card in self.deck.cards:
        if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects: 
            if card.craft_suit == "ambush":
                pass
            elif activations >= card.craft_cost:
                craft_options.append(CraftDTO(card))
            elif card.craft_suit == "anything":
                pass
            elif card.craft_suit == "all" and activations >= 3:
                craft_options.append(CraftDTO(card))
            elif card.craft_suit == "dominance" and self.victory_points >= 10 and self.win_condition == "points":
                craft_options.append(CraftDTO(card))
    return craft_options       

 
def get_slip_options(self, map):
    slip_options = []
    for neighbor in map.places[map.vagabond_position].neighbors:
        slip_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, 0, who='vagabond'))
    return slip_options

def get_moves(self, map):
    move_options = []
    for neighbor in map.places[map.vagabond_position].neighbors:
        if not neighbor[1]:
            boot_cost = 2 if self.relations[map.places[neighbor[0]].owner] == 'hostile' else 1
            if [item for item in self.satchel if item.exhausted == False and item.damaged == False].count(Item("boot")) >= boot_cost:
                move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=0, who='vagabond'))
                if self.relations['cat'] == 'friendly' and map.places[map.vagabond_position].soldiers['cat'] > 0:
                    for i in range(map.places[map.vagabond_position].soldiers['cat']):
                        move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=1, who='vagabond', vagabond_allies=(i+1, 'cat')))
                if self.relations['bird'] == 'friendly' and map.places[map.vagabond_position].soldiers['bird'] > 0:
                    for i in range(map.places[map.vagabond_position].soldiers['bird']):
                        move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=1,  who='vagabond', vagabond_allies=(i+1, 'bird')))
                if self.relations['alliance'] == 'friendly' and map.places[map.vagabond_position].soldiers['alliance'] > 0:
                    for i in range(map.places[map.vagabond_position].soldiers['alliance']):
                        move_options.append(MoveDTO(map.vagabond_position, map.places[neighbor[0]].name, how_many=1,  who='vagabond', vagabond_allies=(i+1, 'alliance')))
    return move_options

def get_refresh_options(self):
    all_items = self.satchel + self.other_items
    exhausted_items = [item for item in all_items if item.exhausted]
    return exhausted_items

def get_repair_options(self):
    hammer_avaible = any(item for item in self.satchel if item.name == "hammer" and not item.damaged and not item.exhausted)
    all_items = self.satchel + self.other_items
    damaged_items = [item for item in all_items if item.damaged]
    if hammer_avaible:
        return damaged_items
    else:
        return []

def get_battle_options(self, map):
    battle_options = []
    if any(item for item in self.satchel if item.name == "sword" and not item.damaged and not item.exhausted):
        for army in map.places[map.vagabond_position].soldiers:
            if map.places[map.vagabond_position].soldiers[army] > 0:
                battle_options.append(Battle_DTO(map.vagabond_position, army))
                if self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, army, brutal_tactics_usage=True))
                if self.armorers:
                    battle_options.append(Battle_DTO(map.vagabond_position, army, armorer_usage=True))
                if self.armorers and self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, army, brutal_tactics_usage=True, armorer_usage=True))
        for building_slots in map.places[map.vagabond_position].building_slots:
            if building_slots[1] != "No one" and not isinstance(building_slots[1], Item):
                battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1]))
                if self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1], brutal_tactics_usage=True))
                if self.armorers:
                    battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1], armorer_usage=True))
                if self.armorers and self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, building_slots[1], brutal_tactics_usage=True, armorer_usage=True))
        
        if "sympathy" in map.places[map.vagabond_position].tokens:
                battle_options.append(Battle_DTO(map.vagabond_position, 'alliance'))
                if self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'alliance', brutal_tactics_usage=True))
                if self.armorers:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'alliance', armorer_usage=True))
                if self.armorers and self.brutal_tactics:
                    battle_options.append(Battle_DTO(map.vagabond_position, 'alliance', brutal_tactics_usage=True, armorer_usage=True))
        if "wood" in map.places[map.vagabond_position].tokens or "keep" in map.places[map.vagabond_position].tokens:
            battle_options.append(Battle_DTO(map.vagabond_position, 'cat'))
            if self.brutal_tactics:
                battle_options.append(Battle_DTO(map.vagabond_position, 'cat', brutal_tactics_usage=True))
            if self.armorers:
                battle_options.append(Battle_DTO(map.vagabond_position, 'cat', armorer_usage=True))
            if self.armorers and self.brutal_tactics:
                battle_options.append(Battle_DTO(map.vagabond_position, 'cat', brutal_tactics_usage=True, armorer_usage=True))
    return battle_options

def get_quest_options(self, map):
    quest_options = []
    current_clearing = map.places[map.vagabond_position]
    for quest_card in self.quest_deck.cards:
        if (quest_card.suit == current_clearing.suit and
                self.has_items(quest_card.item1, quest_card.item2)):
            quest_options.append((quest_card.ID, 'draw'))
            quest_options.append((quest_card.ID, 'VP'))
    return quest_options


def get_thief_ability(self, map):
    if not self.has_non_exhausted_item(Item('torch')):
        return []
    thief_ability_options = []
    current_clearing = map.places[map.vagabond_position]
    if current_clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in current_clearing.building_slots]or 'keep' in current_clearing.tokens or 'wood' in current_clearing.tokens:
        thief_ability_options.append('cat')
    if current_clearing.soldiers['bird'] > 0 or True in [slot[0] == 'roost' for slot in current_clearing.building_slots]:
        thief_ability_options.append('bird')
    if current_clearing.soldiers['alliance'] > 0 or True in [slot[0] == 'base' for slot in current_clearing.building_slots] or "sympathy" in current_clearing.tokens:
        thief_ability_options.append('alliance')
    return thief_ability_options
    
def get_ruin_explore_options(self, map):
    if not self.has_non_exhausted_item(Item('torch')):
        return []
    current_clearing = map.places[map.vagabond_position]
    has_ruin = any(slot[0] == 'ruin' for slot in current_clearing.building_slots)
    if has_ruin:
        return [(has_ruin, "explore")]
    return []


def get_strike_options(self, map):
    if not self.has_non_exhausted_item(Item("crossbow")):
        return []
    strike_options = []
    current_clearing = map.places[map.vagabond_position]
    for opponent in ['cat', 'bird', 'alliance']:
        if current_clearing.soldiers[opponent] > 0:
            strike_options.append((current_clearing.name, opponent, 'soldier'))
            continue
        if opponent=="alliance" and 'sympathy' in current_clearing.tokens:
            strike_options.append((current_clearing.name, opponent, 'sympathy'))
        if opponent=="cat" and 'keep' in current_clearing.tokens:
            strike_options.append((current_clearing.name, opponent, 'keep'))
        if opponent=="cat" and 'wood' in current_clearing.tokens:
            strike_options.append((current_clearing.name, opponent, 'wood'))
        for slot in current_clearing.building_slots:
            if slot[1]==opponent:
                strike_options.append((current_clearing.name, opponent, slot[0]))
        
    return strike_options


def get_aid_options(self, map, opponents):
    aid_options = []
    current_clearing = map.places[map.vagabond_position]
    # Iterates through name
    for opponent in opponents:
        if current_clearing.has_opponent_pieces(opponent.name):
            relation = self.relations[opponent.name]
            if relation == 'hostile':
                continue
            item_choices = []  # Get items from the opponent
            for item in opponent.items: #Iterates through opponent objects from arquments
                item_choices.append(Item(item.name))
            item_choices = set(item_choices)
            for card in self.deck.cards:
                if card.card_suit == current_clearing.suit or card.card_suit == 'bird':
                    if item_choices:
                        for item in item_choices:
                            aid_options.append((opponent, card.ID, item))
                    else:
                        aid_options.append((opponent, card.ID, None))
    return aid_options


def get_item_dmg_options(self, map):
    """Returns a list of items that can be damaged"""
    item_dmg_options = []
    for item in self.satchel + self.other_items:
        if not item.damaged:
            item_dmg_options.append(item)
    self.refresh_allied_soldiers(map)
    for soldier in self.allied_soldiers:
        item_dmg_options.append(soldier)
    random.shuffle(item_dmg_options)
    self.items_to_damage = item_dmg_options
    

def get_discard_items_down_to_sack_options(self):
    max_items_satchtel = 6 + self.other_items.count(Item("sack")) * 2
    if len(self.satchel) <= max_items_satchtel:
        return
    return self.satchel