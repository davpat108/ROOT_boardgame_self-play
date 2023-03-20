import os
from deck import Deck
from map import Map

if __name__ == "__main__":
    Deck()
    Map(10)
    soldiers = {
			"cat" : 2,
			"bird" : 0,
			"alliance" : 2
		}
    Map.clearings['A'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.clearings['A'].update_owner()