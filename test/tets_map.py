from map import Map
from map import build_regular_forest

def test_clearing_owner():
    Map(10)
    soldiers = {
			"cat" : 1,
			"bird" : 0,
			"alliance" : 1
		}
    Map.objects['A'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.objects['A'].update_owner()

    assert Map.objects['A'].owner == 'bird'

    soldiers = {
			"cat" : 2,
			"bird" : 0,
			"alliance" : 2
		}
    Map.objects['A'].update_pieces([('empty', 'No one'), ('empty', 'No one'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.objects['A'].update_owner()
    assert Map.objects['A'].owner == 'No one'

    Map.objects['A'].update_pieces([('empty', 'No one'), ('Workshop', 'cat'), ('Roost', 'bird')], soldiers, [("Sympathy", 1)])
    Map.objects['A'].update_owner()
    assert Map.objects['A'].owner == 'cat'
  
def test_default_map():
    map = build_regular_forest()