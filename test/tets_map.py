from map import Map

def test_clearing_owner():
    Map(10)
    soldiers = {
			"cat" : 1,
			"bird" : 0,
			"alliance" : 1
		}
    Map.clearings['A'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.clearings['A'].update_owner()

    assert Map.clearings['A'].owner == 'bird'

    soldiers = {
			"cat" : 2,
			"bird" : 0,
			"alliance" : 2
		}
    Map.clearings['A'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.clearings['A'].update_owner()
    assert Map.clearings['A'].owner == 'No one'

    Map.clearings['A'].update_pieces([('empty', 'No one'), ('Workshop', 'cat'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.clearings['A'].update_owner()
    assert Map.clearings['A'].owner == 'cat'