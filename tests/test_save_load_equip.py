from player import Player
from inventory import Inventory
from items import generate_equipment
import save_system

# Создаём игрока и инвентарь
player = Player('Tester', class_id=None)
player.gold = 500
inv = Inventory(max_size=10)

# Сгенерируем оружие и добавим в инвентарь
w = generate_equipment('iron_sword', rotation=0, player_level=1, quality='iron', item_level=1)
inv.add_item(w)
# Экипируем его
w.equipped = True
player.weapon = w

# Добавим камень улучшения
from items import Item
stone = Item('upgrade_stone', 'Material', 0)
inv.add_item(stone)

print('Before save:')
print('Player weapon uid:', getattr(player.weapon, 'uid', None), 'equipped:', getattr(player.weapon, 'equipped', None))
for i,it in enumerate(inv.items):
    print(i, it.name, getattr(it,'uid',None), getattr(it,'equipped',None))

ok, msg = save_system.save_game(player, inv, rotation=0, victories=0)
print('Save:', ok, msg)

res, msg = save_system.load_game()
print('Load result message:', msg)
if res:
    player2, inv2, rotation2, vic2 = res
    print('After load:')
    print('Player weapon:', getattr(player2.weapon,'name',None), 'uid:', getattr(player2.weapon,'uid',None))
    for i,it in enumerate(inv2.items):
        print(i, it.name, getattr(it,'uid',None), getattr(it,'equipped',None))
else:
    print('Load failed')
