# Core Concepts
## Army
Each player has an army, composed by several Units from up to 3 Regiments. 

## Regiment
A collection of Units that are thematically and mechanically similar. Each player can have up to 3 Regiments in their Army, and can only use Units from the selected Regiments.
Regiments have dedicated Abilites and Stratagems.

## Unit
Representing fighters, each Unit has an associated Datasheet and Regiment. 
Each unit will occupy some space on the map, and they cannot overlap.

## Datasheet
All the data of a Unit is stored in a Datasheet. Each has various components:
- MACH: Movement, Armor, Control and Health.
- Tags: Various tags for identification and characterization.
- Weapons: A list of the Unit's Weapons and their stats.
- Abilities: A list of the Unit's Abilities. 

## Weapons
Each Units can have Weapons attached to it. These are fixed and displayed on the Unit's Datasheet.
Each Weapon has:
- A Caliber and Type, denoted by the first and last parts of its Name;
- A Range, Penetration for each Armor value and a Fortification damage value.
- A list of Keywords.

## Abilities
Abilities can be of three types, Core, Regiment and Unit.
- Core Abilities are generic, usually have an associated Rule and are referenced only by a short expression
- Regiment Abilities are exclusive to a single Regiment, and are shared by all Units of a Regiment.
- Unit abilities are usually exclusive to one Unit.

## Keywords
Keywords are short phrases with an associated Rule. These can be a buff, debuff or change to the way Units or Weapons work.
# Starting the Game

## Presentation Step
Each player must present all units on their army to each other

## Mission Choosing
Each player takes turns banning a mission of their choosing.
The last remaining mission is the active one.

## Map Setup
Based on the active mission, setup the map for it.
Maps are hexagonal with 8 tiles on each side (169 tiles total)

## Set Player Order
Randomly choose a player, that player chooses if they go first or second.

## Deploy armies
Each player, starting with the first, deploy a unit or structure of their choosing at a time.
The first deployment is made on any square of their edge, and the following can also be made on any tiles adjacent to already deployed on, up to 3 tiles from the edge. The players can deploy less than their capacity.
When deploying a unit, also choose how much ammunition it starts with.
Afterward, each player can finish their remaining capacity by leaving units in the Reserves, and the remaining units are considered out of battle.

## Starting Actions
Each player, in order, make any "Before the battle" actions.
Then, the Main Phase starts, with the first player beginning.





# Main Phase

## Actions
Each turn the active player gets a Major and a Minor Action to spend on units. These can be spent in any unit, within the following restrictions:
- The Major Action must be spent first, or not spent at all.
- A unit cannot shoot twice with the same weapon.

## Moving
Move the unit up to the specified value. If none was specified, move it up to its M. Restrictions are based on unit type and are explained in the "Extra Rules / Movement Restrictions" section.
- Moving into buildings and into enemy tiles does not have an extra cost.
- Moving out of Enemy Occupied Buildings and enemy tiles costs double movement.

## Shooting
Attacking fortifications works differently, and is explained in the "Fortifications / Fortification Damage" section. 
- The target unit must be within range of the weapon (denoted by R) and within LoS.
- Check the targets Armor and the weapon's Penetration Roll.
- Roll for penetration, then add any effect onto the rolled value
- In case of success, remove 1 H from it.

## Capturing


# Actions
Actions are the main ways players interact with their units. There are 3 types of actions: Major, Minor and Special. 
Spending a Major action on a unit is called Majoring a unit , and spending a Minor action on a unit is called Minoring a unit.
For example, "Major a unit to Advance" means spending a Major action on a unit to do the Advance action, moving up to it's M stat.
## Major

### Move Majors
- Advance: Move up to the unit's M stat.
- Embark: Embark into a Transport, by moving up to 1
- Disembark: Disembark from a Transport and moving up to 1.

### Attack Majors
- Salvo: Shoot a unit. Repeatable for each weapon the unit has that can shoot.
- Capture: Capture a Building, by turning its Pips to your color. When turning pips this way, if you turn a neutral one, instead turn two.


## Minor
### Move
Move 1. Cannot be used by units with 1 M or units that already moved this turn.

### Consolidate
Move up to 2 units into this units tile. Those units can only move 1.

### Control
Capture a Building, by turning its Pips to your color. Cannot be used on a unit that already Captured a building this turn.

### Shot
Shoot a single weapon. This shot is at most a 4- or 9+, depending if it would be rolling up or down.
Cannot be used by units that already shot this turn.



## Special

### Overwatch
Spend a Major and a Minor, choose a unit and an arc it can shoot to. The unit goes into Focus.
When an enemy enters this unit Range within the arc, it may shoot the enemy.
# Map

## Tiles
The map is made up of a grid of hexagonal tiles. These tiles can be empty, have buildings, ally or enemy units in any combination.
- Any tile with a building in considered a Fortification Tile and can be targetted for Shooting
- Tiles with enemy units or enemy deployed buildings are considered Enemy Tiles
- Fortification Tiles with units inside are considered Occupied Buildings.

## Fortifications

### Fortification Damage
When damaging a fortification, remove pips one at a time, always removing a pip of the most popular color. If there is a tie, remove a pip with the following priority, only removing from tied colors : neutral > enemy > ally

If there is an enemy unit inside, for each pip removed from the fortification, roll a d12. For each 9+, that unit looses 1 H.


### Fortification Health Checks
When a fortification has less health than the total of the units inside, each make attacks until the total of pips is lower or equal to the fortification's. The attacks are made in order of unit H, lower to higher, and starting with allied units in case of tie.



# Extra Rules

## Movement
### Infantry
Infantry has full freedom of movement.

### Vehicles
In each movement a vehicle does, it can turn once in addition to moving forward 1 tile.
N, L and M Vehicles can turn and move in any order, but H must move forward and then turn.
Instead of moving, a vehicle can remain stationary and only turn. This still costs 1 tile of movement
Vehicles can also move backwards, following the same rules, but each tile moved costs double.

A Vehicle can only move into a tile if the slots it would occupy (given its future direction) are free. In this case, for non-H vehicles, consider the slots it would occupy after turning after the movement (and if it didn't already used this move's turning)

### Aircraft
Aircraft must always move when activated, and follows the same rules as Vehicles, with the exception that it cannot move backwards and cannot only turn.
Keep in mind that a lot of Aircraft Attack actions are influenced by how you move, not simply your final position.
2 Aircraft units cannot occupy the same position at any time. If they would, destroy both colliding units

### Hover
Hover units have full freedom of movement

## Rolling

### Rolling Up
When the table show a number followed by a "+".
For this roll, you need to roll the shown number or higher.

### Rolling Down
When the table show a number followed by a "-".
For this roll, you need to roll the shown number or lower.