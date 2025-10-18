"""
Quick test to see if combat is happening
"""

from simulator import GameSimulator
from ai_agent import AIAgent

print("Testing AI combat behavior...")
print("="*60)

sim = GameSimulator(map_size=8)

# Create more aggressive AIs
ai1 = AIAgent(player_id=1)
ai2 = AIAgent(player_id=2)

# Boost combat weights
for ai in [ai1, ai2]:
    ai.weights['damage_dealt'] = 150.0
    ai.weights['eliminate_enemy'] = 150.0
    ai.weights['position_advantage'] = 30.0

print(f"\nAI Weights adjusted:")
print(f"  damage_dealt: {ai1.weights['damage_dealt']}")
print(f"  eliminate_enemy: {ai1.weights['eliminate_enemy']}")
print(f"  position_advantage: {ai1.weights['position_advantage']}")

# Run a short game with verbose output
print("\n" + "="*60)
print("Running test game (10 turns)...")
print("="*60)

result = sim.run_game(ai1, ai2, max_turns=10, verbose=True)

print("\n" + "="*60)
print("Final Results:")
print("="*60)
print(f"Winner: Player {result['winner']}" if result['winner'] else "Tie")
print(f"Turns: {result['turns_played']}")
print(f"P1 units: {result['p1_units_remaining']}")
print(f"P2 units: {result['p2_units_remaining']}")
print(f"Scores: P1={result['final_scores'][1]}, P2={result['final_scores'][2]}")
