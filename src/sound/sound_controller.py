import logging

import pygame

from src.graphics.asset_manager import AssetManager


log = logging.getLogger(__name__)


class SoundController:
    def __init__(self, assets: AssetManager) -> None:
        self.assets = assets

    def play(self, name: str) -> None:
        sound = self.assets.get_sound(f"audio/{name}")
        channel = sound.play()
        if channel is None and pygame.mixer.get_init() and isinstance(
                sound, pygame.mixer.Sound):
            channel = pygame.mixer.find_channel(True)
            if channel is None:
                log.warning("No audio channel available for %r", name)
            else:
                channel.play(sound)

    def start_music(self) -> None:
        if not pygame.mixer.get_init():
            log.warning("Mixer not initialised; soundtrack will be silent")
            return
        path = self.assets.base_dir / "audio" / "soundtrack_loop_1.ogg"
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(-1)
        except (pygame.error, OSError) as error:
            log.warning("Could not play soundtrack %s: %s", path, error)

    def stop_music(self) -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
