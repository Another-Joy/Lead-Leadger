"""
Lead Ledger - AI Training and Simulation System
Manages AI training, self-play, and game simulation.
"""

import random
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from game_state import *
from game_engine import GameEngine
from ai_agent import AIAgent
from unit_loader import UnitLoader, ORDAX_UNITS


class ArmyBuilder:
    """Build armies for gameplay"""
    
    def __init__(self, unit_loader: UnitLoader):
        self.loader = unit_loader
    
    def create_balanced_army(self, player_id: int, points_budget: int = 200) -> List[Dict]:
        """Create a balanced army within points budget"""
        # Use hardcoded Ordax units for now
        available_units = [
            ("Rookie Squad", 20, "Infantry"),
            ("M14 Puma", 50, "Light Tank"),
            ("M24 Grizzly", 45, "IFV"),
            ("M29 Vindicator", 60, "Tank Destroyer"),
        ]
        
        army = []
        spent = 0
        
        # Ensure minimum 2 infantry units
        infantry_count = 0
        while infantry_count < 2 and spent + 20 <= points_budget:
            army.append({"name": "Rookie Squad", "type": "Infantry"})
            spent += 20
            infantry_count += 1
        
        # Fill rest with mixed units
        while spent < points_budget:
            # Randomly select unit that fits budget
            affordable = [(name, cost, type_) for name, cost, type_ in available_units 
                         if cost <= points_budget - spent]
            
            if not affordable:
                break
            
            unit_name, cost, unit_type = random.choice(affordable)
            army.append({"name": unit_name, "type": unit_type})
            spent += cost
        
        return army
    
    def create_army_from_list(self, army_list: List[str]) -> List[Dict]:
        """Create army from list of unit names"""
        return [{"name": name, "type": "Unknown"} for name in army_list]


class MapGenerator:
    """Generate game maps"""
    
    def __init__(self, map_size: int = 8):
        self.map_size = map_size
    
    def generate_basic_map(self) -> Tuple[List[HexCoord], Set[HexCoord]]:
        """Generate a basic map with buildings and obstacles"""
        buildings = []
        blocked = set()
        
        # Place 5-7 buildings randomly
        num_buildings = random.randint(5, 7)
        
        for _ in range(num_buildings):
            # Random position in middle area
            q = random.randint(-self.map_size // 2, self.map_size // 2)
            r = random.randint(-self.map_size // 2, self.map_size // 2)
            
            # Ensure in bounds
            if abs(q) + abs(r) <= self.map_size:
                pos = HexCoord(q, r)
                if pos not in buildings:
                    buildings.append(pos)
        
        # Place 3-5 blocked tiles
        num_blocked = random.randint(3, 5)
        
        for _ in range(num_blocked):
            q = random.randint(-self.map_size + 1, self.map_size - 1)
            r = random.randint(-self.map_size + 1, self.map_size - 1)
            
            if abs(q) + abs(r) <= self.map_size:
                pos = HexCoord(q, r)
                if pos not in buildings:
                    blocked.add(pos)
        
        return buildings, blocked
    
    def get_deployment_zone(self, player: int, map_size: int) -> List[HexCoord]:
        """Get deployment zone hexes for a player"""
        zone = []
        
        # Much tighter deployment zones - only 4 tiles from center
        if player == 1:
            # Southern side - closer to center
            for q in range(-map_size, map_size + 1):
                for r in range(max(-map_size, -q - map_size), min(map_size, -q + map_size) + 1):
                    # Deploy in rows 2-4 from center (much closer)
                    if 2 <= r <= 4:
                        zone.append(HexCoord(q, r))
        else:
            # Northern side - closer to center  
            for q in range(-map_size, map_size + 1):
                for r in range(max(-map_size, -q - map_size), min(map_size, -q + map_size) + 1):
                    # Deploy in rows -4 to -2 from center (much closer)
                    if -4 <= r <= -2:
                        zone.append(HexCoord(q, r))
        
        return zone


class GameSimulator:
    """Simulate complete games"""
    
    def __init__(self, map_size: int = 8):
        self.map_size = map_size
        self.unit_loader = UnitLoader()
        self.army_builder = ArmyBuilder(self.unit_loader)
        self.map_generator = MapGenerator(map_size)
        
        # Try to load units from files
        try:
            self.unit_loader.load_all_regiments()
        except:
            print("Could not load units from files, using hardcoded data")
    
    def setup_game(self, army1: Optional[List[str]] = None, 
                   army2: Optional[List[str]] = None,
                   map_setup: Optional[Tuple] = None) -> Tuple[GameState, GameEngine]:
        """Set up a new game"""
        state = GameState(self.map_size)
        
        # Generate or use provided map
        if map_setup:
            building_positions, blocked_tiles = map_setup
        else:
            building_positions, blocked_tiles = self.map_generator.generate_basic_map()
        
        # Create buildings
        for pos in building_positions:
            state.buildings[pos] = Building(position=pos, total_pips=random.randint(3, 6))
        
        state.blocked_tiles = blocked_tiles
        
        # Create armies
        if not army1:
            army1_list = self.army_builder.create_balanced_army(1)
        else:
            army1_list = self.army_builder.create_army_from_list(army1)
        
        if not army2:
            army2_list = self.army_builder.create_balanced_army(2)
        else:
            army2_list = self.army_builder.create_army_from_list(army2)
        
        # Deploy units
        p1_zone = self.map_generator.get_deployment_zone(1, self.map_size)
        p2_zone = self.map_generator.get_deployment_zone(2, self.map_size)
        
        # Player 1 deployment
        for i, unit_info in enumerate(army1_list):
            unit_name = unit_info["name"]
            
            # Get unit data
            if unit_name in ORDAX_UNITS:
                unit_data = ORDAX_UNITS[unit_name]
            else:
                continue
            
            # Find deployment position
            if i < len(p1_zone):
                pos = p1_zone[i]
            else:
                pos = random.choice(p1_zone)
            
            # Create unit
            unit_id = f"p1_unit_{i}"
            unit = self._create_unit_from_data(unit_id, unit_name, unit_data, 1, pos)
            state.units[unit_id] = unit
        
        # Player 2 deployment
        for i, unit_info in enumerate(army2_list):
            unit_name = unit_info["name"]
            
            if unit_name in ORDAX_UNITS:
                unit_data = ORDAX_UNITS[unit_name]
            else:
                continue
            
            if i < len(p2_zone):
                pos = p2_zone[i]
            else:
                pos = random.choice(p2_zone)
            
            unit_id = f"p2_unit_{i}"
            unit = self._create_unit_from_data(unit_id, unit_name, unit_data, 2, pos)
            state.units[unit_id] = unit
        
        state.phase = "main"
        engine = GameEngine(state)
        
        return state, engine
    
    def _create_unit_from_data(self, unit_id: str, name: str, data: Dict, 
                               owner: int, position: HexCoord) -> Unit:
        """Create unit from data dictionary"""
        armor_map = {
            'N': ArmorType.NONE,
            'L': ArmorType.LIGHT,
            'M': ArmorType.MEDIUM,
            'H': ArmorType.HEAVY
        }
        
        weapons = []
        for w_data in data["weapons"]:
            weapon = Weapon(
                name=w_data["name"],
                range=w_data["range"],
                penetration=w_data["penetration"],
                fortification_damage=w_data.get("fortification_damage", 0),
                keywords=w_data.get("keywords", [])
            )
            weapons.append(weapon)
        
        unit = Unit(
            unit_id=unit_id,
            name=name,
            movement=data["movement"],
            armor=armor_map.get(data["armor"], ArmorType.NONE),
            control=data["control"],
            health=data["health"],
            max_health=data["health"],
            weapons=weapons,
            abilities=data.get("abilities", []),
            tags=data.get("tags", []),
            position=position,
            owner=owner
        )
        
        return unit
    
    def run_game(self, ai1: AIAgent, ai2: Optional[AIAgent] = None, 
                 max_turns: int = 50, verbose: bool = False, 
                 log_file: Optional[str] = None) -> Dict:
        """Run a complete game"""
        state, engine = self.setup_game()
        state.max_turns = max_turns
        
        # Set up logging
        log_buffer = []
        
        def log_output(msg: str):
            """Log to both console and buffer"""
            if verbose:
                print(msg)
            if log_file:
                log_buffer.append(msg)
        
        # Log game start
        log_output(f"{'='*60}")
        log_output(f"GAME START - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_output(f"{'='*60}")
        log_output(f"Map Size: {self.map_size}")
        log_output(f"Max Turns: {max_turns}")
        log_output(f"\nPlayer 1 Army:")
        for unit in [u for u in state.units.values() if u.owner == 1]:
            log_output(f"  - {unit.name} (HP: {unit.health})")
        log_output(f"\nPlayer 2 Army:")
        for unit in [u for u in state.units.values() if u.owner == 2]:
            log_output(f"  - {unit.name} (HP: {unit.health})")
        log_output("")
        
        turn_count = 0
        
        while not state.is_game_over() and turn_count < max_turns * 2:
            turn_count += 1
            
            # Determine which AI takes turn
            if state.active_player == 1:
                current_ai = ai1
            else:
                current_ai = ai2 if ai2 else ai1
            
            log_output(f"\n{'='*60}")
            log_output(f"Turn {state.current_turn}, Player {state.active_player}")
            log_output(f"{'='*60}")
            
            # AI takes turn
            actions = current_ai.take_turn(state, engine, verbose=verbose)
            
            # Advance to next turn
            state.advance_turn()
        
        # Calculate final scores
        state.calculate_score()
        winner = state.get_winner()
        
        # Log game end
        log_output(f"\n{'='*60}")
        log_output("GAME END")
        log_output(f"{'='*60}")
        log_output(f"Winner: Player {winner if winner else 'TIE'}")
        log_output(f"Final Scores: P1={state.scores[1]}, P2={state.scores[2]}")
        log_output(f"Turns Played: {state.current_turn}")
        log_output(f"P1 Units Remaining: {len([u for u in state.units.values() if u.owner == 1 and u.is_alive()])}")
        log_output(f"P2 Units Remaining: {len([u for u in state.units.values() if u.owner == 2 and u.is_alive()])}")
        
        # Write log file if specified
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_buffer))
        
        # Update AI statistics
        if ai2:
            ai1.update_from_game_result(winner == 1, state)
            ai2.update_from_game_result(winner == 2, state)
        else:
            # Single player mode - consider it won if player 1 won
            ai1.update_from_game_result(winner == ai1.player_id, state)
        
        return {
            'winner': winner,
            'final_scores': state.scores,
            'turns_played': state.current_turn,
            'p1_units_remaining': len([u for u in state.units.values() if u.owner == 1 and u.is_alive()]),
            'p2_units_remaining': len([u for u in state.units.values() if u.owner == 2 and u.is_alive()])
        }
    
    def run_training_session(self, num_games: int = 100, verbose: bool = False, 
                            save_logs: bool = True) -> Dict:
        """Run multiple games for AI training"""
        ai1 = AIAgent(player_id=1, difficulty="medium")
        ai2 = AIAgent(player_id=2, difficulty="medium")
        
        # Create session directory
        session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_dir = f"TestingResults/session_{session_timestamp}"
        
        if save_logs:
            os.makedirs(session_dir, exist_ok=True)
        
        results = {
            'session_id': session_timestamp,
            'games_played': num_games,
            'p1_wins': 0,
            'p2_wins': 0,
            'ties': 0,
            'average_turns': 0,
            'game_results': []
        }
        
        total_turns = 0
        
        print(f"\nStarting training session: {session_timestamp}")
        print(f"Saving logs to: {session_dir}")
        print("="*60)
        
        for game_num in range(num_games):
            if verbose or (game_num + 1) % 10 == 0:
                print(f"\n=== Game {game_num + 1}/{num_games} ===")
            
            # Set up log file for this game
            log_file = None
            if save_logs:
                log_file = os.path.join(session_dir, f"game_{game_num + 1:03d}.log")
            
            result = self.run_game(ai1, ai2, verbose=verbose, log_file=log_file)
            
            # Track individual game result
            game_summary = {
                'game_number': game_num + 1,
                'winner': result['winner'],
                'turns': result['turns_played'],
                'final_scores': result['final_scores'],
                'p1_units_left': result['p1_units_remaining'],
                'p2_units_left': result['p2_units_remaining'],
                'ai1_win_rate_after': ai1.win_rate,
                'ai2_win_rate_after': ai2.win_rate
            }
            results['game_results'].append(game_summary)
            
            if result['winner'] == 1:
                results['p1_wins'] += 1
            elif result['winner'] == 2:
                results['p2_wins'] += 1
            else:
                results['ties'] += 1
            
            total_turns += result['turns_played']
            
            # Occasionally randomize weights for exploration
            if (game_num + 1) % 20 == 0:
                ai1.randomize_weights(0.05)
                ai2.randomize_weights(0.05)
                print(f"  [Weight adjustment at game {game_num + 1}]")
        
        results['average_turns'] = total_turns / num_games
        results['ai1_win_rate'] = ai1.win_rate
        results['ai2_win_rate'] = ai2.win_rate
        results['ai1_final_weights'] = ai1.weights.copy()
        results['ai2_final_weights'] = ai2.weights.copy()
        
        # Save summary file
        if save_logs:
            self._save_session_summary(session_dir, results, ai1, ai2)
        
        return results
    
    def _save_session_summary(self, session_dir: str, results: Dict, 
                             ai1: AIAgent, ai2: AIAgent):
        """Save comprehensive session summary"""
        summary_path = os.path.join(session_dir, "session_summary.txt")
        json_path = os.path.join(session_dir, "session_data.json")
        
        # Write human-readable summary
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("TRAINING SESSION SUMMARY\n")
            f.write("="*60 + "\n\n")
            f.write(f"Session ID: {results['session_id']}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Games Played: {results['games_played']}\n\n")
            
            f.write("-"*60 + "\n")
            f.write("OVERALL RESULTS\n")
            f.write("-"*60 + "\n")
            f.write(f"Player 1 Wins: {results['p1_wins']} ({results['p1_wins']/results['games_played']*100:.1f}%)\n")
            f.write(f"Player 2 Wins: {results['p2_wins']} ({results['p2_wins']/results['games_played']*100:.1f}%)\n")
            f.write(f"Ties: {results['ties']} ({results['ties']/results['games_played']*100:.1f}%)\n")
            f.write(f"Average Game Length: {results['average_turns']:.1f} turns\n\n")
            
            f.write("-"*60 + "\n")
            f.write("AI LEARNING PROGRESS\n")
            f.write("-"*60 + "\n")
            f.write(f"AI 1 Final Win Rate: {results['ai1_win_rate']:.2%}\n")
            f.write(f"AI 2 Final Win Rate: {results['ai2_win_rate']:.2%}\n")
            f.write(f"AI 1 Games Played: {ai1.games_played}\n")
            f.write(f"AI 2 Games Played: {ai2.games_played}\n\n")
            
            f.write("-"*60 + "\n")
            f.write("AI 1 FINAL WEIGHTS\n")
            f.write("-"*60 + "\n")
            for key, value in sorted(ai1.weights.items()):
                f.write(f"  {key:25s}: {value:8.2f}\n")
            
            f.write("\n" + "-"*60 + "\n")
            f.write("AI 2 FINAL WEIGHTS\n")
            f.write("-"*60 + "\n")
            for key, value in sorted(ai2.weights.items()):
                f.write(f"  {key:25s}: {value:8.2f}\n")
            
            f.write("\n" + "-"*60 + "\n")
            f.write("GAME-BY-GAME RESULTS\n")
            f.write("-"*60 + "\n")
            f.write(f"{'Game':<6} {'Winner':<8} {'Turns':<7} {'P1 Left':<9} {'P2 Left':<9} {'P1 WinRate':<12} {'P2 WinRate':<12}\n")
            f.write("-"*60 + "\n")
            
            for game in results['game_results']:
                winner_str = f"P{game['winner']}" if game['winner'] else "TIE"
                f.write(f"{game['game_number']:<6} {winner_str:<8} {game['turns']:<7} "
                       f"{game['p1_units_left']:<9} {game['p2_units_left']:<9} "
                       f"{game['ai1_win_rate_after']:<12.2%} {game['ai2_win_rate_after']:<12.2%}\n")
        
        # Write JSON data for programmatic access
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSession summary saved to: {summary_path}")
        print(f"Session data saved to: {json_path}")


def main():
    """Main entry point for training"""
    print("Lead Ledger AI Training System")
    print("=" * 50)
    
    simulator = GameSimulator(map_size=8)
    
    # Run a training session
    print("\nRunning training session...")
    results = simulator.run_training_session(num_games=10, verbose=False, save_logs=True)
    
    print("\n" + "=" * 50)
    print("Training Results:")
    print(f"Games Played: {results['games_played']}")
    print(f"Player 1 Wins: {results['p1_wins']}")
    print(f"Player 2 Wins: {results['p2_wins']}")
    print(f"Ties: {results['ties']}")
    print(f"Average Turns: {results['average_turns']:.1f}")
    print(f"AI 1 Win Rate: {results['ai1_win_rate']:.2%}")
    print(f"AI 2 Win Rate: {results['ai2_win_rate']:.2%}")
    print("\nAll logs saved to TestingResults folder")


if __name__ == "__main__":
    main()
