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


    def run(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.update()
            self.clock.tick(self.fps)




 def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                if event.key == pg.K_f:
                    pg.display.set_mode(
                        c.SCREEN_SIZE, pg.HWSURFACE | pg.FULLSCREEN
                    )
                elif event.key == pg.K_u:
                    pg.display.set_mode(c.SCREEN_SIZE)
            elif event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pos = pg.mouse.get_pos()
                (
                    self.mouse_click[0],
                    _,
                    self.mouse_click[1],
                ) = pg.mouse.get_pressed()
                # self.mouse_click[0]表示左键，self.mouse_click[1]表示右键
                print(
                    f'点击位置: ({self.mouse_pos[0]:3}, {self.mouse_pos[1]:3}) 左右键点击情况: {self.mouse_click}'



    def update(self):
        # 自 pygame_init() 调用以来的毫秒数 * 游戏速度倍率，即游戏时间
        self.current_time = pg.time.get_ticks() * self.game_info[c.GAME_RATE]

        if self.state.done:
            self.flip_state()

        self.state.update(
            self.screen, self.current_time, self.mouse_pos, self.mouse_click
        )
        self.mouse_pos = None
        self.mouse_click[0] = False
        self.mouse_click[1] = False
