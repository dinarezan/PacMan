from __future__ import annotations


class SpriteAnimation:
    """
    Looping sequence of frames, each shown for its own duration.

    Handles only the animation times.
    Use `frame` to know which image to draw.

    Parameters
    ----------
    frames : sequence of tuple
        ``(name, seconds)`` pairs in playback order. The sequence loops
        back to the first frame after the last one. Every duration must
        be greater than zero.

    Attributes
    ----------
    frames : list of tuple
        The ``(name, seconds)`` pairs.
    duration : float
        Length of one full loop, in seconds.
    elapsed : float
        Time inside the current loop, in ``[0, duration)``.

    Raises
    ------
    ValueError
        If `frames` is empty or a duration is not positive.

    Examples
    --------
    >>> walk = SpriteAnimation([("a", 0.1), ("b", 0.05), ("c", 0.1),
    ...                         ("b", 0.05)])
    >>> walk.frame
    'a'
    >>> walk.update(0.12)
    >>> walk.frame
    'b'
    """

    def __init__(self, frames: list[tuple[str, float]]) -> None:
        if not frames:
            raise ValueError("An animation needs at least one frame")
        if any(seconds <= 0 for _, seconds in frames):
            raise ValueError("Frame durations must be greater than zero")
        self.frames = list(frames)
        self.duration = sum(seconds for _, seconds in self.frames)
        self.elapsed = 0.0

    @property
    def frame(self) -> str:
        """Name of the frame to show right now."""
        remaining = self.elapsed
        for name, seconds in self.frames:
            if remaining < seconds:
                return name
            remaining -= seconds
        return self.frames[-1][0]       # float rounding at the loop end

    def update(self, dt: float) -> None:
        """
        Advance the animation.

        Parameters
        ----------
        dt : float
            Seconds since the previous call. Large values are fine: the
            animation wraps around instead of skipping or stalling.
        """
        self.elapsed = (self.elapsed + dt) % self.duration

    def reset(self) -> None:
        """Go back to the first frame."""
        self.elapsed = 0.0
