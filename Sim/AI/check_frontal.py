"""
Debug frontal arc issues
"""

from simulator import GameSimulator

sim = GameSimulator(map_size=8)
state, engine = sim.setup_game()

p1_units = [u for u in state.units.values() if u.owner == 1 and u.is_alive()]

print("Testing all Player 1 units:")
for unit in p1_units:
    for weapon in unit.weapons:
        targets = state.get_units_in_range(unit, weapon)
        print(f"\n{unit.name} at {unit.position}, facing {unit.orientation}")
        print(f"  Weapon: {weapon.name} (Range {weapon.range}, Keywords: {weapon.keywords})")
        print(f"  Targets in range: {len(targets)}")
        for target in targets:
            print(f"    - {target.name} at {target.position}")
