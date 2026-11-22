# List of Entities

**Entity**
- Position
- Speed

**Pacman**
- Position
- Direction
- Speed (higher than ghost)
- Control by AWSD directions
- *Ivencibility?*

**Ghosts**
- Position
- Speed
- Type
- Color
- State:
    - Scatter: Return to their corners to make a small break each x time
    - Chase: Search and hunt pacman
    - Frightened: Run randomly away from pacman (slow speed, no damage)
    - Eaten: Eyes running to their corner.
    - Sleep: Closed eyes without move it.
- Behavior

## Original types:

**Blinky**
-- The Shadow
color: Red
Behavior: 
    Accelerate when are less pacgums or pellers.\
	Random movement for x seconds, than chase.
	When accelerate than chase only.

**Pinky**
-- The Speedy
color: Pink
Behavior: 
    Try to calculate Pacman movement to move in front of him.
    pathfinder to 4 pos in front of pacman.

**Inky**
-- The Bashful
color: Cyan
Behavior: 
    Use Pacman position and Blinky to trap him.
    Use blink pos and 2 pos in front of pacman
    Try to leave pacman between blinky and him.

**Clyde**
-- The Pokey
color: Orange
Behavior: 
    Chase Pacman but if is close, run to the bottom-left corner.
    If is over 8 pos far of pacman, works like Blinky
    If is less than 8 pos, target left bottom corner

*Ghost never stop to move.

## Extra types

**Sue**
Added in Ms. Pac-Man (1982).
color: purple/orange
Behavior: 
    Target pacman from behind.
    Chasing pacman until 8 tiles and retreat
    Can act like BLinky (Leader)

**Tim**
Added in Jr. Pac-Man (1983).
color: Peach
Behavior: 
    Like Clyde, priorize vertical movement.

*//We are not add jumping stuff*
**Funky**
Added in Pac-Mania (1987).
color: Green
Behavior: 
    Can jump over pacman path (Because this motherfk pacman jumps too)
    He patrols strictly horizontally in coordinated groups??

**Spunky**
Added in Funky in Pac-Mania (1987).
color: Grey
Behavior:
    Like Funky but jumper more high?
    Sleep, when pacman is at 4 blocks, wakeup and chase him relentlessly.

**Kinky**
Added in Pac-Man Arrangement (1996).
color: Yellow/Gold 
Behavior:
    Permanently Frightened.
    Chase other ghost to power up them.
    Give them more attacks:
        Blinky -> Charge in horizontal line
        Pinky -> Jump walls
        Inky -> Duplicate in the opposite side of the map
        Clyde -> Became bigger and spit pac-dots of 20 points.

**Orson**
Added in Pac-Man World (1999).
color: Greenish-grey
Behavior:
    Use a robot to exterminate???
    Powerpellet allow only to damage the robot, not the ghost.

**Glitchy**
Added  in Pac-Man 256 (2015).
color: multicolor, bugged style
Behavior:
    Moves erratically and randomly teleport short distances next to pacman
    Umpredectible.

**Punky**
Added in The Sandbox Evolution (2017) Pac-Man crossover.
color: pink variant
Behavior:
    mimic pink behaviour.
    Keep stationary in a line of sight before suddenly charging straight toward Pac-Man
    On powerpellet cancel his charge.

**Dinky**
Added in Baby Pac-Man (1982).
color: Blue
Behavior:
    Primarily a lore and pinball-hybrid character rather than a standard maze AI, acting as a mischievous younger cousin to the main Ghost Gang. 


## Horror ghosts (Pacm̬̦̩̹̌͢a̪͓̮̼͍̗͑̿ͫn̛̥͈ͅ & Darkest Hours).
https://www.youtube.com/watch?v=amaVx5Uh2tk

This mode Pacman have vision of all points from him. Randomly all map is revealed.

**Blindy**
color: Light blue
Behavior:
    He is completely blind to sight and wanders aimlessly, remaining invisible outside of your direct line of sight. However, if he hears sound or detects proximity, he charges rapidly.
    On powerpellet is not invisible.

**Screamy**
color: Red
Behavior:
    Represents Blinky's skull-faced counterpart. He stalks the player aggressively, and his face glows yellow right before he unleashes a high-speed charge attack.
    Cancel his charge, emit distorted audio

**Slendy**
color: Orange
Behavior:
    Represents Clyde's stitched-face counterpart. Normally sluggish, he enters an "enraged" state when provoked, turning bright yellow as his stitched eyes and mouth tear open to pursue the player.
    Force to be stop.

**Old One**
color: Eldritch
Behavior:
    Functions as a heavyweight hazard in Darkest Hours alongside the trio above, patrolling key areas with devastating area-denial attacks.
    Imnune to Power Pellets.


## Last

**nightmare**
Color: something dark, own sprite.
Behavior:
    Chasing always, increase slowly the speed.
    Doesn't care about walls.


*On dead, transparent eyes move to the cornet.
few seconds before respam, flash the body, faster when is going to spam.