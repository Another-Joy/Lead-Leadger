"""
Lead Ledger AI - Quick Start Example
Simple examples to get started with the AI system.
"""

from simulator import GameSimulator
from ai_agent import AIAgent


def example_1_quick_game():
    """Run a quick game between two AI players"""
    print("Example 1: Quick AI vs AI Game\n")
    
    # Create simulator
    sim = GameSimulator(map_size=8)
    
    # Create two AI players
    ai_player1 = AIAgent(player_id=1, difficulty="medium")
    ai_player2 = AIAgent(player_id=2, difficulty="medium")
    
    # Run a single game
    result = sim.run_game(ai_player1, ai_player2, max_turns=30, verbose=True)
    
    print("\n--- Final Result ---")
    print(f"Winner: Player {result['winner']}" if result['winner'] else "Tie!")
    print(f"Score: P1={result['final_scores'][1]}, P2={result['final_scores'][2]}")
    print(f"Turns: {result['turns_played']}")


def example_2_custom_armies():
    """Play with custom army compositions"""
    print("\nExample 2: Custom Armies\n")
    
    sim = GameSimulator()
    
    # Define custom armies
    tank_heavy_army = ["M24 Grizzly", "M29 Vindicator", "M14 Puma", "M24 Grizzly"]
    balanced_army = ["Rookie Squad", "Rookie Squad", "M24 Grizzly", "M14 Puma"]
    
    print(f"Army 1 (Tank Heavy): {tank_heavy_army}")
    print(f"Army 2 (Balanced): {balanced_army}\n")
    
    # Setup game with custom armies
    state, engine = sim.setup_game(army1=tank_heavy_army, army2=balanced_army)
    
    # Create AIs
    ai1 = AIAgent(player_id=1)
    ai2 = AIAgent(player_id=2)
    
    # Run game
    result = sim.run_game(ai1, ai2, max_turns=30, verbose=False)
    
    print(f"\nWinner: Player {result['winner']}" if result['winner'] else "\nTie!")
    print(f"Units left: P1={result['p1_units_remaining']}, P2={result['p2_units_remaining']}")


def example_3_training():
    """Train AI through multiple games"""
    print("\nExample 3: AI Training Session\n")
    
    sim = GameSimulator()
    
    print("Training AI through 50 games...")
    results = sim.run_training_session(num_games=50, verbose=False)
    
    print("\n--- Training Results ---")
    print(f"Total games: {results['games_played']}")
    print(f"Player 1 wins: {results['p1_wins']} ({results['p1_wins']/results['games_played']*100:.1f}%)")
    print(f"Player 2 wins: {results['p2_wins']} ({results['p2_wins']/results['games_played']*100:.1f}%)")
    print(f"Ties: {results['ties']}")
    print(f"Average game length: {results['average_turns']:.1f} turns")
    print(f"\nAI 1 learned win rate: {results['ai1_win_rate']:.1%}")
    print(f"AI 2 learned win rate: {results['ai2_win_rate']:.1%}")


def example_4_aggressive_ai():
    """Create a more aggressive AI by tuning weights"""
    print("\nExample 4: Aggressive vs Defensive AI\n")
    
    sim = GameSimulator()
    
    # Create aggressive AI (higher combat weights)
    aggressive_ai = AIAgent(player_id=1)
    aggressive_ai.weights['eliminate_enemy'] = 150.0
    aggressive_ai.weights['damage_dealt'] = 100.0
    aggressive_ai.weights['capture_building'] = 50.0
    
    # Create defensive AI (higher building control weights)
    defensive_ai = AIAgent(player_id=2)
    defensive_ai.weights['eliminate_enemy'] = 60.0
    defensive_ai.weights['damage_dealt'] = 40.0
    defensive_ai.weights['capture_building'] = 120.0
    defensive_ai.weights['building_control'] = 150.0
    
    print("Aggressive AI vs Defensive AI")
    print("\nAggressive weights:")
    print(f"  Eliminate: {aggressive_ai.weights['eliminate_enemy']}")
    print(f"  Damage: {aggressive_ai.weights['damage_dealt']}")
    print(f"  Capture: {aggressive_ai.weights['capture_building']}")
    
    print("\nDefensive weights:")
    print(f"  Eliminate: {defensive_ai.weights['eliminate_enemy']}")
    print(f"  Capture: {defensive_ai.weights['capture_building']}")
    print(f"  Control: {defensive_ai.weights['building_control']}")
    
    result = sim.run_game(aggressive_ai, defensive_ai, max_turns=30, verbose=False)
    
    print(f"\nWinner: Player {result['winner']}" if result['winner'] else "\nTie!")
    print(f"Final scores: P1={result['final_scores'][1]}, P2={result['final_scores'][2]}")


def example_5_step_by_step():
    """Step through a game manually"""
    print("\nExample 5: Manual Step-by-Step Game\n")
    
    from game_state import GameState
    from game_engine import GameEngine
    
    sim = GameSimulator()
    state, engine = sim.setup_game()
    
    ai1 = AIAgent(player_id=1)
    ai2 = AIAgent(player_id=2)
    
    print("Game initialized. Taking 5 turns manually...\n")
    
    for turn in range(5):
        current_ai = ai1 if state.active_player == 1 else ai2
        
        print(f"Turn {state.current_turn + 1}, Player {state.active_player}")
        
        # AI decides action
        action = current_ai.decide_action(state, engine)
        
        if action:
            print(f"  Action: {action['type']}")
            print(f"  Unit: {action.get('unit').name if action.get('unit') else 'N/A'}")
            
            # Execute action
            success = current_ai.execute_action(action, engine)
            print(f"  Result: {'✓' if success else '✗'}")
        else:
            print("  No action available")
        
        # Advance turn
        state.advance_turn()
        print()


if __name__ == "__main__":
    import sys
    
    examples = {
        '1': ("Quick AI vs AI Game", example_1_quick_game),
        '2': ("Custom Armies", example_2_custom_armies),
        '3': ("AI Training", example_3_training),
        '4': ("Aggressive vs Defensive", example_4_aggressive_ai),
        '5': ("Step-by-Step", example_5_step_by_step),
    }
    
    print("=" * 60)
    print("Lead Ledger AI - Quick Start Examples")
    print("=" * 60)
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run all examples")
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nSelect example (0-5): ").strip()
    
    print()
    
    if choice == '0':
        for key, (name, func) in examples.items():
            print("\n" + "=" * 60)
            func()
    elif choice in examples:
        examples[choice][1]()
    else:
        print("Invalid choice!")
