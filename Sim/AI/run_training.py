"""
Lead Ledger - Advanced Training Runner
Comprehensive training and testing with detailed logging
"""

from simulator import GameSimulator
from ai_agent import AIAgent
import os


def run_quick_training():
    """Quick training session - 10 games"""
    print("\n" + "="*60)
    print("QUICK TRAINING SESSION (10 games)")
    print("="*60)
    
    simulator = GameSimulator(map_size=8)
    results = simulator.run_training_session(num_games=10, verbose=False, save_logs=True)
    
    print_results_summary(results)


def run_standard_training():
    """Standard training session - 50 games"""
    print("\n" + "="*60)
    print("STANDARD TRAINING SESSION (50 games)")
    print("="*60)
    
    simulator = GameSimulator(map_size=8)
    results = simulator.run_training_session(num_games=50, verbose=False, save_logs=True)
    
    print_results_summary(results)


def run_extended_training():
    """Extended training session - 100 games"""
    print("\n" + "="*60)
    print("EXTENDED TRAINING SESSION (100 games)")
    print("="*60)
    
    simulator = GameSimulator(map_size=8)
    results = simulator.run_training_session(num_games=100, verbose=False, save_logs=True)
    
    print_results_summary(results)


def run_verbose_training():
    """Verbose training - detailed output for 5 games"""
    print("\n" + "="*60)
    print("VERBOSE TRAINING SESSION (5 games with full output)")
    print("="*60)
    
    simulator = GameSimulator(map_size=8)
    results = simulator.run_training_session(num_games=5, verbose=True, save_logs=True)
    
    print_results_summary(results)


def run_custom_training(num_games: int, map_size: int = 8, verbose: bool = False):
    """Custom training session"""
    print("\n" + "="*60)
    print(f"CUSTOM TRAINING SESSION ({num_games} games, map size {map_size})")
    print("="*60)
    
    simulator = GameSimulator(map_size=map_size)
    results = simulator.run_training_session(num_games=num_games, verbose=verbose, save_logs=True)
    
    print_results_summary(results)


def print_results_summary(results: dict):
    """Print formatted results summary"""
    print("\n" + "-"*60)
    print("SESSION COMPLETE")
    print("-"*60)
    print(f"Total Games:       {results['games_played']}")
    print(f"Player 1 Wins:     {results['p1_wins']:3d} ({results['p1_wins']/results['games_played']*100:5.1f}%)")
    print(f"Player 2 Wins:     {results['p2_wins']:3d} ({results['p2_wins']/results['games_played']*100:5.1f}%)")
    print(f"Ties:              {results['ties']:3d} ({results['ties']/results['games_played']*100:5.1f}%)")
    print(f"Avg Game Length:   {results['average_turns']:.1f} turns")
    print(f"\nAI 1 Win Rate:     {results['ai1_win_rate']:.2%}")
    print(f"AI 2 Win Rate:     {results['ai2_win_rate']:.2%}")
    print("-"*60)


def compare_strategies():
    """Run comparison of different AI strategies"""
    print("\n" + "="*60)
    print("STRATEGY COMPARISON")
    print("="*60)
    
    simulator = GameSimulator(map_size=8)
    
    # Create AIs with different weight profiles
    aggressive_ai = AIAgent(player_id=1)
    aggressive_ai.weights['eliminate_enemy'] = 150.0
    aggressive_ai.weights['damage_dealt'] = 100.0
    aggressive_ai.weights['capture_building'] = 50.0
    
    defensive_ai = AIAgent(player_id=2)
    defensive_ai.weights['eliminate_enemy'] = 60.0
    defensive_ai.weights['capture_building'] = 120.0
    defensive_ai.weights['building_control'] = 150.0
    
    print("\nAggressive AI vs Defensive AI (20 games)")
    print("Aggressive weights: eliminate=150, damage=100, capture=50")
    print("Defensive weights:  eliminate=60, capture=120, control=150")
    
    wins = {'aggressive': 0, 'defensive': 0, 'ties': 0}
    
    for i in range(20):
        result = simulator.run_game(aggressive_ai, defensive_ai, verbose=False)
        
        if result['winner'] == 1:
            wins['aggressive'] += 1
        elif result['winner'] == 2:
            wins['defensive'] += 1
        else:
            wins['ties'] += 1
    
    print("\nResults:")
    print(f"  Aggressive wins: {wins['aggressive']}/20 ({wins['aggressive']/20*100:.0f}%)")
    print(f"  Defensive wins:  {wins['defensive']}/20 ({wins['defensive']/20*100:.0f}%)")
    print(f"  Ties:            {wins['ties']}/20")


def main():
    """Main menu for training options"""
    print("="*60)
    print("LEAD LEDGER - AI TRAINING SYSTEM")
    print("="*60)
    print("\nAll results will be saved to the TestingResults folder")
    print("Each session creates:")
    print("  - Individual game logs (game_001.log, game_002.log, etc.)")
    print("  - Session summary (session_summary.txt)")
    print("  - JSON data file (session_data.json)")
    
    print("\n" + "="*60)
    print("TRAINING OPTIONS")
    print("="*60)
    print("1. Quick Training    (10 games)")
    print("2. Standard Training (50 games)")
    print("3. Extended Training (100 games)")
    print("4. Verbose Training  (5 games with detailed output)")
    print("5. Strategy Comparison (Aggressive vs Defensive)")
    print("6. Custom Training   (specify parameters)")
    print("0. Exit")
    
    try:
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == '1':
            run_quick_training()
        elif choice == '2':
            run_standard_training()
        elif choice == '3':
            run_extended_training()
        elif choice == '4':
            run_verbose_training()
        elif choice == '5':
            compare_strategies()
        elif choice == '6':
            num_games = int(input("Number of games: "))
            map_size = int(input("Map size (default 8): ") or "8")
            verbose = input("Verbose output? (y/n): ").lower() == 'y'
            run_custom_training(num_games, map_size, verbose)
        elif choice == '0':
            print("Exiting...")
            return
        else:
            print("Invalid option")
    
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
