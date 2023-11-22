def get_turmoil_options(self):
    if len(self.avaible_leaders) == 0:
        self.avaible_leaders = ["Despot", "Commander", "Builder", "Charismatic"]
    return self.avaible_leaders

def get_decree_options(self):
    actions = ["recruit", "move", "battle", "build"]
    options = []
    for card in self.deck.cards:
        for action in actions:
            options.append((action, card.ID, card.card_suit))
    return options

def get_resolve_recruit(self, map):
    recruit_options = []
    for card_ID, card_suit in self.temp_decree["recruit"]:
        matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]
        total_bird_soldiers = sum([place.soldiers["bird"] for place in map.places.values()])
        if self.leader != "Charismatic" and total_bird_soldiers < 20:
            for clearing in matching_clearings:
                if True in [building[0] == 'roost' for building in clearing.building_slots]:
                    recruit_options.append((clearing.name, card_ID))
        if self.leader == "Charismatic" and total_bird_soldiers < 19:
            for clearing in matching_clearings:
                if True in [building[0] == 'roost' for building in clearing.building_slots]:
                    recruit_options.append((clearing.name, card_ID))
    return recruit_options

def get_resolve_move(self, map):
    move_options = []
    for card_ID, card_suit in  self.temp_decree["move"]:
        matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]
        for source_clearing in matching_clearings:
            if source_clearing.soldiers["bird"] > 0:
                for neighbor in source_clearing.neighbors:
                    if not neighbor[1]:
                        dest_clearing = map.places[neighbor[0]]
                        for soldiers in range(1, source_clearing.soldiers["bird"] + 1):
                            move_options.append(MoveDTO(source_clearing.name, dest_clearing.name, how_many=soldiers,card_ID=card_ID, who="bird"))
    return move_options

def get_cobbler_move_options(self, map):
    move_options = []
    for source_clearing in map.places.values():
        if source_clearing.soldiers["bird"] > 0:
            for neighbor in source_clearing.neighbors:
                if not neighbor[1]:
                    dest_clearing = map.places[neighbor[0]]
                    for soldiers in range(1, source_clearing.soldiers["bird"] + 1):
                        move_options.append(MoveDTO(source_clearing.name, dest_clearing.name, how_many=soldiers, who="bird"))

def get_resolve_battle(self, map):
    battle_options = []
    for card_ID, card_suit in self.temp_decree["battle"]:
        matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]
        for clearing in matching_clearings:
            if clearing.soldiers["bird"] > 0:
                if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                    battle_options.append(Battle_DTO(clearing.name, "cat", card_ID=card_ID))
                if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                    battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID=card_ID))
                if clearing.vagabond_is_here:
                    battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID=card_ID))
                if self.armorers:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", card_ID=card_ID, armorer_usage=True))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID=card_ID, armorer_usage=True))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID=card_ID, armorer_usage=True))
                if self.brutal_tactics:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", card_ID=card_ID, brutal_tactics_usage=True))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID=card_ID, brutal_tactics_usage=True))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID=card_ID, brutal_tactics_usage=True))
                if self.brutal_tactics and self.armorers:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", card_ID=card_ID, brutal_tactics_usage=True, armorer_usage=True))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", card_ID=card_ID, brutal_tactics_usage=True, armorer_usage=True))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", card_ID=card_ID, brutal_tactics_usage=True, armorer_usage=True))
    return battle_options

def get_command_warren_battle(self, map):
    battle_options = []
    for clearing in map.places.values():
        if clearing.soldiers["bird"] > 0:
                if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                    battle_options.append(Battle_DTO(clearing.name, "cat"))
                if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                    battle_options.append(Battle_DTO(clearing.name, "alliance"))
                if clearing.vagabond_is_here:
                    battle_options.append(Battle_DTO(clearing.name, "vagabond"))
                if self.armorers:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", armorer_usage=True))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", armorer_usage=True))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", armorer_usage=True))
                if self.brutal_tactics:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", brutal_tactics_usage=True))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", brutal_tactics_usage=True))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", brutal_tactics_usage=True))
                if self.brutal_tactics and self.armorers:
                    if clearing.soldiers['cat'] > 0 or True in [slot[1]=='cat' for slot in clearing.building_slots] or 'keep' in clearing.tokens or 'wood' in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "cat", brutal_tactics_usage=True, armorer_usage=True))
                    if clearing.soldiers['alliance'] > 0 or True in [slot[1]=='alliance' for slot in clearing.building_slots] or "sympathy" in clearing.tokens:
                        battle_options.append(Battle_DTO(clearing.name, "alliance", brutal_tactics_usage=True, armorer_usage=True))
                    if clearing.vagabond_is_here:
                        battle_options.append(Battle_DTO(clearing.name, "vagabond", brutal_tactics_usage=True, armorer_usage=True))
    return battle_options

def get_resolve_building(self, map):
    building_option = []
    if map.count_on_map(("building", "roost")) > 6:
        return building_option
    for card_ID, card_suit in self.temp_decree["build"]:
        matching_clearings = [place for place in map.places.values() if place.suit == card_suit or card_suit == "bird"]
        total_roosts = sum([True in [slot[0] == 'roost' for slot in place.building_slots] for place in map.places.values()])
        if total_roosts <7:
            for clearing in matching_clearings:
                if clearing.owner == 'bird':
                    if not True in [slot[0] == 'roost' for slot in clearing.building_slots] and True in [slot[0] == 'empty' for slot in clearing.building_slots] and not True in [token == 'keep' for token in clearing.tokens]:
                        building_option.append((clearing.name, card_ID))
                
    return building_option

def get_no_roosts_left_options(self, map): 
    for place in map.places.values():
        if True in [slot[0] == 'roost' for slot in place.building_slots]:
            return []
    
    min_soldiers_clearing = []
    min_soldiers = 100
    for place in map.places.values():
        if sum(place.soldiers.values()) == min_soldiers and not 'keep' in place.tokens and not place.forest and ('empty', 'No one') in place.building_slots:
            min_soldiers = sum(place.soldiers.values())
            min_soldiers_clearing.append(place.name)
        if sum(place.soldiers.values()) < min_soldiers and not 'keep' in place.tokens and not place.forest and ('empty', 'No one') in place.building_slots:
            min_soldiers_clearing = []
            min_soldiers = sum(place.soldiers.values())
            min_soldiers_clearing.append(place.name)
        
            
    return min_soldiers_clearing

def get_options_craft(self, map):
    craft_options = []
    for card in self.deck.cards:
        if card.craft in Immediate_non_item_effects or card.craft in map.craftables or card.craft in persistent_effects:
            if card.craft_suit == "ambush":
                pass
            elif card.craft_suit != "dominance" and card.craft_suit != "all" and card.craft_suit != "anything" and self.craft_activations[card.craft_suit] >= card.craft_cost:
                craft_options.append(CraftDTO(card))
            elif card.craft_suit == "anything":
                if sum(self.craft_activations.values()) >= card.craft_cost:
                    craft_options.append(CraftDTO(card))
            elif card.craft_suit == "all":
                if self.craft_activations["fox"] >= 1 and self.craft_activations["rabbit"] >= 1 and self.craft_activations["mouse"] >= 1:
                    craft_options.append(CraftDTO(card))
            elif card.craft_suit == "dominance" and self.victory_points >= 10 and self.win_condition == "points":
                craft_options.append(CraftDTO(card))
    return craft_options 