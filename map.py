class Clearing:
	def __init__(self, name, suit, building_slot_num):
		self.neighbors = list()

		self.owner = "No one"
		self.name = name
		self.suit = suit
		self.building_slots = []
		for _ in range(building_slot_num):
			self.building_slots.append(('empty', 'No one'))
		# Owner =  cat, bird, alliance
		self.soldiers = {
			"cat" : 0,
			"bird" : 0,
			"alliance" : 0
		}
		# (Name, quantity)
		self.tokens = []

	
	def add_neighbor(self, clearing):
		if clearing not in self.neighbors:
			self.neighbors.append(clearing)
			self.neighbors.sort()

	def update_pieces(self, buildings, soldiers, tokens):
		"""
		Sets the pices based on arguments
		"""
		if len(self.building_slots) != len(buildings):
			raise ValueError("New building slot number doesn't match old")
		self.building_slots = buildings
		self.soldiers = soldiers
		self.tokens = tokens

	def update_owner(self):
		"""
		Updates the owner based on game rules
		"""
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
	clearings = {}
	def __init__(self, clearing_num = None):
		if clearing_num is not None:
			for i in range(ord('A'), ord('A')+clearing_num):
				# TODO hard code the map
				self.add_clearing(Clearing(chr(i), 'rabbit', 3))

	def add_clearing(self, clearing):
		if isinstance(clearing, Clearing) and clearing.name not in self.clearings:
			self.clearings[clearing.name] = clearing
			return True
		else:
			return False
	
	def add_path(self, clearing1, clearing2):
		if clearing1 in self.clearings and clearing2 in self.clearings:
			self.clearings[clearing1].add_neighbor(clearing2)
			self.clearings[clearing2].add_neighbor(clearing1)
			return True
		else:
			return False
			
	def print_graph(self):
		for key in sorted(list(self.clearings.keys())):
			
			print(key + str(self.clearings[key].neighbors))
			print(self.clearings[key].suit, self.clearings[key].building_slots)