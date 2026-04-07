# HITMAN 2D Engine

This project is to create a hitman like engine (topdown view) in python using the pygame library. It will have 2 parts:

- A level creator where we can create, edit and save levels.
- The game itself

## Level creator: (In progress)

This program will provide a tool made with pygame that will allow the user to create a hitman like level. It will also automatically read the Assets folder and import every image in it.
We can move around in the level using the zqsd keys and speed up with lshift.

Diiferent aspect of the level are seperated into multiple modes (using the segmented control on the top): 

- Create / place and delete rooms. We can also chose the floor and wall assets. (Done)
- Assign allowed disguises for each room (To do)
- Place doors to connect rooms (To do)
- Place furnitures with interactive ones like containers or closet (To do)
- Place NPCs / Player / Targets  (To do)
- Provide a path for each NPC. Only assing point of interests and actions, the game's pathfinding will handle the pathing itself (To do)
- Place level exits (To do)

#### This editor is coded to be flexible. Coded some useful widget:

- Button class
- TextField class
- SegmentedControl
- JSONEditor class that can edit any json with a user friendly interface (with textfields)

The settings.py will provide all the menu layout for each mode with minimal coding using a dictionary

## Game (To do)

We will be able to play the level here. Here are the game mechanics:

- The level will end when the player will kill all the targets and exit the level.
- We can take disguises from unconscious / dead bodies so we can blend in in a restricted area.
- Enforcers and suspicious meter ?
- NPC will follow their designated path (using path finding) and do some actions (eat, drink, wait etc). They can interupt their path if something happen (ex: gun shot heard, body found etc)
- A rating stystem to evaluate how stealthy the player is(best one is 'Silent Assassin')

### Rating system

The rating system is inspired by [this video](https://youtu.be/a3edO5zHDos?si=lQQrm_6qLw8i22xI) where the goal is to improve the rating system from the original games.
It will rely on a penalty points system rather than a binary system.

For example a body found will not ruin the Silent Assassin immediatly but add penalty points. When a treshold is excedeed, we will lose the rating and go to the next one.
Some actions can restore some points like getting rid of witnesses or erease camera recording.
