# filepath: /home/raphael/Desktop/escapegame_master/stopwatch.py
"""Simple stopwatch utility with malus support.

Provides both synchronous and async-friendly functions so you can use it
from regular Flask handlers or from async coroutines.

API (sync):
- start(key='global') -> None
- stop(key='global') -> float | None
- elapsed(key='global') -> float | None
- add_malus_minutes(key='global', minutes=1.0) -> None
- get_malus_minutes(key='global') -> int

API (async wrappers):
- async_start(key='global')
- async_stop(key='global') -> float | None
- async_elapsed(key='global') -> float | None

Helper:
- async run_display_loop(key, callback, interval=0.5, stop_event=None)
    calls callback(elapsed_seconds) periodically until cancelled or stop_event set.

Note: in-memory storage — not shared between processes. For multi-process use Redis/DB.
"""
from __future__ import annotations
import time
import threading
import asyncio
from typing import Callable, Optional

_store: dict[str, float] = {}
_wall_start: dict[str, float] = {}
_malus_seconds: dict[str, float] = {}
_lock = threading.Lock()


def start(key: str = 'global') -> None:
    """Start the stopwatch for `key`. Overwrites any existing start time.
    Stores both monotonic (for accurate elapsed) and wall-clock (time.time)
    so the frontend can compute elapsed without server endpoints.
    """
    t = time.monotonic()
    w = time.time()
    with _lock:
        _store[key] = t
        _wall_start[key] = w
        # ensure malus entry exists
        _malus_seconds.setdefault(key, 0.0)


def stop(key: str = 'global') -> Optional[float]:
    """Stop and return elapsed seconds including malus, or None if not started."""
    with _lock:
        t0 = _store.pop(key, None)
        _wall_start.pop(key, None)
        malus = _malus_seconds.get(key, 0.0)
        # keep malus entry (do not remove) so it can be shown on end page if needed
    if t0 is None:
        return None
    return (time.monotonic() - t0) + malus


def elapsed(key: str = 'global') -> Optional[float]:
    """Return elapsed seconds without stopping, including malus, or None if not started."""
    with _lock:
        t0 = _store.get(key)
        malus = _malus_seconds.get(key, 0.0)
    if t0 is None:
        return None
    return (time.monotonic() - t0) + malus


# New helper to expose wall-clock start time to templates/clients
def get_start_wall_time(key: str = 'global') -> Optional[float]:
    """Return the wall-clock (epoch) timestamp when the stopwatch was started, or None."""
    with _lock:
        return _wall_start.get(key)


def add_malus_minutes(key: str = 'global', minutes: float = 1.0) -> None:
    """Increment malus for key by given minutes."""
    seconds = float(minutes) * 60.0
    with _lock:
        _malus_seconds[key] = _malus_seconds.get(key, 0.0) + seconds


def get_malus_minutes(key: str = 'global') -> int:
    """Return the malus in whole minutes (rounded down)."""
    with _lock:
        s = _malus_seconds.get(key, 0.0)
    return int(s // 60)


# Async wrappers for convenience in async code
async def async_start(key: str = 'global') -> None:
    start(key)


async def async_stop(key: str = 'global') -> Optional[float]:
    return stop(key)


async def async_elapsed(key: str = 'global') -> Optional[float]:
    return elapsed(key)


async def run_display_loop(
    key: str,
    callback: Callable[[Optional[float]], None | 'asyncio.Future'],
    interval: float = 0.5,
    stop_event: Optional[asyncio.Event] = None,
):
    """Call `callback(elapsed)` every `interval` seconds until cancelled.

    - callback may be a normal function or an async function.
    - If `stop_event` is provided, the loop exits when it is set.
    - The loop can also be cancelled by cancelling the asyncio Task running it.
    """
    is_async_cb = asyncio.iscoroutinefunction(callback)
    try:
        while True:
            e = elapsed(key)
            try:
                if is_async_cb:
                    await callback(e)  # type: ignore
                else:
                    callback(e)
            except Exception:
                # swallow callback errors to keep loop running
                pass

            if stop_event is not None and stop_event.is_set():
                break

            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        # allow graceful cancellation
        raise


def format_hms(seconds: Optional[float]) -> str:
    """Return HH:MM:SS string for given seconds or '00:00:00' if None."""
    if seconds is None:
        return '00:00:00'
    s = int(seconds)
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"
