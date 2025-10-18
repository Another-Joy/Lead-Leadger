"""
Debug LoS issues
"""

from simulator import GameSimulator

sim = GameSimulator(map_size=8)
state, engine = sim.setup_game()

p1_units = [u for u in state.units.values() if u.owner == 1 and u.is_alive()]
p2_units = [u for u in state.units.values() if u.owner == 2 and u.is_alive()]

# Find the M29 Vindicator  
vindicator = [u for u in p1_units if "Vindicator" in u.name][0]
weapon = vindicator.weapons[0]

print(f"Testing {vindicator.name} at {vindicator.position}")
print(f"Weapon: {weapon.name}, Range: {weapon.range}, Keywords: {weapon.keywords}")

effective_range = weapon.range
if "Long" in weapon.keywords:
    effective_range += 2
print(f"Effective range: {effective_range}")

print(f"\nChecking each enemy:")
for enemy in p2_units:
    dist = vindicator.position.distance(enemy.position)
    print(f"\n  {enemy.name} at {enemy.position}")
    print(f"    Distance: {dist}")
    print(f"    In range: {dist <= effective_range}")
    
    if dist <= effective_range:
        has_los = state.has_line_of_sight(vindicator.position, enemy.position, vindicator.owner)
        print(f"    Line of sight: {has_los}")
        
        if not has_los:
            print(f"    LOS blocked - checking why...")
            # Check what's blocking
            for building_pos in state.buildings.keys():
                # Simple check if building is between
                if building_pos != vindicator.position and building_pos != enemy.position:
                    d1 = vindicator.position.distance(building_pos)
                    d2 = enemy.position.distance(building_pos)
                    total = vindicator.position.distance(enemy.position)
                    if d1 + d2 <= total + 1:  # Rough check
                        print(f"      Building at {building_pos} might block")
