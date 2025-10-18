# Lead Ledger - AI Development Reference Documentation

## System State Representation

### State Vector Components {AIStateVector}
1. Unit_State[unit_id] = {
   - position: (x, y)
   - orientation: 0-5 (hex directions)
   - current_health: int
   - ammo_remaining: [weapon_id: int]
   - actions_available: {major: bool, minor: bool}
   - movement_used: int
   - in_overwatch: bool
   - overwatch_arc: [hex_ids]
}

2. Map_State[hex_id] = {
   - type: {empty, building, blocked}
   - building_control: [neutral_pips, player1_pips, player2_pips]
   - occupied_by: [unit_ids]
   - blocks_los: bool
}

3. Game_State = {
   - current_turn: 1-50
   - current_cycle: 1-5
   - active_player: {p1, p2}
   - score: {p1: int, p2: int}
   - phase: {deployment, main, end}
}

## Decision Trees and Heuristics

### Action Priority Matrix {AIDecisionMatrix}
```
Priority = base_value + situation_modifiers

Base Values:
- Eliminate enemy unit: 100
- Capture building: 80
- Protect low-health unit: 70
- Position for future capture: 60
- Move to advantageous position: 50
- Overwatch setup: 40

Situation Modifiers:
- Unit's remaining health percentage: -20 to +20
- Expected damage output: 0 to +30
- Risk of counterattack: -40 to 0
- Scoring cycle proximity: 0 to +50
- Strategic position value: -10 to +40
```

### Movement Evaluation {AIMovementCalc}
1. Path Cost Calculation:
   ```
   base_cost = tiles_moved
   modifiers = {
       enemy_zone: x2,
       backward_vehicle: x2,
       into_building: +0
   }
   total_cost = base_cost * Π(applicable_modifiers)
   ```

2. Vehicle Movement Constraints:
   ```
   movement_options = {
       light: {turn_then_move: true, move_then_turn: true},
       medium: {turn_then_move: true, move_then_turn: true},
       heavy: {turn_then_move: false, move_then_turn: true},
   }
   ```

### Combat Resolution Framework {AICombatSystem}

1. Target Selection Priority:
   ```
   target_value = sum([
       base_threat_level: 1-10,
       damage_potential: 0-5,
       position_value: 1-5,
       kill_probability: 0-1,
       strategic_value: 1-5
   ]) * survivability_factor
   ```

2. Weapon Selection Logic:
   ```
   weapon_effectiveness = {
       damage_potential: float,
       range_efficiency: float,
       ammo_efficiency: float,
       opportunity_cost: float
   }
   
   optimal_weapon = max(
       weapon_effectiveness * target_priority * tactical_situation
   )
   ```

3. Position Value Assessment:
   ```
   position_value = sum([
       cover_value: 0-3,
       los_to_objectives: 0-5,
       retreat_paths: 0-3,
       threat_exposure: -5-0,
       support_position: 0-4
   ])
   ```

## Tactical Pattern Recognition {AIPatterns}

### Unit Type Behavior Patterns
```
Infantry = {
    primary_role: ["capture", "hold", "support"],
    positioning: {
        optimal_range: 1-2,
        cover_priority: "high",
        building_affinity: "high"
    },
    engagement_patterns: {
        aggressive: {
            move_threshold: 0.7,
            attack_threshold: 0.5
        },
        defensive: {
            move_threshold: 0.4,
            attack_threshold: 0.7
        }
    }
}

Vehicle = {
    primary_role: ["assault", "support", "control"],
    positioning: {
        optimal_range: 2-3,
        cover_priority: "medium",
        building_affinity: "low"
    },
    movement_patterns: {
        approach_vectors: ["frontal", "flanking"],
        retreat_conditions: ["health < 30%", "surrounded"]
    }
}

```

### Building Control Patterns {AIBuildingControl}
```
control_strategy = {
    early_game: {
        priority: "closest_neutral",
        risk_tolerance: "high",
        resource_commitment: "medium"
    },
    mid_game: {
        priority: "high_value_contested",
        risk_tolerance: "medium",
        resource_commitment: "high"
    },
    late_game: {
        priority: "point_differential",
        risk_tolerance: "variable",
        resource_commitment: "calculated"
    }
}

pip_control_values = {
    neutral_conversion: 2.0,
    enemy_conversion: 1.0,
    defensive_holding: 0.8,
    strategic_position: 1.2
}
```

## Action Sequence Optimization {AIActionOptimization}

### Major-Minor Combinations Analysis
```
optimal_sequences = {
    offensive: [
        {major: "advance", minor: "shot", condition: "assault_weapon"},
        {major: "salvo", minor: "control", condition: "building_adjacent"}
    ],
    defensive: [
        {major: "overwatch", minor: "none", condition: "threatened"},
        {major: "none", minor: "consolidate", condition: "support_needed"}
    ],
    tactical: [
        {major: "advance", minor: "control", condition: "building_capture"},
        {major: "salvo", minor: "move", condition: "repositioning"}
    ]
}

action_value_modifiers = {
    turn_position: 0.8-1.2,
    unit_health: 0.6-1.4,
    tactical_situation: 0.5-1.5,
    scoring_opportunity: 1.0-2.0
}
```

### Future State Prediction {AIStatePrediction}
```
state_evaluation = {
    short_term: {
        turns: 1-3,
        focus: ["immediate_threats", "action_opportunities"],
        weight: 0.5
    },
    medium_term: {
        turns: 4-10,
        focus: ["position_control", "unit_preservation"],
        weight: 0.3
    },
    long_term: {
        turns: 11-50,
        focus: ["scoring_potential", "strategic_control"],
        weight: 0.2
    }
}
```