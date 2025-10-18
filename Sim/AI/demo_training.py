"""
Demo: Show the complete training and logging system
"""

from simulator import GameSimulator

print("="*70)
print("LEAD LEDGER AI TRAINING - DEMO")
print("="*70)

print("\nThis demo will:")
print("  1. Run 5 training games")
print("  2. Save detailed logs to TestingResults folder")
print("  3. Generate summary reports")
print("  4. Show you where to find the results")

input("\nPress Enter to start...")

# Run training
print("\n" + "="*70)
print("Running training session...")
print("="*70)

sim = GameSimulator(map_size=8)
results = sim.run_training_session(num_games=5, verbose=False, save_logs=True)

# Show results
print("\n" + "="*70)
print("TRAINING COMPLETE!")
print("="*70)

print(f"\nGames Played:      {results['games_played']}")
print(f"Player 1 Wins:     {results['p1_wins']} ({results['p1_wins']/results['games_played']*100:.0f}%)")
print(f"Player 2 Wins:     {results['p2_wins']} ({results['p2_wins']/results['games_played']*100:.0f}%)")
print(f"Ties:              {results['ties']} ({results['ties']/results['games_played']*100:.0f}%)")
print(f"Avg Game Length:   {results['average_turns']:.1f} turns")

print(f"\nAI 1 Win Rate:     {results['ai1_win_rate']:.1%}")
print(f"AI 2 Win Rate:     {results['ai2_win_rate']:.1%}")

print("\n" + "="*70)
print("FILES CREATED:")
print("="*70)

session_folder = f"TestingResults/session_{results['session_id']}"
print(f"\nSession Folder: {session_folder}")
print(f"\nContains:")
print(f"  • game_001.log through game_005.log - Individual game logs")
print(f"  • session_summary.txt - Human-readable summary")
print(f"  • session_data.json - Machine-readable data")

print("\n" + "="*70)
print("QUICK LOOK AT FINAL AI WEIGHTS:")
print("="*70)

print("\nAI 1 Weights:")
for key, value in sorted(results['ai1_final_weights'].items())[:4]:
    print(f"  {key:25s}: {value:6.1f}")

print("\nAI 2 Weights:")
for key, value in sorted(results['ai2_final_weights'].items())[:4]:
    print(f"  {key:25s}: {value:6.1f}")

print("\n" + "="*70)
print(f"✓ Demo complete! Check {session_folder} for full logs")
print("="*70)
