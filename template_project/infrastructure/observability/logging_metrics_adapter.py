"""Metrics recorder that writes to the application log."""

from __future__ import annotations

import logging
from logging import Logger


class LoggingMetricsAdapter:
    """Implements :class:`MetricsPort`, so no metrics vendor leaks into use cases.

    Telemetry must never break the request it measures: every method degrades
    silently, falling back to the stdlib logger if the injected one fails.

    Parameters
    ----------
    logger : Logger
        Logger the measurements are written to.
    namespace : str
        Prefix applied to every metric name.
    enabled : bool
        When false, measurements are dropped.
    """

    def __init__(self, *, logger: Logger, namespace: str, enabled: bool) -> None:
        self._logger = logger
        self._namespace = namespace
        self._enabled = enabled

    def increment(self, *, name: str, value: int = 1) -> None:
        """Add ``value`` to the counter ``name``.

        Parameters
        ----------
        name : str
            Counter name, recorded under the configured namespace.
        value : int, optional
            Amount to add.
        """
        self._emit(name=name, measurement=f"count={value}")

    def record_duration(self, *, name: str, seconds: float) -> None:
        """Record how long an operation took.

        Parameters
        ----------
        name : str
            Timer name, recorded under the configured namespace.
        seconds : float
            Measured duration.
        """
        self._emit(name=name, measurement=f"seconds={seconds:.4f}")

    def _emit(self, *, name: str, measurement: str) -> None:
        """Write one measurement, swallowing any failure.

        Parameters
        ----------
        name : str
            Metric name, recorded under the configured namespace.
        measurement : str
            Rendered value of the measurement.
        """
        if not self._enabled:
            return
        try:
            self._logger.info("metric %s.%s %s", self._namespace, name, measurement)
        except Exception:  # telemetry never breaks the request it measures
            logging.getLogger(__name__).warning("Dropped metric %s.", name)
