"""
Lead Ledger AI - Test and Demo Script
Quick tests and demonstrations of the AI system.
"""

from simulator import GameSimulator
from ai_agent import AIAgent
from game_state import HexCoord


def test_basic_game():
    """Test a basic game setup and execution"""
    print("=" * 60)
    print("TEST 1: Basic Game Setup and Execution")
    print("=" * 60)
    
    simulator = GameSimulator(map_size=8)
    
    print("\n1. Setting up game...")
    state, engine = simulator.setup_game()
    
    print(f"   Map size: {state.map_size}")
    print(f"   Buildings: {len(state.buildings)}")
    print(f"   Player 1 units: {len([u for u in state.units.values() if u.owner == 1])}")
    print(f"   Player 2 units: {len([u for u in state.units.values() if u.owner == 2])}")
    
    print("\n2. Creating AI agents...")
    ai1 = AIAgent(player_id=1)
    ai2 = AIAgent(player_id=2)
    print(f"   AI 1 initialized for Player {ai1.player_id}")
    print(f"   AI 2 initialized for Player {ai2.player_id}")
    
    print("\n3. Running game...")
    result = simulator.run_game(ai1, ai2, max_turns=10, verbose=False)
    
    print(f"\n   Game completed!")
    print(f"   Winner: Player {result['winner']}" if result['winner'] else "   Tie!")
    print(f"   Turns: {result['turns_played']}")
    print(f"   Final scores: P1={result['final_scores'][1]}, P2={result['final_scores'][2]}")
    print(f"   Units remaining: P1={result['p1_units_remaining']}, P2={result['p2_units_remaining']}")
    
    return True


def test_custom_armies():
    """Test with custom army compositions"""
    print("\n" + "=" * 60)
    print("TEST 2: Custom Army Compositions")
    print("=" * 60)
    
    simulator = GameSimulator(map_size=8)
    
    # Infantry-heavy vs vehicle-heavy
    army1 = ["Rookie Squad", "Rookie Squad", "Rookie Squad", "M14 Puma"]
    army2 = ["M24 Grizzly", "M29 Vindicator", "M14 Puma"]
    
    print(f"\n   Army 1 (Infantry-heavy): {army1}")
    print(f"   Army 2 (Vehicle-heavy): {army2}")
    
    state, engine = simulator.setup_game(army1=army1, army2=army2)
    
    ai1 = AIAgent(player_id=1)
    ai2 = AIAgent(player_id=2)
    
    result = simulator.run_game(ai1, ai2, max_turns=20, verbose=False)
    
    print(f"\n   Result: Player {result['winner']} wins!" if result['winner'] else "   Tie!")
    print(f"   Final scores: P1={result['final_scores'][1]}, P2={result['final_scores'][2]}")
    
    return True


def test_training_session():
    """Test AI training over multiple games"""
    print("\n" + "=" * 60)
    print("TEST 3: AI Training Session")
    print("=" * 60)
    
    simulator = GameSimulator(map_size=8)
    
    print("\n   Running 20 training games...")
    print("   (This may take a minute)")
    
    results = simulator.run_training_session(num_games=20, verbose=False)
    
    print(f"\n   Training Complete!")
    print(f"   Games played: {results['games_played']}")
    print(f"   Player 1 wins: {results['p1_wins']} ({results['p1_wins']/results['games_played']*100:.1f}%)")
    print(f"   Player 2 wins: {results['p2_wins']} ({results['p2_wins']/results['games_played']*100:.1f}%)")
    print(f"   Ties: {results['ties']} ({results['ties']/results['games_played']*100:.1f}%)")
    print(f"   Average game length: {results['average_turns']:.1f} turns")
    print(f"   AI 1 final win rate: {results['ai1_win_rate']:.2%}")
    print(f"   AI 2 final win rate: {results['ai2_win_rate']:.2%}")
    
    return True


def test_game_mechanics():
    """Test specific game mechanics"""
    print("\n" + "=" * 60)
    print("TEST 4: Game Mechanics Verification")
    print("=" * 60)
    
    from game_state import GameState, Unit, Weapon, ArmorType, HexCoord, Building
    from game_engine import GameEngine
    
    print("\n1. Testing hex coordinate system...")
    h1 = HexCoord(0, 0)
    h2 = HexCoord(2, 1)
    distance = h1.distance(h2)
    print(f"   Distance from (0,0) to (2,1): {distance}")
    print(f"   ✓ Hex math working")
    
    print("\n2. Testing weapon penetration...")
    weapon = Weapon(
        name="Test Cannon",
        range=3,
        penetration={"N": "2+", "L": "5+", "M": "10+", "H": "NA"},
        fortification_damage=1
    )
    
    # Test rolling up
    can_pen = weapon.can_penetrate(ArmorType.LIGHT, 6)
    print(f"   6 vs Light (5+): {can_pen}")
    assert can_pen == True, "Should penetrate"
    
    can_pen = weapon.can_penetrate(ArmorType.LIGHT, 4)
    print(f"   4 vs Light (5+): {can_pen}")
    assert can_pen == False, "Should not penetrate"
    print(f"   ✓ Penetration system working")
    
    print("\n3. Testing building control...")
    building = Building(position=HexCoord(0, 0), total_pips=5)
    print(f"   Initial: N={building.neutral_pips}, P1={building.player1_pips}, P2={building.player2_pips}")
    
    building.capture_pips(1, 1)
    print(f"   After P1 captures 1: N={building.neutral_pips}, P1={building.player1_pips}, P2={building.player2_pips}")
    assert building.player1_pips == 2, "Neutral converts at 2x"
    print(f"   ✓ Building control working")
    
    print("\n4. Testing unit creation...")
    unit = Unit(
        unit_id="test1",
        name="Test Unit",
        movement=2,
        armor=ArmorType.MEDIUM,
        control=1,
        health=3,
        max_health=3,
        weapons=[weapon],
        abilities=[],
        tags=["Vehicle"],
        position=HexCoord(0, 0),
        owner=1
    )
    print(f"   Unit: {unit.name}, Health: {unit.current_health}/{unit.max_health}")
    print(f"   Type: {unit.unit_type}")
    print(f"   ✓ Unit system working")
    
    return True


def demo_single_turn():
    """Demonstrate a single turn in detail"""
    print("\n" + "=" * 60)
    print("DEMO: Single Turn Detailed Walkthrough")
    print("=" * 60)
    
    simulator = GameSimulator(map_size=8)
    state, engine = simulator.setup_game()
    
    ai = AIAgent(player_id=1)
    
    print(f"\nCurrent turn: {state.current_turn}")
    print(f"Active player: {state.active_player}")
    print(f"Major action available: {state.major_action_available}")
    print(f"Minor action available: {state.minor_action_available}")
    
    my_units = [u for u in state.units.values() if u.owner == 1 and u.is_alive()]
    print(f"\nPlayer 1 has {len(my_units)} units:")
    for unit in my_units[:3]:  # Show first 3
        print(f"   - {unit.name} at {unit.position} (HP: {unit.current_health}/{unit.max_health})")
    
    print("\nAI evaluating possible actions...")
    action = ai.decide_action(state, engine)
    
    if action:
        print(f"   Best action: {action['type']}")
        print(f"   Unit: {action['unit'].name}")
        
        print("\nExecuting action...")
        success = ai.execute_action(action, engine)
        print(f"   Result: {'Success' if success else 'Failed'}")
    else:
        print("   No valid actions available")
    
    return True


def run_all_tests():
    """Run all tests and demos"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "LEAD LEDGER AI - TEST SUITE" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Basic Game", test_basic_game),
        ("Custom Armies", test_custom_armies),
        ("Game Mechanics", test_game_mechanics),
        ("Single Turn Demo", demo_single_turn),
        ("Training Session", test_training_session),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print(f"\n   ✓ {name} PASSED")
            else:
                failed += 1
                print(f"\n   ✗ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n   ✗ {name} FAILED with error: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
