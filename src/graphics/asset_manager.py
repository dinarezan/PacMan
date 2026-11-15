import os
import pygame

# ! Proto structure for Cache and assets managing

# TODO add method from init and charge all assets here to take it.
# * Take assets by groups: Maps tiles with x style, enemies, items, etc...

# 1. Inint display with pygame.
# 2. Find all assets.
# 3. Turn into surfaces (.convert_alpha())
# 4. Cache assets (surfaces or wathever)
# 5. .copy() on cache surfaces to modify pixels (effects)
# 6. Use @functools.lru_cache decorator maybe -> Check it.


#pygame.init()
#screen = pygame.display.set_mode((1280, 720))

## Initialize and preload
#assets = AssetManager()
#assets.preload_folder("assets/sprites")
#assets.preload_folder("assets/audio")

## Inside a game entity
#class Player(pygame.sprite.Sprite):
#    def __init__(self, assets):
#        super().__init__()
#        # Instant retrieval from memory
#        self.image = assets.get_image("assets/sprites/hero.png", scale=(64, 64))
#        self.jump_sfx = assets.get_sound("assets/audio/jump.wav")


class AssetManager:
    """All images are cached once loaded and reused if you want to use the
    same image again and again.
    """
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def preload_folder(self, folder_path):
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        self.get_image(full_path)
                    elif file.endswith(('.wav', '.ogg')):
                        self.get_sound(full_path)

    def get_image(self, path, scale=None):
        """Create a unique key for both path and scale"""
        cache_key = (path, scale)

        if cache_key not in self.images:
            # Load images and optimice as surface format
            image = pygame.image.load(path).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            self.images[cache_key] = image

        return self.images[cache_key]

    def get_sound(self, path):
        """..."""
        if path not in self.sounds:
            self.sounds[path] = pygame.mixer.Sound(path)
        return self.sounds[path]
