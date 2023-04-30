from item import Item
class Place:
	def __init__(self, name, suit, building_slot_num, vagabond_is_here=False, forest=False, ruin=False):
		self.neighbors = list()
		self.owner = "No one"
		self.name = name
		self.suit = suit
		self.building_slots = []
		for _ in range(building_slot_num):
			self.building_slots.append(('empty', 'No one'))
		if ruin:
			self.building_slots.pop(0)
			self.building_slots.append(("ruin", "No one"))
		# Owner =  cat, bird, alliance
		self.soldiers = {
			"cat" : 0,
			"bird" : 0,
			"alliance" : 0
		}
		# (Name, quantity)
		self.tokens = []
		self.vagabond_is_here = vagabond_is_here
		self.forest = forest

	def remove_building(self, building_type):
		# building type: (name, owner)
		for i, (building, owner) in enumerate(self.building_slots):
			if building == building_type:
				self.building_slots[i] = ('empty', 'No one')
				return
		raise ValueError("No such building")

	def clear_buildings(self, exception_faction=None):
		removed_buildings = 0
		for i in range(len(self.building_slots)):
			if self.building_slots[i][0] != "ruin" and self.building_slots[i][1] != exception_faction:
				self.building_slots[i] = ('empty', 'No one')
				removed_buildings += 1
		return removed_buildings

	def clear_tokens(self, exception_faction=None):
		if exception_faction == "alliance":
			exception_tokens = ["sympathy"]
		elif exception_faction == "cat":
			exception_tokens = ["keep", "wood"]
		else:
			exception_tokens = []
		removed_tokens = 0
		new_tokens = []
		for i in range(len(self.tokens)):
			if self.tokens[i] in exception_tokens:
				new_tokens.append(self.tokens[i])
			else:
				removed_tokens += 1
		self.tokens = new_tokens
		return removed_tokens
	
	def clear_soldiers(self, exception_faction=None):
		for faction in self.soldiers:
			if faction != exception_faction:
				self.soldiers[faction] = 0

	def add_building(self, building_type, owner):
		# building type: (name, owner)
		for i, (building, _) in enumerate(self.building_slots):
			if building == 'empty':
				self.building_slots[i] = (building_type, owner)
				return
		raise ValueError("No empty building slot")

	def has_opponent_pieces(self, opponent):
		has_building = any(slot[1] == opponent for slot in self.building_slots)
		has_token = False
		if opponent == "alliance":
			has_token = any(token == "sympathy" for token in self.tokens)
		if opponent == "cat":
			has_token = any(token == "keep" or token == "wood" for token in self.tokens)
		return has_building or has_token

	def add_neighbor(self, place_name, to_forest):
		"""
		Args:
			place (Place): The clearing to add as a neighbor
			to_forest (bool): Whether the neighbor is a forest
		"""
		if place_name not in self.neighbors:
			self.neighbors.append((place_name, to_forest))
			self.neighbors.sort()

	def update_pieces(self, buildings = None, soldiers = None, tokens = None, vagabond_is_here=None):
		"""
		Sets the pices based on arguments
		"""
		if vagabond_is_here is not None:
			self.vagabond_is_here = vagabond_is_here

		if not self.forest:
			if buildings is not None:
				if len(self.building_slots) != len(buildings):
					raise ValueError("New building slot number doesn't match old")
				self.building_slots = buildings
			if soldiers is not None:
				self.soldiers = soldiers
			if tokens is not None:
				self.tokens = tokens

	def update_owner(self):
		"""
		Updates the owner based on game rules
		"""
		if self.forest:
			return "No one"
		
		points = {
			"cat" : 0,
			"bird" : 0,
			"alliance" : 0
		}
		points["cat"] += [slot[1] == "cat" for slot in self.building_slots].count(True)
		points["cat"] += self.soldiers["cat"]

		points["bird"] += [slot[1] == "bird" for slot in self.building_slots].count(True)
		points["bird"] += self.soldiers["bird"]
		# Birds win if they tie
		if points["bird"] != 0:
			points["bird"] += 0.1

		points["alliance"] += [slot[1] == "alliance" for slot in self.building_slots].count(True)
		points["alliance"] += self.soldiers["alliance"]

		sorted_points = sorted(points.items(), key=lambda item: item[1])
		if sorted_points[-1][1] == sorted_points[-2][1]:
			self.owner = "No one"
		else:
			self.owner = sorted_points[-1][0]



class Map:
	def __init__(self, object_num:int, clearing_num:int, suits:tuple[str, ...], building_slots:tuple[int, ...], vagabond_index:int, ruin_indeces:tuple[int, ...], paths:tuple[str, ...]):
		self.places = {}
		self.vagabond_position = chr(ord('A')+vagabond_index)
		self.craftables = [Item("sack"), Item("sack"), Item("boot"), Item("boot"), Item("crossbow"), Item("hammer"), Item("sword"), Item("sword"), Item("root_tea"), Item("root_tea"), Item("money"), Item("money")]
		for i in range(object_num):
			# Assuming vagabond can only start in the forest
			if i>=clearing_num:
				if i == vagabond_index:
					self.add_object(Place(name=chr(ord('A')+i), suit='Forest', building_slot_num=0, vagabond_is_here=True, forest=True))
				else:
					self.add_object(Place(name=chr(ord('A')+i), suit='Forest', building_slot_num=0, forest=True))
			else:
				if i in ruin_indeces:
					self.add_object(Place(name=chr(ord('A')+i), suit=suits[i], building_slot_num=building_slots[i], ruin=True))
				else:
					self.add_object(Place(name=chr(ord('A')+i), suit=suits[i], building_slot_num=building_slots[i]))
		
		for path in paths:
			self.add_path(path[:1], path[1:])

	def add_object(self, object):
		if isinstance(object, Place) and object.name not in self.places:
			self.places[object.name] = object
			return True
		else:
			return False
	
	def move_vagabond(self, destination_name:str):
		self.vagabond_position = destination_name
		for place in self.places.values():
			if place.vagabond_is_here:
				place.vagabond_is_here = False
			if place.name == destination_name:
				place.vagabond_is_here = True
	
	def add_path(self, object1, object2):
		if object1 in self.places and object2 in self.places:
			if ord(object2)>ord('L'):
				self.places[object1].add_neighbor(object2, to_forest = True)
				self.places[object2].add_neighbor(object1, to_forest = False)
			else:
				self.places[object1].add_neighbor(object2, to_forest = False)
				self.places[object2].add_neighbor(object1, to_forest = False)
			return True
		else:
			return False
	
	def count_on_map(self, what_to_look_for, per_suit = False):
		"""
		Args:
			counts buildings/tokens on the map
			what_to_look_for:(list[type,name])
			per suit(bool): return count per suit in a dict or just integer
		Returns:
			count if per suit: dict of counts per suit, if not int
		"""
		if per_suit:
			count = {
				"rabbit" : 0,
				"fox" : 0,
				"mouse" : 0
				}
			
			for key in sorted(list(self.places.keys())):
				if what_to_look_for[0] == "building":
					for building_slot in self.places[key].building_slots:
						if building_slot[0] == what_to_look_for[1]:
							count[self.places[key].suit] += 1

				if what_to_look_for[0] == "token":
					for token in self.places[key].tokens:
						if token == what_to_look_for[1]:
							count[self.places[key].suit] += 1
		
		else:
			count = 0
			for key in sorted(list(self.places.keys())):
				if what_to_look_for[0] == "building":
					for building_slot in self.places[key].building_slots:
						if building_slot[0] == what_to_look_for[1]:
							count += 1
							
				if what_to_look_for[0] == "token":
					for token in self.places[key].tokens:
						if token == what_to_look_for[1]:
							count += 1
		return count
	
	def get_connected_places(self, start_place, player_name = 'cat', visited=None):
		"""
		Finds all places connected to the start_place through places that are all owned by player_name.
		
		Args:
		- start_place (Place): the starting place to search from
		- player_name (str): the name of the player who owns all places in the path
		- visited (set): set of places that have already been visited
		
		Returns:
		- set of all places that are connected to the start_place through places owned by player_name
		"""
		if start_place.owner != player_name:
			return set()
		
		if visited is None:
			visited = set()
		visited.add(start_place)
		connected_places = set()
		for path in start_place.neighbors:
			next_place = self.places[path[0]]
			if next_place not in visited and next_place.owner == player_name:
				connected_places.update(self.get_connected_places(next_place, player_name, visited))
		connected_places.add(start_place)
		return connected_places

	def check_vagabond(self):
		vagabond_num = 0
		for key in sorted(list(self.places.keys())):
			vagabond_num += self.places[key].vagabond_is_here
		assert vagabond_num == 1

	def count_paths(self):
		i = 0
		for key in sorted(list(self.places.keys())):
			i+=len(self.places[key].neighbors)
		print(i)

	def update_owners(self):
		"""
		Updates owners of all places on the map
		"""
		for key in sorted(list(self.places.keys())):
			self.places[key].update_owner()

	def print_graph(self):
		for key in sorted(list(self.places.keys())):
			
			#print(key + str(self.places[key].neighbors))
			print(key, self.places[key].soldiers, self.places[key].building_slots, self.places[key].tokens, self.places[key].suit)


def build_regular_forest():
	clearing_num = 12
	suits = ["fox", "rabbit", "mouse", "rabbit", "mouse", "rabbit", "fox", "mouse", "fox", "fox", "mouse", "rabbit"]
	building_slots = [1, 2, 2, 2, 2, 1, 2, 3, 2, 2, 2, 1]
	vagabond_index = 14
	ruin_indeces = [3, 6, 7, 8]
	ruin_items = [Item("sword"), Item("sack"), Item("boot"), Item("hammer")]
	paths = ['AB', 'AM', 'AD', 'AN', 'AE', 'BC', 'BM', 'CM', 'CD', 'CI','CO',
	   'DM', 'DN', 'DG', 'DO', 'EN', 'EG', 'EF', 'EP', 'GP', 'GQ', 'GF',
		'GH', 'GR', 'GO', 'GN', 'GK', 'FP', 'FQ', 'FJ', 'HO', 'HR', 'HS',
		  'HL', 'HI', 'IO', 'IS', 'IL', "JF", 'JK', 'JQ', 'JT', 'KL', 'KT',
		    'KR', 'KQ', 'LT', 'LS', 'LR']
	map = Map(20, clearing_num=clearing_num, building_slots=building_slots, suits=suits, vagabond_index=vagabond_index, ruin_indeces=ruin_indeces, paths=paths)

	starting_pieces = [('A', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('sawmill', 'cat')], 'tokens' : ['keep']}),
		     ('D', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('workshop', 'cat'), ('ruin', ruin_items[0])]}),
			   ('E', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('recruiter', 'cat'), ('empty', 'No one')]}),
			   ('G', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('ruin', ruin_items[1])]}),
			   ('H', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('empty', 'No one'), ('ruin', ruin_items[2])]}),
			   ('I', {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}, 'buildings': [('empty', 'No one'), ('ruin', ruin_items[3])]}),
			     ('L', {'soldiers' : {'cat': 0, 'bird' : 6, 'alliance' : 0}, 'buildings': [('roost', 'bird')]})]
	basic = {'soldiers' : {'cat': 1, 'bird' : 0, 'alliance' : 0}}
	i = 0
	for key in sorted(list(map.places.keys())):
		if not map.places[key].forest:
			if map.places[key].name == starting_pieces[i][0]:
				map.places[key].update_pieces(**starting_pieces[i][1])
				i += 1
			else:
				map.places[key].update_pieces(**basic)
	map.update_owners()

	return map