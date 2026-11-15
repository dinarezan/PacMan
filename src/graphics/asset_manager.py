"""Cached, group-aware loading of images, sounds and fonts for pygame."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterator

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

log = logging.getLogger(__name__)

DEFAULT_GROUP = "default"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
SOUND_EXTENSIONS = (".wav", ".ogg")  # ? ADD MP3 -> Require extra files.


class _SilentSound:
    """Stand-in used when the mixer is unavailable or a sound is missing."""

    def __getattr__(self, name: str) -> Any:
        return lambda *args, **kwargs: None


class AssetManager:
    """
    Load assets once, share them, and release them by group.

    Assets are organised in *groups* (for example ``"menu"``,
    ``"map_classic"`` or ``"enemies"``). A group is loaded when a state
    needs it and unloaded when it is no longer needed, so memory only
    holds what the current screen uses. An asset that belongs to several
    groups stays in memory until the last of them is unloaded.

    Assets are addressed by *name*: the path relative to `base_dir`,
    without extension, using ``/`` (e.g. ``"enemies/ghost"``).

    Parameters
    ----------
    base_dir : str or pathlib.Path, optional
        Root folder of all assets. Default is the current directory.
    strict : bool, optional
        If True, a missing or unreadable asset raises an exception. If
        False (default), a warning is logged and a placeholder is used
        (a magenta/black square, or a silent sound), so the game keeps
        running.

    Notes
    -----
    Images need an initialised display (``pygame.display.set_mode``)
    because they are converted to the display's pixel format, which makes
    drawing them much faster.

    Examples
    --------
    >>> assets = AssetManager("assets")
    >>> assets.load_group("menu")                       # assets/menu/
    >>> assets.load_group("map_classic", "maps/classic")
    >>> ghost = assets.get_image("enemies/ghost", (40, 40), group="enemies")
    >>> assets.unload_group("map_classic")              # free that map style

    A loading screen can draw progress between files:

    >>> for done, total in assets.iter_load_group("enemies"):
    ...     draw_progress_bar(done / max(total, 1))
    """

    def __init__(self, base_dir: str | Path = ".",
                 strict: bool = False) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.strict = strict
        # name -> {(alpha, scale, smooth): Surface}; scale None = original
        self._images: dict[str, dict[tuple, pygame.Surface]] = {}
        self._sounds: dict[str, Any] = {}
        self._fonts: dict[tuple, pygame.font.Font] = {}
        self._paths: dict[tuple[str, str], Path] = {}
        self._aliases: dict[str, str] = {}
        # group -> {(kind, name)}
        self._groups: dict[str, set[tuple[str, str]]] = {}

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------
    def load_group(self, group: str, folder: str | Path | None = None,
                   recursive: bool = True, alpha: bool = True) -> int:
        """
        Load every image and sound of a folder into a group.

        Parameters
        ----------
        group : str
            Group name.
        folder : str or pathlib.Path, optional
            Folder to scan, relative to `base_dir`. Defaults to `group`.
        recursive : bool, optional
            Also scan sub-folders. Default is True.
        alpha : bool, optional
            Convert images keeping per-pixel transparency. Use False for
            opaque images such as backgrounds (faster to draw). Default
            is True.

        Returns
        -------
        int
            Number of files in the folder.
        """
        total = 0
        for _, total in self.iter_load_group(group, folder, recursive,
                                             alpha):
            pass
        return total

    def iter_load_group(self, group: str, folder: str | Path | None = None,
                        recursive: bool = True,
                        alpha: bool = True) -> Iterator[tuple[int, int]]:
        """
        Load a group file by file, yielding progress after each one.

        Same parameters as `load_group`. Iterate it from the main loop
        (or a loading screen) to keep the window responsive.

        Yields
        ------
        tuple of int
            ``(files_done, files_total)``; the first value yielded is
            ``(0, total)``.
        """
        files = self._scan(group if folder is None else folder, recursive)
        total = len(files)
        members = self._groups.setdefault(group, set())
        yield 0, total
        for done, (kind, path) in enumerate(files, 1):
            name = self._name_of(path)
            self._paths[(kind, name)] = path
            members.add((kind, name))
            if kind == "image":
                self._load_image(name, alpha)
            else:
                self._load_sound(name)
            yield done, total

    def unload_group(self, group: str) -> int:
        """
        Release a group's assets.

        Assets that also belong to another loaded group are kept.

        Parameters
        ----------
        group : str
            Group name.

        Returns
        -------
        int
            Number of assets actually freed.
        """
        members = self._groups.pop(group, None)
        if not members:
            return 0
        still_used: set[tuple[str, str]] = set()
        for other in self._groups.values():
            still_used |= other

        freed = 0
        for kind, name in members - still_used:
            store = self._images if kind == "image" else self._sounds
            if store.pop(name, None) is not None:
                freed += 1
        return freed

    def has_group(self, group: str) -> bool:
        """Return True if `group` is currently loaded."""
        return group in self._groups

    def clear(self) -> None:
        """Release everything."""
        self._images.clear()
        self._sounds.clear()
        self._fonts.clear()
        self._paths.clear()
        self._aliases.clear()
        self._groups.clear()

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------
    def get_image(self, name: str, scale: tuple[int, int] | None = None, *,
                  alpha: bool = True, smooth: bool = False,
                  group: str | None = None) -> pygame.Surface:
        """
        Return a cached image, loading it on first use.

        Scaled versions are made from the cached original (never from
        disk again) and cached too.

        Parameters
        ----------
        name : str
            Asset name, e.g. ``"enemies/ghost"``.
        scale : tuple of int, optional
            Target ``(width, height)``. Must be a tuple (hashable).
        alpha : bool, optional
            Keep per-pixel transparency. Default is True.
        smooth : bool, optional
            Use smooth scaling (better quality, slower). Default False.
        group : str, optional
            Group that owns the image. If omitted, an image that is not
            in any group goes to the ``"default"`` group.

        Returns
        -------
        pygame.Surface
            The image. Do not modify it; copy it first if you need to.
        """
        # Fast path: this is called every frame in the game loop.
        entry = self._images.get(self._aliases.get(name, name))
        if entry is not None and group is None:
            surface = entry.get((alpha, scale, smooth if scale else False))
            if surface is not None:
                return surface

        canonical = self._canonical("image", name)
        surface = self._load_image(canonical, alpha, scale, smooth)
        self._track(group, "image", canonical)
        return surface

    def get_sound(self, name: str, group: str | None = None) -> Any:
        """
        Return a cached sound, loading it on first use.

        Parameters
        ----------
        name : str
            Asset name, e.g. ``"sfx/chomp"``.
        group : str, optional
            Group that owns the sound (see `get_image`).

        Returns
        -------
        pygame.mixer.Sound
            The sound, or a silent stand-in if the mixer is not
            initialised or the file is missing (non-strict mode).
        """
        sound = self._sounds.get(self._aliases.get(name, name))
        if sound is not None and group is None:
            return sound

        canonical = self._canonical("sound", name)
        sound = self._load_sound(canonical)
        if canonical in self._sounds:
            self._track(group, "sound", canonical)
        return sound

    def get_font(self, size: int, name: str | None = None) -> pygame.font.Font:
        """
        Return a cached font.

        Parameters
        ----------
        size : int
            Font size in pixels.
        name : str, optional
            Font file relative to `base_dir`. If None, pygame's default
            font is used.

        Returns
        -------
        pygame.font.Font
            The font. Fonts are not tied to groups; `clear` releases them.
        """
        key = (name, size)
        if key not in self._fonts:
            path = str(self.base_dir / name) if name else None
            self._fonts[key] = pygame.font.Font(path, size)
        return self._fonts[key]

    def stats(self) -> dict[str, int]:
        """
        Return a summary of what is in memory.

        Returns
        -------
        dict
            Counts of ``images`` (original files), ``image_variants``
            (all cached surfaces), ``sounds``, ``fonts`` and ``groups``,
            plus ``image_bytes``, the approximate pixel memory in bytes.
        """
        surfaces = [s for e in self._images.values() for s in e.values()]
        return {
            "images": len(self._images),
            "image_variants": len(surfaces),
            "sounds": len(self._sounds),
            "fonts": len(self._fonts),
            "groups": len(self._groups),
            "image_bytes": sum(s.get_width() * s.get_height()
                               * s.get_bytesize() for s in surfaces),
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _abs(self, folder: str | Path) -> Path:
        path = Path(folder)
        return path if path.is_absolute() else self.base_dir / path

    def _name_of(self, path: Path) -> str:
        """Return the canonical name of a file (relative, no extension)."""
        path = path.resolve()
        try:
            path = path.relative_to(self.base_dir)
        except ValueError:
            pass
        return path.with_suffix("").as_posix()

    def _scan(self, folder: str | Path,
              recursive: bool) -> list[tuple[str, Path]]:
        """List ``(kind, path)`` for every supported file in a folder."""
        root = self._abs(folder)
        if not root.is_dir():
            if self.strict:
                raise FileNotFoundError(f"Asset folder not found: {root}")
            log.warning("Asset folder not found: %s", root)
            return []
        found: list[tuple[str, Path]] = []
        for path in sorted(root.rglob("*") if recursive else root.glob("*")):
            suffix = path.suffix.lower()
            if not path.is_file():
                continue
            if suffix in IMAGE_EXTENSIONS:
                found.append(("image", path))
            elif suffix in SOUND_EXTENSIONS:
                found.append(("sound", path))
        return found

    def _resolve(self, kind: str, name: str) -> Path:
        """Find the file for `name`; raise FileNotFoundError if absent."""
        path = self._paths.get((kind, name))
        if path is not None:
            return path
        extensions = IMAGE_EXTENSIONS if kind == "image" else SOUND_EXTENSIONS
        candidate = self._abs(name)
        if candidate.suffix.lower() in extensions and candidate.is_file():
            return candidate
        for extension in extensions:
            with_ext = Path(str(candidate) + extension)
            if with_ext.is_file():
                return with_ext
        raise FileNotFoundError(f"{kind} not found: {name}")

    def _canonical(self, kind: str, name: str) -> str:
        """Map any accepted spelling of `name` to its canonical name."""
        try:
            path = self._resolve(kind, name)
        except FileNotFoundError:
            return name  # the loader reports the problem
        canonical = self._name_of(path)
        self._paths[(kind, canonical)] = path
        if canonical != name:
            self._aliases[name] = canonical
        return canonical

    def _owned(self, kind: str, name: str) -> bool:
        return any((kind, name) in members
                   for members in self._groups.values())

    def _track(self, group: str | None, kind: str, name: str) -> None:
        """Record that `group` uses an asset (default group if unowned)."""
        if group is None:
            if self._owned(kind, name):
                return
            group = DEFAULT_GROUP
        self._groups.setdefault(group, set()).add((kind, name))

    # ? Adapt image generator from Amazing??
    @staticmethod
    def _placeholder() -> pygame.Surface:
        """Visible 'missing image' marker."""
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 255))
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, 16, 16))
        pygame.draw.rect(surface, (0, 0, 0), (16, 16, 16, 16))
        return surface

    def _read_image(self, name: str, alpha: bool) -> pygame.Surface:
        """Read and convert an image from disk."""
        if pygame.display.get_surface() is None:
            raise RuntimeError(
                "Call pygame.display.set_mode() before loading images.")
        try:
            image = pygame.image.load(str(self._resolve("image", name)))
        except (FileNotFoundError, pygame.error) as error:
            if self.strict:
                raise
            log.warning("Could not load image %r: %s", name, error)
            return self._placeholder()
        return image.convert_alpha() if alpha else image.convert()

    def _load_image(self, name: str, alpha: bool,
                    scale: tuple[int, int] | None = None,
                    smooth: bool = False) -> pygame.Surface:
        """Return an image (or scaled variant), loading it if needed."""
        entry = self._images.get(name)
        base_key = (alpha, None, False)
        base = entry.get(base_key) if entry else None
        if base is None:
            base = self._read_image(name, alpha)
            entry = self._images.setdefault(name, {})
            entry[base_key] = base
        if scale is None:
            return base

        key = (alpha, scale, smooth)
        scaled = entry.get(key)
        if scaled is None:
            resize = (pygame.transform.smoothscale if smooth
                      else pygame.transform.scale)
            scaled = entry[key] = resize(base, scale)
        return scaled

    def _load_sound(self, name: str) -> Any:
        """Return a sound, loading it if needed."""
        sound = self._sounds.get(name)
        if sound is not None:
            return sound
        if not pygame.mixer.get_init():
            log.warning("Mixer not initialised; %r will be silent", name)
            return _SilentSound()  # not cached: may work once mixer is up
        try:
            sound = pygame.mixer.Sound(str(self._resolve("sound", name)))
        except (FileNotFoundError, pygame.error) as error:
            if self.strict:
                raise
            log.warning("Could not load sound %r: %s", name, error)
            sound = _SilentSound()
        self._sounds[name] = sound
        return sound
