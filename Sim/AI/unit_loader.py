"""
Lead Ledger - Unit Data Loader
Loads unit datasheets from markdown files.
"""

import os
import re
from typing import Dict, List, Optional
from game_state import Unit, Weapon, ArmorType, HexCoord


class UnitLoader:
    """Load unit datasheets from markdown files"""
    
    def __init__(self, units_path: str = "../Units"):
        self.units_path = units_path
        self.unit_database: Dict[str, Dict] = {}
    
    def parse_weapon_table(self, lines: List[str]) -> List[Weapon]:
        """Parse weapon table from markdown"""
        weapons = []
        
        # Find table header and data rows
        header_idx = -1
        for i, line in enumerate(lines):
            if '| Name' in line or '|Name|' in line:
                header_idx = i
                break
        
        if header_idx == -1:
            return weapons
        
        # Skip separator line
        data_start = header_idx + 2
        
        for line in lines[data_start:]:
            if not line.strip() or not line.startswith('|'):
                break
            
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) < 7:
                continue
            
            name = parts[0]
            range_val = int(parts[1]) if parts[1].isdigit() else 2
            
            # Parse penetration values
            penetration = {
                'N': parts[2],
                'L': parts[3],
                'M': parts[4],
                'H': parts[5]
            }
            
            # Fortification damage
            fort_dmg = 0
            if parts[6] and parts[6] != 'NA':
                try:
                    fort_dmg = int(parts[6])
                except:
                    pass
            
            # Keywords
            keywords = []
            if len(parts) > 7 and parts[7]:
                keywords = [k.strip() for k in parts[7].split(',')]
            
            weapon = Weapon(
                name=name,
                range=range_val,
                penetration=penetration,
                fortification_damage=fort_dmg,
                keywords=keywords
            )
            weapons.append(weapon)
        
        return weapons
    
    def parse_unit_file(self, filepath: str) -> Optional[Dict]:
        """Parse a single unit markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return None
        
        lines = content.split('\n')
        unit_data = {
            'name': os.path.basename(filepath).replace('.md', ''),
            'movement': 2,
            'armor': 'N',
            'control': 0,
            'health': 1,
            'weapons': [],
            'abilities': [],
            'tags': []
        }
        
        # Parse MACH table
        for i, line in enumerate(lines):
            if '| M' in line and '| A' in line and '| C' in line and '| H' in line:
                # Next non-separator line is data
                data_line = lines[i + 2] if i + 2 < len(lines) else ""
                parts = [p.strip() for p in data_line.split('|')[1:-1]]
                
                if len(parts) >= 4:
                    try:
                        unit_data['movement'] = int(parts[0]) if parts[0].isdigit() else 2
                        unit_data['armor'] = parts[1]
                        unit_data['control'] = int(parts[2]) if parts[2].isdigit() else 0
                        unit_data['health'] = int(parts[3]) if parts[3].isdigit() else 1
                    except:
                        pass
                break
        
        # Parse weapons
        unit_data['weapons'] = self.parse_weapon_table(lines)
        
        # Parse abilities
        in_abilities = False
        for line in lines:
            if line.strip().startswith('Abilities:'):
                in_abilities = True
                continue
            
            if in_abilities:
                if line.strip().startswith('Cost:') or line.strip().startswith('Tags:'):
                    in_abilities = False
                elif line.strip().startswith('-'):
                    ability = line.strip()[1:].strip()
                    if ability:
                        unit_data['abilities'].append(ability)
        
        # Parse tags
        in_tags = False
        for line in lines:
            if line.strip().startswith('Tags:'):
                in_tags = True
                continue
            
            if in_tags:
                if line.strip() and not line.strip().startswith('#'):
                    tags = [t.strip() for t in line.split(',')]
                    unit_data['tags'].extend([t for t in tags if t])
                else:
                    break
        
        return unit_data
    
    def load_regiment(self, regiment_name: str) -> Dict[str, Dict]:
        """Load all units from a regiment"""
        regiment_path = os.path.join(self.units_path, regiment_name)
        
        if not os.path.exists(regiment_path):
            return {}
        
        units = {}
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(regiment_path):
            for file in files:
                if file.endswith('.md') and file != 'Summary.md':
                    filepath = os.path.join(root, file)
                    unit_data = self.parse_unit_file(filepath)
                    if unit_data:
                        units[unit_data['name']] = unit_data
        
        return units
    
    def create_unit_instance(self, unit_name: str, unit_id: str, owner: int, 
                            position: Optional[HexCoord] = None) -> Optional[Unit]:
        """Create a unit instance from database"""
        if unit_name not in self.unit_database:
            return None
        
        data = self.unit_database[unit_name]
        
        # Convert armor string to enum
        armor_map = {
            'N': ArmorType.NONE,
            'L': ArmorType.LIGHT,
            'M': ArmorType.MEDIUM,
            'H': ArmorType.HEAVY
        }
        armor = armor_map.get(data['armor'], ArmorType.NONE)
        
        # Create weapon instances
        weapons = []
        for w_data in data['weapons']:
            weapon = Weapon(
                name=w_data.name,
                range=w_data.range,
                penetration=w_data.penetration,
                fortification_damage=w_data.fortification_damage,
                keywords=w_data.keywords.copy()
            )
            weapons.append(weapon)
        
        unit = Unit(
            unit_id=unit_id,
            name=unit_name,
            movement=data['movement'],
            armor=armor,
            control=data['control'],
            health=data['health'],
            max_health=data['health'],
            weapons=weapons,
            abilities=data['abilities'].copy(),
            tags=data['tags'].copy(),
            position=position,
            owner=owner
        )
        
        return unit
    
    def load_all_regiments(self):
        """Load all available regiments"""
        if not os.path.exists(self.units_path):
            return
        
        for regiment_dir in os.listdir(self.units_path):
            regiment_path = os.path.join(self.units_path, regiment_dir)
            if os.path.isdir(regiment_path):
                units = self.load_regiment(regiment_dir)
                self.unit_database.update(units)
    
    def get_available_units(self) -> List[str]:
        """Get list of all available unit names"""
        return list(self.unit_database.keys())
    
    def get_unit_info(self, unit_name: str) -> Optional[Dict]:
        """Get unit information"""
        return self.unit_database.get(unit_name)


# Fallback: Hardcoded Ordax Regiment units
ORDAX_UNITS = {
    "Rookie Squad": {
        "name": "Rookie Squad",
        "movement": 2,
        "armor": "N",
        "control": 2,
        "health": 4,
        "weapons": [
            {
                "name": "5.56×45mm NATO",
                "range": 2,
                "penetration": {"N": "3+", "L": "13+", "M": "NA", "H": "NA"},
                "fortification_damage": 0,
                "keywords": ["Assault"]
            }
        ],
        "abilities": [],
        "tags": ["Infantry"]
    },
    "M24 Grizzly": {
        "name": "M24 Grizzly",
        "movement": 2,
        "armor": "M",
        "control": 0,
        "health": 4,
        "weapons": [
            {
                "name": "50mm AC",
                "range": 2,
                "penetration": {"N": "4-", "L": "2+", "M": "10+", "H": "NA"},
                "fortification_damage": 1,
                "keywords": ["Linked"]
            },
            {
                "name": "7.62mm MG",
                "range": 2,
                "penetration": {"N": "1+", "L": "11+", "M": "NA", "H": "NA"},
                "fortification_damage": 0,
                "keywords": ["Linked"]
            }
        ],
        "abilities": [],
        "tags": ["Vehicle", "IFV"]
    },
    "M14 Puma": {
        "name": "M14 Puma",
        "movement": 3,
        "armor": "L",
        "control": 0,
        "health": 3,
        "weapons": [
            {
                "name": "105mm HEAT",
                "range": 2,
                "penetration": {"N": "NA", "L": "8-", "M": "4+", "H": "9+"},
                "fortification_damage": 0,
                "keywords": ["Assault"]
            }
        ],
        "abilities": [],
        "tags": ["Vehicle", "Light Tank"]
    },
    "M29 Vindicator": {
        "name": "M29 Vindicator",
        "movement": 2,
        "armor": "M",
        "control": 0,
        "health": 2,
        "weapons": [
            {
                "name": "130mm APFSDS",
                "range": 5,
                "penetration": {"N": "NA", "L": "NA", "M": "7-", "H": "3+"},
                "fortification_damage": 0,
                "keywords": ["Long", "Frontal"]
            }
        ],
        "abilities": ["Sloped, NERA Armor", "Sturdy"],
        "tags": ["Vehicle", "SPG"]
    }
}
