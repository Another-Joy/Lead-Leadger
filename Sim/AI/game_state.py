"""
Lead Ledger - Game State Management
Handles all game state, rules enforcement, and state transitions.
"""

import json
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from copy import deepcopy


class ArmorType(Enum):
    NONE = "N"
    LIGHT = "L"
    MEDIUM = "M"
    HEAVY = "H"


class UnitType(Enum):
    INFANTRY = "Infantry"
    VEHICLE = "Vehicle"
    AIRCRAFT = "Aircraft"
    HOVER = "Hover"


class ActionType(Enum):
    # Major Actions
    ADVANCE = "advance"
    EMBARK = "embark"
    DISEMBARK = "disembark"
    SALVO = "salvo"
    CAPTURE = "capture"
    # Minor Actions
    MOVE = "move"
    CONSOLIDATE = "consolidate"
    CONTROL = "control"
    SHOT = "shot"
    # Special Actions
    OVERWATCH = "overwatch"


@dataclass
class HexCoord:
    """Axial coordinate system for hexagonal grid"""
    q: int  # column
    r: int  # row
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
    
    def distance(self, other: 'HexCoord') -> int:
        """Calculate hex distance between two coordinates"""
        return (abs(self.q - other.q) + 
                abs(self.q + self.r - other.q - other.r) + 
                abs(self.r - other.r)) // 2
    
    def neighbors(self) -> List['HexCoord']:
        """Get all 6 adjacent hex coordinates"""
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [HexCoord(self.q + dq, self.r + dr) for dq, dr in directions]
    
    def get_direction_to(self, target: 'HexCoord') -> int:
        """Get direction (0-5) to target hex"""
        dq = target.q - self.q
        dr = target.r - self.r
        
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        # Normalize direction
        max_val = max(abs(dq), abs(dr), abs(-dq-dr))
        if max_val == 0:
            return 0
        
        norm_dq = dq // max_val
        norm_dr = dr // max_val
        
        for i, (d_q, d_r) in enumerate(directions):
            if d_q == norm_dq and d_r == norm_dr:
                return i
        return 0


@dataclass
class Weapon:
    name: str
    range: int
    penetration: Dict[str, str]  # armor_type: roll_requirement (e.g., "3+", "8-")
    fortification_damage: int
    keywords: List[str] = field(default_factory=list)
    ammo: Optional[int] = None  # None = unlimited
    
    def can_penetrate(self, armor: ArmorType, roll: int) -> bool:
        """Check if a roll penetrates given armor"""
        armor_key = armor.value
        if armor_key not in self.penetration or self.penetration[armor_key] == "NA":
            return False
        
        requirement = self.penetration[armor_key]
        if '+' in requirement:  # Roll up
            target = int(requirement.replace('+', ''))
            return roll >= target
        else:  # Roll down
            target = int(requirement.replace('-', ''))
            return roll <= target


@dataclass
class Unit:
    unit_id: str
    name: str
    movement: int
    armor: ArmorType
    control: int
    health: int
    max_health: int
    weapons: List[Weapon]
    abilities: List[str]
    tags: List[str]
    position: Optional[HexCoord] = None
    orientation: int = 0  # 0-5 for hex directions
    owner: int = 0  # player id (1 or 2)
    
    # State tracking
    current_health: int = 0
    has_moved: bool = False
    has_shot: bool = False
    movement_used: int = 0
    in_overwatch: bool = False
    overwatch_arc: Optional[int] = None
    weapons_fired: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if self.current_health == 0:
            self.current_health = self.health
    
    @property
    def unit_type(self) -> UnitType:
        """Determine unit type from tags"""
        for tag in self.tags:
            if "Infantry" in tag:
                return UnitType.INFANTRY
            elif "Aircraft" in tag:
                return UnitType.AIRCRAFT
            elif "Hover" in tag:
                return UnitType.HOVER
        return UnitType.VEHICLE
    
    def is_alive(self) -> bool:
        return self.current_health > 0
    
    def take_damage(self, amount: int = 1):
        self.current_health = max(0, self.current_health - amount)
    
    def reset_turn_state(self):
        """Reset state at start of turn"""
        self.has_moved = False
        self.has_shot = False
        self.movement_used = 0
        self.weapons_fired.clear()


@dataclass
class Building:
    position: HexCoord
    total_pips: int
    neutral_pips: int = 0
    player1_pips: int = 0
    player2_pips: int = 0
    
    def __post_init__(self):
        if self.neutral_pips == 0 and self.player1_pips == 0 and self.player2_pips == 0:
            self.neutral_pips = self.total_pips
    
    @property
    def current_pips(self) -> int:
        return self.neutral_pips + self.player1_pips + self.player2_pips
    
    def get_control_value(self, player: int) -> int:
        """Get pip count for a specific player"""
        if player == 1:
            return self.player1_pips
        elif player == 2:
            return self.player2_pips
        return self.neutral_pips
    
    def capture_pips(self, player: int, amount: int = 1):
        """Capture pips for a player (priority: neutral > enemy > ally)"""
        if player not in [1, 2]:
            return
        
        enemy = 2 if player == 1 else 1
        pips_to_capture = amount
        
        while pips_to_capture > 0:
            if self.neutral_pips > 0:
                # Neutral pips convert at 2x rate
                convert_amount = min(1, pips_to_capture)
                self.neutral_pips -= convert_amount
                if player == 1:
                    self.player1_pips += 2 * convert_amount
                else:
                    self.player2_pips += 2 * convert_amount
                pips_to_capture -= convert_amount
            elif (enemy == 1 and self.player1_pips > 0) or (enemy == 2 and self.player2_pips > 0):
                # Convert enemy pips
                if enemy == 1:
                    convert_amount = min(self.player1_pips, pips_to_capture)
                    self.player1_pips -= convert_amount
                    self.player2_pips += convert_amount
                else:
                    convert_amount = min(self.player2_pips, pips_to_capture)
                    self.player2_pips -= convert_amount
                    self.player1_pips += convert_amount
                pips_to_capture -= convert_amount
            else:
                break


class GameState:
    """Main game state manager"""
    
    def __init__(self, map_size: int = 8):
        self.map_size = map_size
        self.current_turn = 0
        self.current_cycle = 0
        self.active_player = 1
        self.phase = "deployment"
        
        # Game entities
        self.units: Dict[str, Unit] = {}
        self.buildings: Dict[HexCoord, Building] = {}
        self.blocked_tiles: Set[HexCoord] = set()
        
        # Scores
        self.scores = {1: 0, 2: 0}
        
        # Action tracking
        self.major_action_available = True
        self.minor_action_available = True
        
        # Game settings
        self.max_turns = 50
        self.cycle_length = 10
    
    def get_unit_at(self, pos: HexCoord) -> Optional[Unit]:
        """Get unit at specific position"""
        for unit in self.units.values():
            if unit.position == pos and unit.is_alive():
                return unit
        return None
    
    def get_units_at(self, pos: HexCoord) -> List[Unit]:
        """Get all units at specific position"""
        return [u for u in self.units.values() if u.position == pos and u.is_alive()]
    
    def is_enemy_tile(self, pos: HexCoord, player: int) -> bool:
        """Check if tile contains enemy units"""
        enemy = 2 if player == 1 else 1
        return any(u.owner == enemy for u in self.get_units_at(pos))
    
    def is_valid_position(self, pos: HexCoord) -> bool:
        """Check if position is within map bounds"""
        # For hexagonal map with radius map_size
        return abs(pos.q) <= self.map_size and abs(pos.r) <= self.map_size and abs(pos.q + pos.r) <= self.map_size
    
    def has_line_of_sight(self, from_pos: HexCoord, to_pos: HexCoord, shooter_player: int) -> bool:
        """Check if there's line of sight between two positions"""
        if from_pos == to_pos:
            return True
        
        # Use bresenham-like line algorithm for hex grid
        distance = from_pos.distance(to_pos)
        
        # Early exit if distance is 1 (adjacent hexes always have LoS)
        if distance <= 1:
            return True
        
        checked = set()  # Prevent infinite loops
        for i in range(1, distance):
            t = i / distance
            # Linear interpolation in cube coordinates
            q = from_pos.q + t * (to_pos.q - from_pos.q)
            r = from_pos.r + t * (to_pos.r - from_pos.r)
            
            # Round to nearest hex
            check_pos = HexCoord(round(q), round(r))
            
            # Skip if already checked
            if check_pos in checked:
                continue
            checked.add(check_pos)
            
            # Don't check the start or end positions
            if check_pos == from_pos or check_pos == to_pos:
                continue
            
            # Check if blocked by building
            if check_pos in self.buildings:
                return False
            
            # Check if blocked by enemy unit
            if self.is_enemy_tile(check_pos, shooter_player):
                return False
        
        return True
    
    def get_units_in_range(self, unit: Unit, weapon: Weapon) -> List[Unit]:
        """Get all enemy units in range of weapon"""
        if not unit.position:
            return []
        
        targets = []
        enemy = 2 if unit.owner == 1 else 1
        
        for target in self.units.values():
            if not target.is_alive() or target.owner != enemy or not target.position:
                continue
            
            distance = unit.position.distance(target.position)
            
            # Check range
            weapon_range = weapon.range
            if "Long" in weapon.keywords:
                weapon_range += 2
            
            if distance > weapon_range:
                continue
            
            # Check frontal arc if needed
            if "Frontal" in weapon.keywords:
                direction = unit.position.get_direction_to(target.position)
                if abs(direction - unit.orientation) > 1 and abs(direction - unit.orientation) < 5:
                    continue
            
            # Check line of sight
            if not self.has_line_of_sight(unit.position, target.position, unit.owner):
                continue
            
            targets.append(target)
        
        return targets
    
    def calculate_score(self):
        """Calculate scores based on building control"""
        self.scores = {1: 0, 2: 0}
        for building in self.buildings.values():
            self.scores[1] += building.player1_pips
            self.scores[2] += building.player2_pips
    
    def advance_turn(self):
        """Advance to next player's turn"""
        self.active_player = 2 if self.active_player == 1 else 1
        
        if self.active_player == 1:
            self.current_turn += 1
            
            # Check for cycle end
            if self.current_turn % self.cycle_length == 0:
                self.current_cycle += 1
                self.calculate_score()
        
        # Reset action availability
        self.major_action_available = True
        self.minor_action_available = True
        
        # Reset all units for active player
        for unit in self.units.values():
            if unit.owner == self.active_player:
                unit.reset_turn_state()
    
    def is_game_over(self) -> bool:
        """Check if game is over"""
        if self.current_turn >= self.max_turns:
            return True
        
        # Check if either player has no units
        p1_alive = any(u.is_alive() and u.owner == 1 for u in self.units.values())
        p2_alive = any(u.is_alive() and u.owner == 2 for u in self.units.values())
        
        return not p1_alive or not p2_alive
    
    def get_winner(self) -> Optional[int]:
        """Get winner (None if tie)"""
        if not self.is_game_over():
            return None
        
        # Check elimination
        p1_alive = any(u.is_alive() and u.owner == 1 for u in self.units.values())
        p2_alive = any(u.is_alive() and u.owner == 2 for u in self.units.values())
        
        if not p1_alive and p2_alive:
            return 2
        if p1_alive and not p2_alive:
            return 1
        
        # Score-based winner
        if self.scores[1] > self.scores[2]:
            return 1
        elif self.scores[2] > self.scores[1]:
            return 2
        return None
    
    def clone(self) -> 'GameState':
        """Create a deep copy of the game state"""
        return deepcopy(self)
