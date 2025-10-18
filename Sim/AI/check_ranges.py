"""
Check why no combat is happening
"""

from simulator import GameSimulator
from ai_agent import AIAgent

sim = GameSimulator(map_size=8)
state, engine = sim.setup_game()

print("Analyzing game setup...")
print("="*60)

p1_units = [u for u in state.units.values() if u.owner == 1 and u.is_alive()]
p2_units = [u for u in state.units.values() if u.owner == 2 and u.is_alive()]

print(f"\nPlayer 1 units: {len(p1_units)}")
for u in p1_units:
    print(f"  {u.name} at {u.position}")
    if u.weapons:
        for w in u.weapons:
            print(f"    {w.name}: Range={w.range}")

print(f"\nPlayer 2 units: {len(p2_units)}")
for u in p2_units:
    print(f"  {u.name} at {u.position}")

print(f"\nDistances between opposing units:")
for p1u in p1_units[:3]:
    for p2u in p2_units[:3]:
        dist = p1u.position.distance(p2u.position)
        print(f"  {p1u.name} to {p2u.name}: {dist} tiles")

print(f"\nChecking if any unit can see/shoot any enemy:")
for p1u in p1_units:
    if p1u.weapons:
        for weapon in p1u.weapons:
            targets = engine.get_valid_targets(p1u, weapon)
            print(f"  {p1u.name} {weapon.name} (R{weapon.range}): {len(targets)} targets")
            if targets:
                for t in targets:
                    print(f"    -> {t.name}")
