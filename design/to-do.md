

# Requirements

## General Rules

- [ ] Python 3.10 or >
- [ ] flake8
- [ ] mypy
- [ ] Catch all exceptions (NO CRASH)
- [ ] Not leaks or lost connection resources.
- [ ] Include docs strings in fn and classes by [PEP 257](https://peps.python.org/pep-0257/)

## Makefile

- [ ] install
- [ ] run
- [ ] debug
- [ ] clean
- [ ] lint
- [ ] lint-strict 

## Additional

- [ ] Tests
- [ ] .gitignore
- [ ] venv

## Mandatory

- [ ] Custon config by file (JSON with coments) -> Game parametters
- [ ] Error handli, no crash.
- [ ] Level generation by external A-Maze-ing package.
- [ ] Persistent highscore system -> Json file in the disk.
- [ ] Polished graphical UI with Menu, game view, game-over, etc.
- [ ] Cheat mode for evaluation purpose (change live, points, level, *special guess*).

- [ ] Main loop: Main Menu -> Start Game -> Result -> Add name to score -> Back to menu

## Specifications

- [ ] To lunch it: `python3 pac-man.py config.json `.
- [ ] 1 argument -> Configuration json file (no matter name)
- [ ] Handle any error with proper message.
- [ ] Configuration file:
    - [ ] Handle comments with `#`
    - [ ] Support additional languages comments "c, c++"
    - [ ] Documented into README
    - [ ] highscore_filename
    - [ ] level (array of multiple levels)
    - [ ] width, height for each level
    - [ ] lives: 3
    - [ ] pacgum: 42
    - [ ] points_per_pacgum: 10
    - [ ] points_per_super_pacgum: 50
    - [ ] points_per_ghost: 200
    - [ ] seed: 42
    - [ ] level_max_time: 90
    - [ ] Handle missing values: safe Default and continue, logs & uknown keys ignored.
- [ ] Maze generator:
    - [ ] Use their package as-is.
    - [ ] Adapted to their interface.
    - [ ] Parameter PERFECT -> FALSE
    - [ ] Handle generation Errors.
- [ ] Score system:
    - [ ] Document on README
    - [ ] Stored in a choose root.
    - [ ] Robust file errors (missing or invalid).
    - [ ] Handle player names up to 10 alphanum with ' '.
    - [ ] Handle positive integers scores.
    - [ ] Track only the 10 highest scores.
    - [ ] Read at the start and update at the end.
    - [ ] Ask players enter name when finish with their score.
    - [ ] Display score in main menu

## Game Specifications

**LEVEL STRUCTURE**
- [ ] Level with walls and corridors by A-MAZE-ing package
- [ ] First level with fixed seed (42). After randomly.
- [ ] pacgums (dots) in most corridors. *Not all:?*
- [ ] Super-pacgums (powerups) in the 4 corners.
- [ ] 4 ghosts, one per corner (next to the Super-pacgums).
- [ ] Starts at the center.
**PLAYER**
- [ ] Player can go around corridors, not walls.
- [ ] 4 directions AWSD.
- [ ] 3 lives.
- [ ] Loses a live when a ghost touch.
- [ ] Respawn at the middle (reset ghost positions).
- [ ] End game when no lives.
- [ ] Win level when all Super pacgums are eaten.
- [ ] Win game when all levels are passed.
- [ ] pacgums increase by X.
- [ ] SuperPacgums by Y and make ghost edible for short time.
- [ ] Eat ghost increase score by z points. *(ZYX like 353??)*
- [ ] Score no decreae.
**GHOSTS**
- [ ] Move autonomously through corridors.
- [ ] Chase the player when not edible. Define chase behavior.
- [ ] Run away from player when are edible.
- [ ] Respawn to their corned after a while when eaten (5-10s..)
**CHEAT MODE**
- [ ] Activate or disable.
- [ ] Invicibility.
- [ ] Level Skip
- [ ] Ghost freeze
- [ ] Extra Lives
- [ ] Increase Speed
- [ ] More stuff??
    - Choose a level.
    - Change the puntuation.
    - Make ghost perma edibles.
    - Add weapon to Pacman to shot.
    - Delete ghost from level (disabled them)
    - Make them always run away from you.
    - Invoque the nightmare to chase you (dont die, dont care about walls, always it follow you).
**GAME PROGRESSION**
- [ ] Multiple levels, min 10.
- [ ] Each level with a time limit.
- [ ] If time ends -> Reset game or levl or lost or... INVOQUE THE NIGHTMARE TO CHASE TO CHASE YOU!!!
- [ ] If complete a level, move to the next one.
- [ ] Keep score and lives between levels.
- [ ] Pause option *(Ghost dance meanwhile??)*.
- [ ] When game ends, final score is displayed, player can enter the name to save it.
- [ ] After finished the game, is returning to the main menu.
**INTERFACE**
- [ ] *Display highest scores Top 3??*
- [ ] Main menu:
    - [ ] Start Game.
    - [ ] View Highscores (top 10).
    - [ ] Instructions.
    - [ ] Exit.
- [ ] HUB in game:
    - [ ] Current score.
    - [ ] Remaining lives.
    - [ ] Current level.
    - [ ] Remaining time.
    - [ ] *Cheat mode activate?*
- [ ] Pause:
    - [ ] Return to the game
    - [ ] Return to the Main menu
- [ ] Game Over:
    - [ ] Display final score.
    - [ ] Prompts the prayer name and save with score.
- [ ] Vitory Screen:
    - [ ] Display final score and contratulatory message.
    - [ ] Prompts the prayer na...
**PACKAGING**
- [ ] Complete game to be installed and launched from public platform as free but unlisted/private build
- [ ] Fully functional package.
- [ ] minimal in-package instructions.
- [ ] Git repository with full source and packaging script/spec at the root.
- [ ] Be ready to generate a fkck package in review or brief.
**EXTRA**
- [ ] Project timeline.
- [ ] Actual profess tracking compared to timeline.
- [ ] Project analysis and associated choises
- [ ] Risk analysis and possible mitigations (*42 pay for this labour?*)
- [ ] Team organization and slavery agreements.
- [ ] Accetable test plan (feature tested, bugs found/fixed).
- [ ] Summary of blocking points or conlficts..
**README**
- [ ] names
- [ ] Description
- [ ] Instructions
- [ ] Resources
- [ ] Usage, feature, technical choices.
- [ ] Configuration
- [ ] highscore
- [ ] Maze generation
- [ ] Implementation
- [ ] General sofrware architecture
- [ ] Project mANAGEMENT.
