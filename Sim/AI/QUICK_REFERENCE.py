"""
Lead Ledger AI - Quick Reference Card
Essential commands and patterns for using the AI system.
"""

# ============================================================================
# QUICK START COMMANDS
# ============================================================================

# Run test suite
python test_ai.py

# Run training session
python simulator.py

# Run examples interactively
python examples.py

# ============================================================================
# COMMON PATTERNS
# ============================================================================

# Pattern 1: Simple Training
from simulator import GameSimulator
sim = GameSimulator()
results = sim.run_training_session(num_games=50, verbose=False)

# Pattern 2: Single Game with Verbose Output
from simulator import GameSimulator
from ai_agent import AIAgent

sim = GameSimulator()
ai1 = AIAgent(player_id=1)
ai2 = AIAgent(player_id=2)
result = sim.run_game(ai1, ai2, verbose=True)

# Pattern 3: Custom Armies
sim = GameSimulator()
army1 = ["Rookie Squad", "M24 Grizzly", "M14 Puma"]
army2 = ["M29 Vindicator", "M24 Grizzly", "M14 Puma"]
state, engine = sim.setup_game(army1=army1, army2=army2)
result = sim.run_game(ai1, ai2)

# Pattern 4: Tune AI Behavior
ai = AIAgent(player_id=1)
ai.weights['eliminate_enemy'] = 150.0      # More aggressive
ai.weights['capture_building'] = 100.0     # Focus on objectives
ai.weights['health_preservation'] = 80.0   # More cautious

# Pattern 5: Manual Game Control
sim = GameSimulator()
state, engine = sim.setup_game()
ai = AIAgent(player_id=1)

for _ in range(10):  # 10 turns
    action = ai.decide_action(state, engine)
    if action:
        ai.execute_action(action, engine)
    state.advance_turn()

# ============================================================================
# AVAILABLE UNITS (Ordax Regiment)
# ============================================================================

units = {
    "Rookie Squad": {
        "cost": 20,
        "role": "Infantry/Capture",
        "stats": "M2 A:N C2 H4",
        "weapon": "5.56mm (R2, Assault)"
    },
    "M14 Puma": {
        "cost": 50,
        "role": "Light Tank/Anti-Armor",
        "stats": "M3 A:L C0 H3",
        "weapon": "105mm HEAT (R2, Assault)"
    },
    "M24 Grizzly": {
        "cost": 45,
        "role": "IFV/Anti-Infantry",
        "stats": "M2 A:M C0 H4",
        "weapons": "50mm AC + 7.62mm MG (R2, Linked)"
    },
    "M29 Vindicator": {
        "cost": 60,
        "role": "Tank Destroyer",
        "stats": "M2 A:M C0 H2",
        "weapon": "130mm APFSDS (R5, Long, Frontal)"
    }
}

# ============================================================================
# AI WEIGHT REFERENCE
# ============================================================================

default_weights = {
    'eliminate_enemy': 100.0,      # Priority to destroy enemy units
    'capture_building': 80.0,      # Priority to capture buildings
    'protect_unit': 70.0,          # Priority to preserve own units
    'position_advantage': 50.0,    # Priority to gain good positions
    'damage_dealt': 60.0,          # Priority to deal damage
    'health_preservation': 40.0,   # Priority to keep units healthy
    'building_control': 90.0,      # Priority to control buildings
}

# Aggressive AI preset
aggressive = {
    'eliminate_enemy': 150.0,
    'damage_dealt': 120.0,
    'capture_building': 50.0,
    'health_preservation': 30.0,
}

# Defensive/Objective AI preset
defensive = {
    'eliminate_enemy': 60.0,
    'capture_building': 130.0,
    'building_control': 150.0,
    'protect_unit': 100.0,
}

# ============================================================================
# KEY CLASSES & METHODS
# ============================================================================

# GameState - Main game state
state = GameState(map_size=8)
state.units          # Dict of all units
state.buildings      # Dict of all buildings
state.current_turn   # Current turn number
state.active_player  # 1 or 2
state.is_game_over() # Check if game ended
state.get_winner()   # Get winner (or None)

# GameEngine - Execute actions
engine = GameEngine(state)
engine.execute_move(unit, target_pos)
engine.execute_salvo(shooter, {weapon.name: target})
engine.execute_capture(unit)
engine.get_valid_moves(unit)
engine.get_valid_targets(unit, weapon)

# AIAgent - AI player
ai = AIAgent(player_id=1, difficulty="medium")
ai.decide_action(state, engine)  # Returns action dict
ai.execute_action(action, engine)  # Executes action
ai.take_turn(state, engine)  # Complete turn
ai.weights  # Modify decision weights
ai.win_rate  # Check learning progress

# GameSimulator - Run games
sim = GameSimulator(map_size=8)
sim.setup_game(army1, army2, map_setup)
sim.run_game(ai1, ai2, max_turns=50, verbose=True)
sim.run_training_session(num_games=100, verbose=False)

# ============================================================================
# DEBUGGING & ANALYSIS
# ============================================================================

# Print game state
print(f"Turn: {state.current_turn}, Player: {state.active_player}")
print(f"Score: {state.scores}")
print(f"Units: P1={len([u for u in state.units.values() if u.owner==1])}")

# Print unit info
for unit in state.units.values():
    if unit.is_alive() and unit.owner == 1:
        print(f"{unit.name} at {unit.position}, HP:{unit.current_health}/{unit.max_health}")

# Print building control
for pos, building in state.buildings.items():
    print(f"Building at {pos}: N={building.neutral_pips}, "
          f"P1={building.player1_pips}, P2={building.player2_pips}")

# Check AI decision without executing
action = ai.decide_action(state, engine)
if action:
    print(f"AI wants to: {action['type']} with {action['unit'].name}")

# Evaluate position value
from game_state import HexCoord
pos = HexCoord(0, 0)
value = ai.evaluate_position(pos, unit, state)
print(f"Position value: {value}")

# ============================================================================
# TIPS & TRICKS
# ============================================================================

# 1. Speed up training: reduce max_turns
results = sim.run_training_session(num_games=100, verbose=False)

# 2. Make AI more random (exploration)
ai.randomize_weights(variance=0.2)  # 20% variance

# 3. Clone state for lookahead
future_state = state.clone()
# Try actions on future_state without affecting real game

# 4. Check if action would be valid before deciding
can_move, reason = engine.can_move(unit, target_pos)
if can_move:
    engine.execute_move(unit, target_pos)

# 5. Get all possible targets for a unit
for weapon in unit.weapons:
    targets = engine.get_valid_targets(unit, weapon)
    print(f"{weapon.name} can target {len(targets)} enemies")

# ============================================================================
# COMMON ISSUES & SOLUTIONS
# ============================================================================

# Issue: Games ending in ties
# Solution: Increase game length or make AI more aggressive
ai.weights['damage_dealt'] = 150.0
ai.weights['eliminate_enemy'] = 150.0

# Issue: AI not capturing buildings
# Solution: Increase building control weights
ai.weights['capture_building'] = 150.0
ai.weights['building_control'] = 150.0

# Issue: Units not moving
# Solution: Check movement restrictions and valid moves
valid_moves = engine.get_valid_moves(unit)
print(f"Unit can move to {len(valid_moves)} positions")

# Issue: Want to see what AI is thinking
# Solution: Use verbose mode and check decide_action
action = ai.decide_action(state, engine)
print(f"Best action: {action}")
result = sim.run_game(ai1, ai2, verbose=True)
