"""
Lead Ledger - AI Agent
Implements decision-making AI for the game.
"""

import random
import math
from typing import List, Dict, Tuple, Optional
from game_state import *
from game_engine import GameEngine
from collections import defaultdict


class AIAgent:
    """AI agent for playing Lead Ledger"""
    
    def __init__(self, player_id: int, difficulty: str = "medium"):
        self.player_id = player_id
        self.difficulty = difficulty
        self.enemy_id = 2 if player_id == 1 else 1
        
        # Learning parameters
        self.position_values: Dict[HexCoord, float] = defaultdict(float)
        self.action_history: List[Dict] = []
        self.win_rate = 0.0
        self.games_played = 0
        
        # Strategic weights (can be tuned during learning)
        self.weights = {
            'eliminate_enemy': 100.0,
            'capture_building': 80.0,
            'protect_unit': 70.0,
            'position_advantage': 50.0,
            'damage_dealt': 60.0,
            'health_preservation': 40.0,
            'building_control': 90.0,
        }
    
    def evaluate_state(self, state: GameState) -> float:
        """Evaluate how good the current state is for this player"""
        score = 0.0
        
        # Building control score
        my_building_control = sum(b.get_control_value(self.player_id) for b in state.buildings.values())
        enemy_building_control = sum(b.get_control_value(self.enemy_id) for b in state.buildings.values())
        score += (my_building_control - enemy_building_control) * self.weights['building_control']
        
        # Unit health and count
        my_units = [u for u in state.units.values() if u.owner == self.player_id and u.is_alive()]
        enemy_units = [u for u in state.units.values() if u.owner == self.enemy_id and u.is_alive()]
        
        my_total_health = sum(u.current_health for u in my_units)
        enemy_total_health = sum(u.current_health for u in enemy_units)
        
        score += (my_total_health - enemy_total_health) * self.weights['health_preservation']
        score += (len(my_units) - len(enemy_units)) * self.weights['eliminate_enemy']
        
        # Position evaluation
        for unit in my_units:
            if not unit.position:
                continue
            
            # Value being near buildings
            for building_pos in state.buildings.keys():
                distance = unit.position.distance(building_pos)
                if distance <= 2:
                    score += (3 - distance) * 10
            
            # Value being near enemies (for combat units)
            if unit.weapons:
                for enemy in enemy_units:
                    if enemy.position:
                        distance = unit.position.distance(enemy.position)
                        weapon_range = max(w.range for w in unit.weapons)
                        if distance <= weapon_range:
                            score += 20
        
        return score
    
    def get_best_target(self, unit: Unit, engine: GameEngine) -> Optional[Tuple[Weapon, Unit]]:
        """Find the best target for a unit"""
        best_target = None
        best_score = -float('inf')
        
        for weapon in unit.weapons:
            targets = engine.get_valid_targets(unit, weapon)
            
            for target in targets:
                # Calculate target priority
                score = 0.0
                
                # Prioritize low-health enemies
                health_ratio = target.current_health / target.max_health
                score += (1.0 - health_ratio) * 50
                
                # Prioritize high-threat enemies
                if target.weapons:
                    score += len(target.weapons) * 20
                
                # Prioritize enemies near our buildings
                for building_pos in engine.state.buildings.keys():
                    if target.position:
                        distance = target.position.distance(building_pos)
                        if distance <= 2:
                            score += 30
                
                # Consider kill probability
                pen_value = weapon.penetration.get(target.armor.value, "NA")
                if pen_value != "NA":
                    if '+' in pen_value:
                        threshold = int(pen_value.replace('+', ''))
                        kill_prob = (13 - threshold) / 12.0
                    else:
                        threshold = int(pen_value.replace('-', ''))
                        kill_prob = threshold / 12.0
                    
                    score += kill_prob * 40
                
                if score > best_score:
                    best_score = score
                    best_target = (weapon, target)
        
        return best_target
    
    def choose_move_position(self, unit: Unit, engine: GameEngine) -> Optional[HexCoord]:
        """Choose best position to move to"""
        valid_moves = engine.get_valid_moves(unit)
        
        if not valid_moves:
            return None
        
        best_pos = None
        best_score = -float('inf')
        
        for pos in valid_moves:
            score = 0.0
            
            # Value being near buildings
            for building_pos, building in engine.state.buildings.items():
                distance = pos.distance(building_pos)
                
                # Prioritize buildings we don't fully control
                our_control = building.get_control_value(self.player_id)
                max_control = building.total_pips
                
                if our_control < max_control:
                    if distance == 0:
                        score += 100  # On the building
                    elif distance <= 2:
                        score += (3 - distance) * 30
            
            # Value being in range of enemies
            for enemy in engine.state.units.values():
                if enemy.owner != self.enemy_id or not enemy.is_alive() or not enemy.position:
                    continue
                
                distance = pos.distance(enemy.position)
                
                # For units with weapons, value being in range
                if unit.weapons:
                    max_range = max(w.range for w in unit.weapons)
                    if distance <= max_range:
                        score += 25
                
                # Avoid being too close to strong enemies
                if enemy.weapons and distance <= 2:
                    score -= 20
            
            # Avoid enemy-controlled buildings
            for building_pos, building in engine.state.buildings.items():
                if building.get_control_value(self.enemy_id) > building.get_control_value(self.player_id):
                    distance = pos.distance(building_pos)
                    if distance == 0:
                        score -= 30
            
            if score > best_score:
                best_score = score
                best_pos = pos
        
        return best_pos
    
    def decide_action(self, state: GameState, engine: GameEngine) -> Optional[Dict]:
        """Decide on the best action to take"""
        # Get all units we control
        my_units = [u for u in state.units.values() 
                   if u.owner == self.player_id and u.is_alive() and u.position]
        
        if not my_units:
            return None
        
        best_action = None
        best_value = -float('inf')
        
        # Evaluate each unit's potential actions
        for unit in my_units:
            # Try combat actions if major action available
            if state.major_action_available:
                # Try capture if on building
                building = state.buildings.get(unit.position)
                if building and unit.control > 0:
                    enemy_pips = building.get_control_value(self.enemy_id)
                    neutral_pips = building.neutral_pips
                    
                    if enemy_pips > 0 or neutral_pips > 0:
                        value = (enemy_pips * 2 + neutral_pips * 4) * self.weights['capture_building'] / 100
                        
                        if value > best_value:
                            best_value = value
                            best_action = {
                                'type': 'capture',
                                'unit': unit,
                                'action': ActionType.CAPTURE
                            }
                
                # Try salvo if has targets
                target_data = self.get_best_target(unit, engine)
                if target_data:
                    weapon, target = target_data
                    
                    # Estimate damage value - make this much more valuable!
                    damage_value = self.weights['damage_dealt'] * 2.0  # Base value doubled
                    if target.current_health == 1:
                        damage_value *= 3  # Triple value for kills
                    elif target.current_health == 2:
                        damage_value *= 2  # Double for near-kills
                    
                    # Add strategic value for attacking important targets
                    if target.weapons:
                        damage_value += self.weights['eliminate_enemy'] * 0.5
                    
                    if damage_value > best_value:
                        best_value = damage_value
                        best_action = {
                            'type': 'salvo',
                            'unit': unit,
                            'weapon': weapon,
                            'target': target,
                            'action': ActionType.SALVO
                        }
                
                # Try advance towards objective
                best_pos = self.choose_move_position(unit, engine)
                if best_pos and best_pos != unit.position:
                    # Simple pathfinding: direct line
                    path = [unit.position, best_pos]
                    
                    move_value = self.weights['position_advantage'] * 0.8
                    
                    # Bonus if has assault weapon and can shoot after
                    has_assault = any('Assault' in w.keywords for w in unit.weapons)
                    if has_assault:
                        move_value *= 1.5
                    
                    if move_value > best_value:
                        best_value = move_value
                        best_action = {
                            'type': 'advance',
                            'unit': unit,
                            'path': path,
                            'action': ActionType.ADVANCE
                        }
            
            # Try minor actions
            if state.minor_action_available:
                # Try minor shot
                if not unit.has_shot and unit.weapons:
                    target_data = self.get_best_target(unit, engine)
                    if target_data:
                        weapon, target = target_data
                        value = self.weights['damage_dealt'] * 1.5  # Increased value for minor shots
                        if target.current_health <= 2:
                            value *= 2  # Much more valuable if can kill
                        
                        if value > best_value:
                            best_value = value
                            best_action = {
                                'type': 'minor_shot',
                                'unit': unit,
                                'weapon': weapon,
                                'target': target,
                                'action': ActionType.SHOT
                            }
                
                # Try control
                building = state.buildings.get(unit.position)
                if building and unit.control > 0 and not unit.has_moved:
                    enemy_pips = building.get_control_value(self.enemy_id)
                    neutral_pips = building.neutral_pips
                    
                    if enemy_pips > 0 or neutral_pips > 0:
                        value = (enemy_pips + neutral_pips * 2) * self.weights['capture_building'] / 150
                        
                        if value > best_value:
                            best_value = value
                            best_action = {
                                'type': 'control',
                                'unit': unit,
                                'action': ActionType.CONTROL
                            }
                
                # Try minor move
                if not unit.has_moved and unit.movement > 1:
                    neighbors = [n for n in unit.position.neighbors() if state.is_valid_position(n)]
                    if neighbors:
                        best_neighbor = max(neighbors, 
                                          key=lambda p: self.evaluate_position(p, unit, state))
                        
                        value = self.weights['position_advantage'] * 0.3
                        
                        if value > best_value:
                            best_value = value
                            best_action = {
                                'type': 'minor_move',
                                'unit': unit,
                                'target_pos': best_neighbor,
                                'action': ActionType.MOVE
                            }
        
        return best_action
    
    def evaluate_position(self, pos: HexCoord, unit: Unit, state: GameState) -> float:
        """Evaluate how good a position is"""
        score = 0.0
        
        # Near buildings
        for building_pos in state.buildings.keys():
            distance = pos.distance(building_pos)
            if distance <= 2:
                score += (3 - distance) * 10
        
        # Near enemies (for combat)
        if unit.weapons:
            for enemy in state.units.values():
                if enemy.owner != self.enemy_id or not enemy.position:
                    continue
                distance = pos.distance(enemy.position)
                if distance <= 3:
                    score += 5
        
        return score
    
    def execute_action(self, action: Dict, engine: GameEngine, verbose: bool = False) -> bool:
        """Execute the chosen action"""
        if not action:
            return False
        
        action_type = action['type']
        unit = action['unit']
        
        try:
            if action_type == 'capture':
                if verbose:
                    print(f"  {unit.name} capturing building at {unit.position}")
                success, msg = engine.execute_capture(unit)
                if verbose:
                    print(f"    Result: {msg}")
                return success
            
            elif action_type == 'salvo':
                weapon = action['weapon']
                target = action['target']
                if verbose:
                    dist = unit.position.distance(target.position)
                    print(f"  {unit.name} shooting {weapon.name} at {target.name}")
                    print(f"    Distance: {dist}, Target HP: {target.current_health}/{target.max_health}")
                targets = {weapon.name: target}
                results = engine.execute_salvo(unit, targets)
                if verbose:
                    for wname, success, msg in results:
                        print(f"    {wname}: {msg}")
                    print(f"    Target HP after: {target.current_health}/{target.max_health}")
                return any(success for _, success, _ in results)
            
            elif action_type == 'advance':
                path = action['path']
                if verbose:
                    print(f"  {unit.name} advancing: {path[0]} -> {path[-1]}")
                success = engine.execute_advance(unit, path)
                
                # Try assault shot after advance if possible
                if success and engine.state.minor_action_available:
                    for weapon in unit.weapons:
                        if 'Assault' in weapon.keywords:
                            target_data = self.get_best_target(unit, engine)
                            if target_data:
                                w, t = target_data
                                if verbose:
                                    print(f"    Assault shot: {w.name} at {t.name}")
                                shot_success, shot_msg = engine.execute_minor_shot(unit, w, t)
                                if verbose:
                                    print(f"    {shot_msg}")
                                break
                
                return success
            
            elif action_type == 'minor_shot':
                weapon = action['weapon']
                target = action['target']
                if verbose:
                    dist = unit.position.distance(target.position)
                    print(f"  {unit.name} (minor) shooting {weapon.name} at {target.name}")
                    print(f"    Distance: {dist}, Target HP: {target.current_health}/{target.max_health}")
                success, msg = engine.execute_minor_shot(unit, weapon, target)
                if verbose:
                    print(f"    Result: {msg}")
                    print(f"    Target HP after: {target.current_health}/{target.max_health}")
                return success
            
            elif action_type == 'control':
                if verbose:
                    print(f"  {unit.name} controlling building at {unit.position}")
                success, msg = engine.execute_control(unit)
                if verbose:
                    print(f"    {msg}")
                return success
            
            elif action_type == 'minor_move':
                target_pos = action['target_pos']
                if verbose:
                    print(f"  {unit.name} moving: {unit.position} -> {target_pos}")
                success, msg = engine.execute_minor_move(unit, target_pos)
                return success
        
        except Exception as e:
            print(f"Error executing action: {e}")
            return False
        
        return False
    
    def take_turn(self, state: GameState, engine: GameEngine, verbose: bool = False) -> List[Dict]:
        """Take a complete turn (major + minor actions)"""
        actions_taken = []
        
        if verbose:
            print(f"\nPlayer {self.player_id} turn:")
        
        # Try to take major action
        if state.major_action_available:
            action = self.decide_action(state, engine)
            if action:
                if verbose:
                    print(f"  Major action: {action['type']}")
                success = self.execute_action(action, engine, verbose=verbose)
                if success:
                    actions_taken.append(action)
                elif verbose:
                    print(f"    FAILED to execute")
        
        # Try to take minor action
        if state.minor_action_available:
            action = self.decide_action(state, engine)
            if action:
                if verbose:
                    print(f"  Minor action: {action['type']}")
                success = self.execute_action(action, engine, verbose=verbose)
                if success:
                    actions_taken.append(action)
                elif verbose:
                    print(f"    FAILED to execute")
        
        return actions_taken
    
    def update_from_game_result(self, won: bool, final_state: GameState):
        """Update AI learning from game result"""
        self.games_played += 1
        if won:
            self.win_rate = (self.win_rate * (self.games_played - 1) + 1.0) / self.games_played
        else:
            self.win_rate = (self.win_rate * (self.games_played - 1)) / self.games_played
    
    def randomize_weights(self, variance: float = 0.1):
        """Slightly randomize weights for exploration"""
        for key in self.weights:
            adjustment = random.uniform(-variance, variance)
            self.weights[key] *= (1.0 + adjustment)
