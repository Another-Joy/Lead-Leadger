# Lead Ledger AI - Summary of Changes

## ✅ What Was Added

### 1. Comprehensive Logging System

**New Features:**
- Automatic creation of `TestingResults` folder
- Session-based organization with timestamps
- Individual game logs for every game played
- Session summary files (human-readable .txt and machine-readable .json)

**File Structure:**
```
TestingResults/
├── session_20251016_163315/
│   ├── game_001.log          # Turn-by-turn game record
│   ├── game_002.log
│   ├── game_003.log
│   ├── ...
│   ├── session_summary.txt   # Overall statistics
│   └── session_data.json     # Data for analysis
```

### 2. Enhanced Training Functions

**Modified `simulator.py`:**
- Added `log_file` parameter to `run_game()`
- Added `save_logs` parameter to `run_training_session()`
- New `_save_session_summary()` method for comprehensive reports
- Automatic timestamp-based session naming

**New `run_training.py`:**
- Interactive menu with 6 training options
- Quick (10), Standard (50), Extended (100) training modes
- Verbose mode for detailed output
- Strategy comparison mode
- Custom training parameters

**Demo Scripts:**
- `test_logging.py` - Quick test of logging
- `demo_training.py` - Full demonstration with explanations

### 3. Documentation

**New `TRAINING_GUIDE.md`:**
- Complete explanation of how AI learning works
- Detailed guide to training results
- Usage examples
- Troubleshooting tips
- Future improvement suggestions

---

## 📊 Understanding AI Learning

### How It Works (Simple Explanation)

1. **Weights**: AI has 7 strategic priorities (weights) like "eliminate enemy" or "capture buildings"
2. **Decision Making**: Every turn, AI evaluates all possible actions using these weights
3. **Win Rate**: After each game, AI tracks if it won or lost
4. **Exploration**: Every 20 games, AI randomly tweaks its weights by ±5%
5. **Evolution**: Over many games, successful weight combinations survive

### Current Storage

**In-Memory (lost when program ends):**
- Win rates
- Games played
- Current weights

**On-Disk (persistent):**
- Game logs in TestingResults folder
- Final weights in session_summary.txt
- Complete session data in JSON format

**⚠️ Important:** Learning doesn't automatically persist between sessions yet, but you can manually copy weights from session_summary.txt to restart with evolved weights.

---

## 🎮 How to Use

### Quick Start

```bash
# Run simple 10-game training
python simulator.py

# Run interactive menu
python run_training.py

# Run demo
python demo_training.py
```

### Example: Standard Training

```bash
python run_training.py
# Select option 2 (Standard Training - 50 games)
```

This will:
1. Create folder like `TestingResults/session_20251016_120000/`
2. Run 50 games between two AIs
3. Save individual logs for each game
4. Generate comprehensive summary files
5. Show final statistics

### Example: Verbose Mode

```python
from simulator import GameSimulator

sim = GameSimulator(map_size=8)
results = sim.run_training_session(
    num_games=5,
    verbose=True,      # Show every action
    save_logs=True     # Save to files
)
```

---

## 📁 What's in the Logs

### game_XXX.log

With `verbose=False` (default):
- Starting armies
- Turn markers
- Final results

With `verbose=True`:
- Every unit action
- Target selection
- Dice rolls and penetration checks
- Damage dealt
- Movement paths

### session_summary.txt

- Overall win/loss/tie statistics
- Average game length
- AI learning progress (win rates over time)
- Final AI weights after training
- Game-by-game results table

### session_data.json

Machine-readable format with:
- All statistics from summary
- Individual game results array
- Final AI weights as dictionary
- Ready for programmatic analysis

---

## 🔧 Key Files Modified

### simulator.py
- Added imports: `os`, `datetime`
- Modified `run_game()`: Added logging buffer and file writing
- Modified `run_training_session()`: Added session directory creation and summary generation
- New method `_save_session_summary()`: Writes comprehensive reports

### NEW FILES:
- `run_training.py` - Interactive training menu
- `test_logging.py` - Quick test script
- `demo_training.py` - Full demonstration
- `TRAINING_GUIDE.md` - Complete documentation

---

## 🎯 Next Steps

### To Run Training:

1. **Quick test**: `python demo_training.py`
2. **Standard training**: `python run_training.py` → Choose option 2
3. **Custom training**: Use the Custom option (#6) in run_training.py

### To Analyze Results:

1. Navigate to `TestingResults/session_XXXXXX/`
2. Open `session_summary.txt` for overview
3. Open `game_001.log` to see a specific game
4. Use `session_data.json` for programmatic analysis

### To Continue Learning:

Currently manual process:
1. Run training session
2. Note the final weights from session_summary.txt
3. Manually set those weights for next session:
   ```python
   ai = AIAgent(player_id=1)
   ai.weights['eliminate_enemy'] = 105.2  # from summary
   ai.weights['capture_building'] = 82.1  # from summary
   # etc.
   ```

---

## 📈 Example Output

```
Starting training session: 20251016_163315
Saving logs to: TestingResults/session_20251016_163315
============================================================

Session summary saved to: TestingResults/session_20251016_163315\session_summary.txt
Session data saved to: TestingResults/session_20251016_163315\session_data.json

------------------------------------------------------------
SESSION COMPLETE
------------------------------------------------------------
Total Games:       50
Player 1 Wins:      15 ( 30.0%)
Player 2 Wins:      12 ( 24.0%)
Ties:               23 ( 46.0%)
Avg Game Length:   42.3 turns

AI 1 Win Rate:     30.00%
AI 2 Win Rate:     24.00%
------------------------------------------------------------
```

---

## 🐛 Fixes Applied

Also fixed in this session:
- Line of Sight infinite loop bug (added loop prevention)
- Deployment zones now closer together (r=1 vs r=-1 for 2 tiles separation)
- Combat system fully functional with salvos and shots working

---

## ✨ Summary

You now have:
- ✅ Comprehensive logging to TestingResults folder
- ✅ Individual game logs for every match
- ✅ Session summaries with all statistics
- ✅ JSON data files for analysis
- ✅ Complete documentation in TRAINING_GUIDE.md
- ✅ Multiple ways to run training (simulator.py, run_training.py, demo)
- ✅ Understanding of how AI learning works

The AI learns through weight evolution and tracks win rates, with all results now permanently saved to disk for analysis!
