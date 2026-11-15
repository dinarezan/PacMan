import pygame


class RenderMap:

    def __init__(self, map, tileset, size: tuple[int, int]):
        self.map = map
        self.tileset = tileset
        self.size = size


