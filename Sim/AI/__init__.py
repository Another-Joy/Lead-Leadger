"""
Lead Ledger AI System
A trainable AI for the Lead Ledger tactical wargame.
"""

from .game_state import GameState, Unit, Weapon, Building, HexCoord, ArmorType, UnitType
from .game_engine import GameEngine
from .ai_agent import AIAgent
from .unit_loader import UnitLoader
from .simulator import GameSimulator, ArmyBuilder, MapGenerator

__version__ = "0.1.0"
__all__ = [
    'GameState', 'Unit', 'Weapon', 'Building', 'HexCoord', 'ArmorType', 'UnitType',
    'GameEngine', 'AIAgent', 'UnitLoader', 'GameSimulator', 'ArmyBuilder', 'MapGenerator'
]
