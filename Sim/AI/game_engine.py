"""
Lead Ledger - Game Engine
Handles action execution, rules enforcement, and game logic.
"""

import random
from typing import List, Optional, Tuple
from game_state import *


class GameEngine:
    """Game engine for executing actions and enforcing rules"""
    
    def __init__(self, state: GameState):
        self.state = state
    
    def can_move(self, unit: Unit, target_pos: HexCoord) -> Tuple[bool, str]:
        """Check if unit can move to target position"""
        if not unit.position:
            return False, "Unit has no position"
        
        if not self.state.is_valid_position(target_pos):
            return False, "Target position out of bounds"
        
        if target_pos in self.state.blocked_tiles:
            return False, "Target position is blocked"
        
        # Calculate movement cost
        distance = unit.position.distance(target_pos)
        cost = distance
        
        # Check if exiting enemy tile
        if self.state.is_enemy_tile(unit.position, unit.owner):
            cost *= 2
        
        # Check if unit has enough movement
        movement_available = unit.movement - unit.movement_used
        if cost > movement_available:
            return False, f"Insufficient movement: need {cost}, have {movement_available}"
        
        return True, "OK"
    
    def execute_move(self, unit: Unit, target_pos: HexCoord, orientation: Optional[int] = None) -> bool:
        """Execute unit movement"""
        can_move, reason = self.can_move(unit, target_pos)
        if not can_move:
            return False
        
        # Calculate cost
        distance = unit.position.distance(target_pos)
        cost = distance
        
        if self.state.is_enemy_tile(unit.position, unit.owner):
            cost *= 2
        
        # Move unit
        unit.position = target_pos
        unit.movement_used += cost
        unit.has_moved = True
        
        if orientation is not None:
            unit.orientation = orientation % 6
        
        return True
    
    def execute_advance(self, unit: Unit, path: List[HexCoord], final_orientation: Optional[int] = None) -> bool:
        """Execute advance action (major)"""
        if not self.state.major_action_available:
            return False
        
        if not path or path[0] != unit.position:
            return False
        
        # Calculate total movement needed
        total_cost = 0
        for i in range(len(path) - 1):
            total_cost += path[i].distance(path[i + 1])
        
        if total_cost > unit.movement:
            return False
        
        # Execute movement along path
        for target in path[1:]:
            if not self.execute_move(unit, target):
                return False
        
        if final_orientation is not None:
            unit.orientation = final_orientation % 6
        
        self.state.major_action_available = False
        return True
    
    def roll_dice(self) -> int:
        """Roll a d12"""
        return random.randint(1, 12)
    
    def execute_shot(self, shooter: Unit, weapon: Weapon, target: Unit, is_minor: bool = False) -> Tuple[bool, str]:
        """Execute a weapon shot"""
        if not shooter.position or not target.position:
            return False, "Units must have positions"
        
        # Check if weapon was already fired
        if weapon.name in shooter.weapons_fired:
            return False, "Weapon already fired this turn"
        
        # Check range
        distance = shooter.position.distance(target.position)
        weapon_range = weapon.range
        if "Long" in weapon.keywords:
            weapon_range += 2
        
        if distance > weapon_range:
            return False, "Target out of range"
        
        # Check LoS
        if not self.state.has_line_of_sight(shooter.position, target.position, shooter.owner):
            return False, "No line of sight"
        
        # Check frontal restriction
        if "Frontal" in weapon.keywords:
            direction = shooter.position.get_direction_to(target.position)
            if abs(direction - shooter.orientation) > 1 and abs(direction - shooter.orientation) < 5:
                return False, "Target not in frontal arc"
        
        # Roll for penetration
        roll = self.roll_dice()
        
        # Minor shot limitation (4- or 9+)
        if is_minor:
            pen_value = weapon.penetration.get(target.armor.value, "NA")
            if pen_value != "NA":
                if '+' in pen_value:
                    target_num = int(pen_value.replace('+', ''))
                    if target_num < 9:
                        roll = min(roll, 9)  # Cap at 9+ for rolling up
                else:
                    target_num = int(pen_value.replace('-', ''))
                    if target_num > 4:
                        roll = max(roll, 4)  # Cap at 4- for rolling down
        
        # Check penetration
        if weapon.can_penetrate(target.armor, roll):
            target.take_damage(1)
            shooter.weapons_fired.add(weapon.name)
            return True, f"Hit! Rolled {roll}, target health: {target.current_health}/{target.max_health}"
        else:
            shooter.weapons_fired.add(weapon.name)
            return False, f"Miss. Rolled {roll}, failed to penetrate {target.armor.value}"
    
    def execute_salvo(self, shooter: Unit, targets: Dict[str, Unit]) -> List[Tuple[str, bool, str]]:
        """Execute salvo action (major) - shoot with all weapons"""
        if not self.state.major_action_available:
            return [("", False, "Major action not available")]
        
        results = []
        for weapon in shooter.weapons:
            if weapon.name in targets:
                target = targets[weapon.name]
                success, msg = self.execute_shot(shooter, weapon, target, is_minor=False)
                results.append((weapon.name, success, msg))
        
        shooter.has_shot = True
        self.state.major_action_available = False
        return results
    
    def execute_capture(self, unit: Unit) -> Tuple[bool, str]:
        """Execute capture action (major)"""
        if not self.state.major_action_available:
            return False, "Major action not available"
        
        if not unit.position:
            return False, "Unit has no position"
        
        # Check if there's a building at unit's position
        building = self.state.buildings.get(unit.position)
        if not building:
            return False, "No building at unit position"
        
        # Capture pips
        building.capture_pips(unit.owner, unit.control)
        
        self.state.major_action_available = False
        return True, f"Captured {unit.control} pips"
    
    def execute_minor_move(self, unit: Unit, target_pos: HexCoord) -> Tuple[bool, str]:
        """Execute minor move action"""
        if not self.state.minor_action_available:
            return False, "Minor action not available"
        
        if unit.movement == 1:
            return False, "Unit with M=1 cannot use minor move"
        
        if unit.has_moved:
            return False, "Unit already moved this turn"
        
        if unit.position.distance(target_pos) != 1:
            return False, "Minor move only allows 1 tile"
        
        if self.execute_move(unit, target_pos):
            self.state.minor_action_available = False
            return True, "Moved 1 tile"
        
        return False, "Movement failed"
    
    def execute_minor_shot(self, shooter: Unit, weapon: Weapon, target: Unit) -> Tuple[bool, str]:
        """Execute minor shot action"""
        if not self.state.minor_action_available:
            return False, "Minor action not available"
        
        if shooter.has_shot:
            return False, "Unit already shot this turn"
        
        success, msg = self.execute_shot(shooter, weapon, target, is_minor=True)
        if success or "rolled" in msg.lower():
            self.state.minor_action_available = False
            shooter.has_shot = True
        
        return success, msg
    
    def execute_control(self, unit: Unit) -> Tuple[bool, str]:
        """Execute control action (minor)"""
        if not self.state.minor_action_available:
            return False, "Minor action not available"
        
        if not unit.position:
            return False, "Unit has no position"
        
        # Check if there's a building at unit's position
        building = self.state.buildings.get(unit.position)
        if not building:
            return False, "No building at unit position"
        
        # Capture pips (normal rate, not double for neutral)
        pips_captured = unit.control
        if building.neutral_pips > 0:
            convert = min(building.neutral_pips, pips_captured)
            building.neutral_pips -= convert
            if unit.owner == 1:
                building.player1_pips += convert
            else:
                building.player2_pips += convert
            pips_captured -= convert
        
        # Convert enemy pips if any left
        enemy = 2 if unit.owner == 1 else 1
        if pips_captured > 0:
            if enemy == 1 and building.player1_pips > 0:
                convert = min(building.player1_pips, pips_captured)
                building.player1_pips -= convert
                building.player2_pips += convert
            elif enemy == 2 and building.player2_pips > 0:
                convert = min(building.player2_pips, pips_captured)
                building.player2_pips -= convert
                building.player1_pips += convert
        
        self.state.minor_action_available = False
        return True, f"Controlled {unit.control} pips"
    
    def execute_overwatch(self, unit: Unit, arc: int) -> Tuple[bool, str]:
        """Execute overwatch action (special - major + minor)"""
        if not self.state.major_action_available or not self.state.minor_action_available:
            return False, "Requires both major and minor actions"
        
        unit.in_overwatch = True
        unit.overwatch_arc = arc
        
        self.state.major_action_available = False
        self.state.minor_action_available = False
        
        return True, f"Unit on overwatch, arc: {arc}"
    
    def get_valid_moves(self, unit: Unit) -> List[HexCoord]:
        """Get all valid move positions for a unit"""
        if not unit.position:
            return []
        
        valid_positions = []
        movement_range = unit.movement - unit.movement_used
        
        # BFS to find all reachable positions
        visited = {unit.position}
        queue = [(unit.position, 0)]
        
        while queue:
            pos, cost = queue.pop(0)
            
            for neighbor in pos.neighbors():
                if neighbor in visited:
                    continue
                
                if not self.state.is_valid_position(neighbor):
                    continue
                
                if neighbor in self.state.blocked_tiles:
                    continue
                
                move_cost = 1
                if self.state.is_enemy_tile(pos, unit.owner):
                    move_cost = 2
                
                new_cost = cost + move_cost
                
                if new_cost <= movement_range:
                    valid_positions.append(neighbor)
                    visited.add(neighbor)
                    queue.append((neighbor, new_cost))
        
        return valid_positions
    
    def get_valid_targets(self, unit: Unit, weapon: Weapon) -> List[Unit]:
        """Get all valid targets for a unit's weapon"""
        return self.state.get_units_in_range(unit, weapon)
