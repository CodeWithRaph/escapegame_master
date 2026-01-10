import time
import asyncio
import threading
from typing import Callable, Optional
import yaml

# ...existing code...
_stopwatch = {"start_time": None, "wall_time": None}
_lock = threading.Lock()
_malus_seconds = 0

def export():
    """Sauvegarde minimale et robuste de l'état."""
    data = {
        "running": _stopwatch["start_time"] is not None,
        "wall_time": _stopwatch["wall_time"],
    }
    try:
        with open("stopwatch.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    except Exception:
        # ne pas faire planter l'app si l'export échoue
        pass


def import_stopwatch():
    """Lit le fichier de persistence ; retourne {} si absent / invalide."""
    try:
        with open("stopwatch.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except Exception:
        return {}


def start():
    """Démarre un nouveau chrono (écrase l'ancien)."""
    t = time.monotonic()
    w = time.time()
    with _lock:
        _stopwatch["start_time"] = t
        _stopwatch["wall_time"] = w
    export()


def reset():
    """Remet à zéro en mémoire et sur disque."""
    with _lock:
        _stopwatch["start_time"] = None
        _stopwatch["wall_time"] = None
    export()


def restart():
    """Restaurer l'état persistant si le YAML indique running=True.
    Ne redémarre rien si un chrono est déjà en mémoire.
    """
    saved = import_stopwatch()
    if not saved:
        return
    if saved.get("running") and saved.get("wall_time") is not None:
        with _lock:
            if _stopwatch["start_time"] is None:
                w = saved["wall_time"]
                _stopwatch["wall_time"] = w
                # reconstruire start_time à partir de l'horloge monotone locale
                _stopwatch["start_time"] = time.monotonic() - (time.time() - w)


def stop():
    """Arrête le chrono et retourne les secondes écoulées (float) ou None."""
    with _lock:
        t0 = _stopwatch["start_time"]
        if t0 is None:
            return None
        elapsed_sec = time.monotonic() - t0
        _stopwatch["start_time"] = None
        _stopwatch["wall_time"] = None
    export()
    return elapsed_sec


def start_time():
    """Retourne le temps au lancement du chrono."""
    with _lock:
        return _stopwatch["start_time"]


# Async wrappers non bloquants
async def async_start():
    await asyncio.to_thread(start)


async def async_stop():
    return await asyncio.to_thread(stop)


async def async_elapsed():
    return await asyncio.to_thread(elapsed)


def get_start_wall_time():
    """Retourne le timestamp epoch (wall clock) du démarrage, ou None."""
    with _lock:
        return _stopwatch["wall_time"]

def add_malus_minutes(minutes):
    """Increment malus for key by given minutes."""
    seconds = float(minutes) * 60.0
    with _lock:
        _malus_seconds = _malus_seconds + seconds


def get_malus_minutes():
    """Return the malus in whole minutes (rounded down)."""
    with _lock:
        s = _malus_seconds
    return int(s // 60)


def format_hms(seconds: Optional[float]) -> str:
    """Return HH:MM:SS string for given seconds or '00:00:00' if None."""
    if seconds is None:
        return '00:00:00'
    s = int(seconds)
    hrs = s // 3600
    mins = (s % 3600) // 60
    secs = s % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


restart()