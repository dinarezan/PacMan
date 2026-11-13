Project/
│
├── assets/                  # Non-code resources
│   ├── sprites/             # Player, enemy, and tile images
│   ├── audio/               # Jump, crash, and click sounds
│   └── fonts/               # Game text fonts
│
├── src/                     # All source code lives here
│   ├── __init__.py          # Makes 'src' a package
│   ├── main.py              # Application entry point (runs the game)
│   │
│   ├── core/                # Engine fundamentals
│   │   ├── engine.py        # Contains the main loop (update/render)
│   │   └── settings.py      # SCREEN_WIDTH, FPS, COLORS
│   │
│   ├── entities/            # Interactive objects
│   │   ├── player.py        # Player class and movement
│   │   └── enemy.py         # Enemy AI behavior
│   │
│   ├── states/              # Game screen managers
│   │   ├── menu.py          # Start screen logic
│   │   └── gameplay.py      # Main action state
│   │
│   ├── Packages/            # ..
/*