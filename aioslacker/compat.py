import asyncio
import sys

import aiohttp

try:
    from asyncio import ensure_future
except ImportError:
    ensure_future = getattr(asyncio, 'async')

PY_350 = sys.version_info >= (3, 5, 0)
PY_352 = sys.version_info >= (3, 5, 2)

AIOHTTP_2 = aiohttp.__version__ >= '2.0.0'
