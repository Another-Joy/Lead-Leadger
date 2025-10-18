# Lead Ledger AI System

An AI system for the Lead Ledger tactical wargame that can learn and improve through self-play.

## Project Structure

```
AI/
├── game_state.py      # Core game state management and data structures
├── game_engine.py     # Game rules enforcement and action execution
├── ai_agent.py        # AI decision-making agent
├── unit_loader.py     # Unit datasheet loader from markdown files
├── simulator.py       # Game simulation and AI training system
└── README.md          # This file
```

## Features

### Two Operational Modes

1. **Self-Play Mode**: Two instances of the AI play against each other
   - Used for training and improvement through reinforcement learning
   - Both AIs learn from victories and defeats
   
2. **Single-Player Mode**: AI plays against a human or another opponent
   - Can use custom army lists
   - Accepts map configurations

### AI Capabilities

The AI can handle all aspects of the game:
- **Movement**: Infantry, vehicles, aircraft, and hover units with proper restrictions
- **Combat**: Weapon selection, target prioritization, penetration calculations
- **Building Control**: Capture and control strategic objectives
- **Action Economy**: Optimal use of Major and Minor actions
- **Strategic Planning**: Long-term position evaluation and objective control

### Learning System

- Weight-based decision making that adapts over time
- Win rate tracking for performance evaluation
- Exploratory weight randomization to discover new strategies
- Position value learning

## Usage

### Basic Training Session

```python
from simulator import GameSimulator

simulator = GameSimulator(map_size=8)
results = simulator.run_training_session(num_games=100, verbose=False)

print(f"Player 1 wins: {results['p1_wins']}")
print(f"Player 2 wins: {results['p2_wins']}")
```

### Single Game with Custom Armies

```python
from simulator import GameSimulator
from ai_agent import AIAgent

simulator = GameSimulator()

# Define custom armies
army1 = ["Rookie Squad", "Rookie Squad", "M24 Grizzly", "M14 Puma"]
army2 = ["Rookie Squad", "M29 Vindicator", "M24 Grizzly"]

# Create AI agents
ai1 = AIAgent(player_id=1)
ai2 = AIAgent(player_id=2)

# Set up game with custom armies
state, engine = simulator.setup_game(army1=army1, army2=army2)

# Run the game
result = simulator.run_game(ai1, ai2, verbose=True)
```

### Run from Command Line

```bash
python simulator.py
```

This will run a default training session with 10 games.

## Game Rules Implementation

The system implements the complete Lead Ledger ruleset:

### Movement Rules
- **Infantry**: Full freedom of movement
- **Vehicles**: Can turn once per movement, heavy vehicles must move-then-turn
- **Aircraft**: Must always move, cannot move backwards
- **Hover**: Full freedom of movement

### Combat System
- Line of sight checking (blocked by buildings and enemy units)
- Dice rolling (d12) with penetration checks
- Weapon keywords (Assault, Linked, Blast, Frontal, Precision, Long)
- Armor vs. ammunition effectiveness matrix

### Actions
- **Major Actions**: Advance, Salvo, Capture, Embark, Disembark
- **Minor Actions**: Move, Consolidate, Control, Shot
- **Special Actions**: Overwatch

### Victory Conditions
- Most points after 50 turns (scored from building control every 10 turns)
- Complete elimination of enemy forces

## Customization

### Adjusting AI Difficulty

Modify the weights in `AIAgent.__init__()`:

```python
self.weights = {
    'eliminate_enemy': 100.0,
    'capture_building': 80.0,
    'protect_unit': 70.0,
    # ... adjust these values
}
```

### Custom Map Setup

```python
from game_state import HexCoord, Building

# Define building positions
building_positions = [
    HexCoord(0, 0),
    HexCoord(3, 2),
    HexCoord(-2, 3)
]

# Define blocked tiles
blocked_tiles = {
    HexCoord(1, 1),
    HexCoord(-1, -1)
}

map_setup = (building_positions, blocked_tiles)
state, engine = simulator.setup_game(map_setup=map_setup)
```

## Future Enhancements

- Neural network-based decision making
- Monte Carlo Tree Search for action selection
- Replay system for analyzing AI decisions
- More sophisticated learning algorithms (Q-learning, Policy Gradient)
- Unit database expansion
- Multi-regiment support
- Advanced tactical patterns recognition

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

## Contributing

When adding new units, place markdown files in the `Units/[Regiment]/` directory following the standard format:

```markdown
| M   | A   | C   | H   |
| --- | --- | --- | --- |
| 2   | M   | 0   | 4   |

| Name      | R   | N   | L   | M   | H   | F   | Keywords |
| --------- | --- | --- | --- | --- | --- | --- | -------- |
| 50mm AC   | 2   | 4-  | 2+  | 10+ | NA  | 1   | Linked   |

Tags:
Vehicle, IFV
```

The system will automatically parse and load them.

## License

This is a game development project. Please respect the game creator's rights.
