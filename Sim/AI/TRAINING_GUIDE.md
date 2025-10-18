# Lead Ledger AI Training System

## How the AI Learns

### Learning Mechanism

The AI uses a **genetic algorithm-inspired approach** with weight-based decision making:

1. **Initial State**: AI starts with default strategic weights (e.g., eliminate_enemy=100, capture_building=80)

2. **Game Evaluation**: After each action, the AI evaluates positions using these weights to decide its next move

3. **Win Rate Tracking**: After each game, the AI updates its running win rate:
   - Wins increase the rate: `win_rate = (old_rate * games + 1) / (games + 1)`
   - Losses decrease it: `win_rate = (old_rate * games) / (games + 1)`

4. **Exploration (Every 20 games)**: AI randomly adjusts each weight by ±5% to explore new strategies
   - Example: If `eliminate_enemy = 100`, it might become 95-105

5. **Evolution**: Over many games, AIs that find successful weight combinations maintain higher win rates

### Current Limitations

⚠️ **Learning is NOT persistent** - When the program ends, all learning is lost because:
- Weights are stored only in memory (AIAgent class)
- No save/load functionality exists yet
- Each session starts fresh with default weights

### Storage Locations

**In-Memory Only:**
- `AIAgent.win_rate` - Running average of wins (0.0 to 1.0)
- `AIAgent.games_played` - Total games played
- `AIAgent.weights` - Dictionary of strategic priorities
- `AIAgent.position_values` - Learned value map (currently unused)

**On-Disk (New):**
- Game logs in `TestingResults/session_TIMESTAMP/`
- Final weights saved in session_summary.txt
- Can be manually restored in future sessions

---

## Training Results & Logs

### Folder Structure

All training results are saved to the **`TestingResults`** folder:

```
TestingResults/
├── session_20251016_120000/
│   ├── game_001.log          # Individual game log
│   ├── game_002.log          # Individual game log
│   ├── game_003.log          # Individual game log
│   ├── ...
│   ├── session_summary.txt   # Human-readable summary
│   └── session_data.json     # Machine-readable data
├── session_20251016_140000/
│   └── ...
```

### File Contents

#### `game_XXX.log` - Individual Game Logs
Contains turn-by-turn record of a single game:
- Starting armies for both players
- Each turn's actions (when verbose=True)
- Final game result
- Units remaining

#### `session_summary.txt` - Training Summary
Human-readable overview including:
- Overall win/loss statistics
- Average game length
- AI learning progress (win rates)
- Final AI weights after training
- Game-by-game results table

#### `session_data.json` - Machine-Readable Data
JSON format for programmatic analysis:
- Complete session metadata
- Individual game results
- Final AI weights
- Win rates over time

---

## Running Training Sessions

### Quick Start

```bash
# Run default training (10 games)
python simulator.py

# Run interactive menu
python run_training.py
```

### Training Options

The `run_training.py` script provides multiple options:

1. **Quick Training** (10 games) - Fast test
2. **Standard Training** (50 games) - Good balance
3. **Extended Training** (100 games) - Deep learning
4. **Verbose Training** (5 games) - Full action logs
5. **Strategy Comparison** - Test different AI approaches
6. **Custom Training** - Specify your own parameters

### Programmatic Usage

```python
from simulator import GameSimulator

# Create simulator
sim = GameSimulator(map_size=8)

# Run training session
results = sim.run_training_session(
    num_games=50,        # Number of games
    verbose=False,       # Print detailed turn info
    save_logs=True       # Save to TestingResults folder
)

# Access results
print(f"P1 wins: {results['p1_wins']}")
print(f"P2 wins: {results['p2_wins']}")
print(f"AI 1 win rate: {results['ai1_win_rate']:.2%}")
```

### Verbose Mode

When `verbose=True`, game logs include:
- Every action taken by each AI
- Target selection reasoning
- Dice rolls and damage calculations
- Movement paths
- Special action triggers

When `verbose=False`, logs include only:
- Game start/end information
- Starting armies
- Final results

---

## Interpreting Results

### Win Rate

- **0% - 30%**: AI is struggling, may need weight adjustments
- **30% - 70%**: Balanced, competitive gameplay
- **70% - 100%**: Dominating strategy found

### Ties

High tie rates (>50%) may indicate:
- Turn limit reached before decisive victory
- Very defensive play styles
- Need for longer games or aggressive weights

### AI Weights

Key strategic parameters (default values):

- `eliminate_enemy: 100.0` - Priority to destroy enemy units
- `capture_building: 80.0` - Value of capturing objectives
- `building_control: 90.0` - Maintaining building control
- `damage_dealt: 60.0` - Importance of dealing damage
- `protect_unit: 70.0` - Keeping own units alive
- `position_advantage: 50.0` - Tactical positioning
- `health_preservation: 40.0` - Unit health management

Higher values = Higher priority in decision making

---

## Future Improvements

### Potential Enhancements:

1. **Persistent Learning**
   - Save/load AI weights to disk
   - Resume training sessions
   - Track long-term evolution

2. **Advanced Learning**
   - Reinforce successful action sequences
   - Learn from specific game situations
   - Position value learning (heatmaps)

3. **Analysis Tools**
   - Visualize weight evolution over time
   - Heatmaps of successful strategies
   - Automated strategy recommendations

4. **Matchmaking**
   - Rate AIs by strength (ELO system)
   - Tournament modes
   - Champion vs challenger system

---

## Examples

### Example 1: Quick Test

```python
from simulator import GameSimulator

sim = GameSimulator()
results = sim.run_training_session(num_games=5, verbose=True, save_logs=True)

print(f"Session saved to: TestingResults/session_{results['session_id']}")
```

### Example 2: Custom AI Weights

```python
from simulator import GameSimulator
from ai_agent import AIAgent

sim = GameSimulator()

# Create custom aggressive AI
aggressive = AIAgent(player_id=1)
aggressive.weights['eliminate_enemy'] = 150.0
aggressive.weights['damage_dealt'] = 120.0

# Create custom defensive AI  
defensive = AIAgent(player_id=2)
defensive.weights['building_control'] = 150.0
defensive.weights['protect_unit'] = 120.0

# Run matchup
result = sim.run_game(aggressive, defensive, verbose=True, 
                     log_file="TestingResults/custom_match.log")
```

### Example 3: Load Previous Weights

```python
# Manually set weights from a previous successful session
import json

# Load from previous session
with open("TestingResults/session_XXXXXX/session_data.json") as f:
    data = json.load(f)

ai = AIAgent(player_id=1)
ai.weights = data['ai1_final_weights']

# Continue training with these weights
# ...
```

---

## Troubleshooting

**Q: Logs are empty except for start/end?**  
A: Set `verbose=True` to see turn-by-turn actions

**Q: Games always end in ties?**  
A: Increase `max_turns` or adjust AI weights to be more aggressive

**Q: AI isn't learning?**  
A: Learning is gradual - run 50+ games. Also remember learning doesn't persist between program runs yet.

**Q: How do I compare two training sessions?**  
A: Compare the session_data.json files or session_summary.txt files

---

## Credits

Lead Ledger AI Training System  
Version 1.0 - October 2025
