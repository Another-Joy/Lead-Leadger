"""Quick test of logging system"""
from simulator import GameSimulator

print("Testing logging system...")
sim = GameSimulator(map_size=8)
results = sim.run_training_session(num_games=3, verbose=False, save_logs=True)

print("\n✓ Test complete!")
print(f"Check TestingResults folder for logs")
