import asyncio
import sys

try:
    from asyncio import ensure_future
except ImportError:
    ensure_future = getattr(asyncio, 'async')

PY_350 = sys.version_info >= (3, 5, 0)
PY_352 = sys.version_info >= (3, 5, 2)
