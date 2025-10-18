"""
Lead Ledger AI - Detailed Debug Script
Shows complete information about AI decisions and actions.
"""

from simulator import GameSimulator
from ai_agent import AIAgent
from game_state import GameState
from game_engine import GameEngine


def debug_single_turn():
    """Debug a single turn with complete detail"""
    print("=" * 80)
    print("DETAILED AI DECISION DEBUG")
    print("=" * 80)
    
    sim = GameSimulator(map_size=8)
    state, engine = sim.setup_game()
    
    ai1 = AIAgent(player_id=1)
    ai2 = AIAgent(player_id=2)
    
    # Run first few turns with extreme detail
    for turn_num in range(5):
        current_ai = ai1 if state.active_player == 1 else ai2
        
        print(f"\n{'='*80}")
        print(f"TURN {state.current_turn + 1} - PLAYER {state.active_player}")
        print(f"{'='*80}")
        
        # Show unit status
        my_units = [u for u in state.units.values() 
                   if u.owner == state.active_player and u.is_alive()]
        enemy_units = [u for u in state.units.values() 
                      if u.owner != state.active_player and u.is_alive()]
        
        print(f"\nMy Units ({len(my_units)}):")
        for u in my_units[:3]:
            print(f"  - {u.name} at {u.position}")
            print(f"    HP: {u.current_health}/{u.max_health}, M: {u.movement}")
            print(f"    Weapons: {[w.name for w in u.weapons]}")
            if u.weapons:
                for weapon in u.weapons:
                    targets = engine.get_valid_targets(u, weapon)
                    print(f"      {weapon.name}: {len(targets)} targets in range")
                    if targets:
                        for t in targets[:2]:
                            distance = u.position.distance(t.position)
                            print(f"        -> {t.name} at distance {distance}")
        
        print(f"\nEnemy Units ({len(enemy_units)}):")
        for u in enemy_units[:3]:
            print(f"  - {u.name} at {u.position}, HP: {u.current_health}/{u.max_health}")
        
        # Show buildings
        print(f"\nBuildings ({len(state.buildings)}):")
        for pos, building in list(state.buildings.items())[:3]:
            my_pips = building.get_control_value(state.active_player)
            enemy_pips = building.get_control_value(2 if state.active_player == 1 else 1)
            print(f"  - At {pos}: Neutral={building.neutral_pips}, "
                  f"Mine={my_pips}, Enemy={enemy_pips}")
        
        print(f"\nActions Available:")
        print(f"  Major: {state.major_action_available}")
        print(f"  Minor: {state.minor_action_available}")
        
        # MAJOR ACTION
        if state.major_action_available:
            print(f"\n--- EVALUATING MAJOR ACTION ---")
            action = current_ai.decide_action(state, engine)
            
            if action:
                print(f"\n✓ Selected Action: {action['type'].upper()}")
                unit = action.get('unit')
                
                if unit:
                    print(f"  Unit: {unit.name} at {unit.position}")
                    print(f"  HP: {unit.current_health}/{unit.max_health}")
                
                if action['type'] == 'advance':
                    path = action.get('path', [])
                    print(f"  Path: {' -> '.join(str(p) for p in path)}")
                    
                elif action['type'] == 'salvo':
                    weapon = action.get('weapon')
                    target = action.get('target')
                    if weapon and target:
                        print(f"  Weapon: {weapon.name} (Range: {weapon.range})")
                        print(f"  Target: {target.name} at {target.position}")
                        print(f"  Distance: {unit.position.distance(target.position)}")
                        print(f"  Target Armor: {target.armor.value}")
                        
                        # Show penetration requirements
                        pen_req = weapon.penetration.get(target.armor.value, "NA")
                        print(f"  Penetration needed: {pen_req}")
                        
                        # Check LoS
                        has_los = state.has_line_of_sight(unit.position, target.position, unit.owner)
                        print(f"  Line of Sight: {has_los}")
                
                elif action['type'] == 'capture':
                    building = state.buildings.get(unit.position)
                    if building:
                        print(f"  Building pips: N={building.neutral_pips}, "
                              f"P1={building.player1_pips}, P2={building.player2_pips}")
                        print(f"  Capture strength: {unit.control}")
                
                # Execute action
                print(f"\n  Executing...")
                success = current_ai.execute_action(action, engine)
                print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
                
                # Show results for combat
                if action['type'] == 'salvo':
                    target = action.get('target')
                    if target:
                        print(f"  Target health after: {target.current_health}/{target.max_health}")
            else:
                print("\n✗ No major action chosen")
        
        # MINOR ACTION
        if state.minor_action_available:
            print(f"\n--- EVALUATING MINOR ACTION ---")
            action = current_ai.decide_action(state, engine)
            
            if action:
                print(f"\n✓ Selected Action: {action['type'].upper()}")
                unit = action.get('unit')
                
                if unit:
                    print(f"  Unit: {unit.name} at {unit.position}")
                
                if action['type'] == 'minor_shot':
                    weapon = action.get('weapon')
                    target = action.get('target')
                    if weapon and target:
                        print(f"  Weapon: {weapon.name}")
                        print(f"  Target: {target.name}")
                        print(f"  Distance: {unit.position.distance(target.position)}")
                
                elif action['type'] == 'minor_move':
                    target_pos = action.get('target_pos')
                    print(f"  From: {unit.position} -> To: {target_pos}")
                
                elif action['type'] == 'control':
                    building = state.buildings.get(unit.position)
                    if building:
                        print(f"  Building pips before: N={building.neutral_pips}, "
                              f"P1={building.player1_pips}, P2={building.player2_pips}")
                
                # Execute action
                print(f"\n  Executing...")
                success = current_ai.execute_action(action, engine)
                print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
                
                if action['type'] == 'control':
                    building = state.buildings.get(unit.position)
                    if building:
                        print(f"  Building pips after: N={building.neutral_pips}, "
                              f"P1={building.player1_pips}, P2={building.player2_pips}")
            else:
                print("\n✗ No minor action chosen")
        
        # Advance turn
        state.advance_turn()
        
        print("\n" + "="*80)
        input("Press Enter for next turn...")


def analyze_ai_weights():
    """Analyze what the AI is prioritizing"""
    print("\n" + "=" * 80)
    print("AI WEIGHT ANALYSIS")
    print("=" * 80)
    
    ai = AIAgent(player_id=1)
    
    print("\nCurrent AI Weights:")
    for key, value in sorted(ai.weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {key:.<30} {value:>6.1f}")
    
    print("\nThis means the AI prioritizes (highest to lowest):")
    sorted_weights = sorted(ai.weights.items(), key=lambda x: x[1], reverse=True)
    for i, (key, value) in enumerate(sorted_weights, 1):
        print(f"  {i}. {key}")


def test_combat_system():
    """Test if combat is working at all"""
    print("\n" + "=" * 80)
    print("COMBAT SYSTEM TEST")
    print("=" * 80)
    
    from game_state import Unit, Weapon, ArmorType, HexCoord
    
    # Create test units
    attacker_weapon = Weapon(
        name="Test Cannon",
        range=3,
        penetration={"N": "3+", "L": "6+", "M": "9+", "H": "NA"},
        fortification_damage=1,
        keywords=[]
    )
    
    attacker = Unit(
        unit_id="test_attacker",
        name="Test Attacker",
        movement=2,
        armor=ArmorType.MEDIUM,
        control=0,
        health=5,
        max_health=5,
        weapons=[attacker_weapon],
        abilities=[],
        tags=["Vehicle"],
        position=HexCoord(0, 0),
        owner=1
    )
    
    target = Unit(
        unit_id="test_target",
        name="Test Target",
        movement=2,
        armor=ArmorType.LIGHT,
        control=0,
        health=3,
        max_health=3,
        weapons=[],
        abilities=[],
        tags=["Vehicle"],
        position=HexCoord(2, 0),
        owner=2
    )
    
    # Create minimal game state
    state = GameState(map_size=8)
    state.units[attacker.unit_id] = attacker
    state.units[target.unit_id] = target
    state.active_player = 1
    
    engine = GameEngine(state)
    
    print(f"\nAttacker: {attacker.name} at {attacker.position}")
    print(f"  Weapon: {attacker_weapon.name}")
    print(f"  Range: {attacker_weapon.range}")
    print(f"  Penetration vs Light: {attacker_weapon.penetration['L']}")
    
    print(f"\nTarget: {target.name} at {target.position}")
    print(f"  Armor: {target.armor.value}")
    print(f"  Health: {target.current_health}/{target.max_health}")
    print(f"  Distance: {attacker.position.distance(target.position)}")
    
    # Check if target is in range
    targets_in_range = engine.get_valid_targets(attacker, attacker_weapon)
    print(f"\n✓ Targets in range: {len(targets_in_range)}")
    if targets_in_range:
        print(f"  - {targets_in_range[0].name}")
    
    # Try to shoot
    print(f"\nAttempting shot...")
    success, msg = engine.execute_shot(attacker, attacker_weapon, target, is_minor=False)
    print(f"Result: {msg}")
    print(f"Target health after: {target.current_health}/{target.max_health}")
    
    # Try salvo
    print(f"\nAttempting salvo...")
    state.major_action_available = True
    results = engine.execute_salvo(attacker, {attacker_weapon.name: target})
    for weapon_name, success, msg in results:
        print(f"  {weapon_name}: {msg}")
    print(f"Target health after: {target.current_health}/{target.max_health}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LEAD LEDGER AI DEBUG SUITE" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")
    
    choice = input("""
Select debug mode:
1. Detailed single turn walkthrough
2. AI weight analysis
3. Combat system test
4. All tests

Choice (1-4): """).strip()
    
    if choice == '1':
        debug_single_turn()
    elif choice == '2':
        analyze_ai_weights()
    elif choice == '3':
        test_combat_system()
    elif choice == '4':
        analyze_ai_weights()
        test_combat_system()
        input("\nPress Enter to start turn-by-turn debug...")
        debug_single_turn()
    else:
        print("Invalid choice")
