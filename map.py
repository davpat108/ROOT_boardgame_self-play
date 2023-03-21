class Map_object:
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

	
	def add_neighbor(self, clearing, to_forest):
		if clearing not in self.neighbors:
			self.neighbors.append((clearing, to_forest))
			self.neighbors.sort()

	def update_pieces(self, buildings, soldiers, tokens, vagabond_is_here=False):
		"""
		Sets the pices based on arguments
		"""
		self.vagabond_is_here = vagabond_is_here
		if not self.forest:
			if len(self.building_slots) != len(buildings):
				raise ValueError("New building slot number doesn't match old")
			self.building_slots = buildings
			self.soldiers = soldiers
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
	objects = {}
	def __init__(self, object_num, clearing_num, suits, building_slots, vagabond_index, ruin_indeces, paths):
		for i in range(object_num):
			# Assuming vagabond can only start in the forest
			if i>=clearing_num:
				if i == vagabond_index:
					self.add_object(Map_object(name=chr(ord('A')+i), suit='Forest', building_slot_num=0, vagabond_is_here=True, forest=True))
				else:
					self.add_object(Map_object(name=chr(ord('A')+i), suit='Forest', building_slot_num=0, forest=True))
			else:
				if i in ruin_indeces:
					self.add_object(Map_object(name=chr(ord('A')+i), suit=suits[i], building_slot_num=building_slots[i], ruin=True))
				else:
					self.add_object(Map_object(name=chr(ord('A')+i), suit=suits[i], building_slot_num=building_slots[i]))
		
		for path in paths:
			self.add_path(path[:1], path[1:])

	def check_vagabond(self):
		vagabond_num = 0
		for key in sorted(list(self.objects.keys())):
			vagabond_num += self.objects[key].vagabond_is_here
		assert vagabond_num == 1

	def add_object(self, object):
		if isinstance(object, Map_object) and object.name not in self.objects:
			self.objects[object.name] = object
			return True
		else:
			return False
	
	def add_path(self, object1, object2):
		if object1 in self.objects and object2 in self.objects:
			if ord(object1)>ord('L') or ord(object2)>ord('L'):
				self.objects[object1].add_neighbor(object2, to_forest = True)
				self.objects[object2].add_neighbor(object1, to_forest = True)
			else:
				self.objects[object1].add_neighbor(object2, to_forest = False)
				self.objects[object2].add_neighbor(object1, to_forest = False)
			return True
		else:
			return False

	def count_paths(self):
		i = 0
		for key in sorted(list(self.objects.keys())):
			i+=len(self.objects[key].neighbors)
		print(i)

	def print_graph(self):
		for key in sorted(list(self.objects.keys())):
			
			print(key + str(self.objects[key].neighbors))
			#print(self.objects[key].suit, self.objects[key].building_slots)


def build_regular_forest():
	clearing_num = 12
	suits = ["fox", "rabbit", "mouse", "rabbit", "mouse", "rabbit", "fox", "mouse", "fox", "fox", "mouse", "rabbit"]
	building_slots = [1, 2, 2, 2, 2, 1, 2, 3, 2, 2, 2, 1]
	vagabond_index = 14
	ruin_indeces = [3, 5, 6, 7]
	paths = ['AB', 'AM', 'AD', 'AN', 'AE', 'BC', 'BM', 'CM', 'CD', 'CI',
	   'DM', 'DN', 'DG', 'DO', 'EN', 'EG', 'EF', 'EP', 'GP', 'GQ', 'GF',
		'GH', 'GR', 'GO', 'GN', 'GK', 'FP', 'FQ', 'FJ', 'HO', 'HR', 'HS',
		  'HL', 'HI', 'IO', 'IS', 'IL', "JF", 'JK', 'JQ', 'JT', 'KL', 'KT',
		    'KR', 'KQ', 'LT', 'LS', 'LR']
	map = Map(20, clearing_num=clearing_num, building_slots=building_slots, suits=suits, vagabond_index=vagabond_index, ruin_indeces=ruin_indeces, paths=paths)
	map.check_vagabond()
	map.count_paths()
	map.print_graph()

	return map