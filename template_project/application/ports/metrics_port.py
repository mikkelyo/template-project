"""Port for recording operational metrics."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class MetricsPort(Protocol):
    """Hides the metrics backend and guarantees telemetry never breaks a request."""

    def increment(self, *, name: str, value: int = 1) -> None:
        """Add ``value`` to the counter ``name``.

        Parameters
        ----------
        name : str
            Counter name.
        value : int, optional
            Amount to add.
        """
        ...

    def record_duration(self, *, name: str, seconds: float) -> None:
        """Record how long an operation took.

        Parameters
        ----------
        name : str
            Timer name.
        seconds : float
            Measured duration.
        """
        ...
