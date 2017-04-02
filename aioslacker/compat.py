import asyncio
import sys
from functools import partial

import aiohttp

PY_344 = sys.version_info >= (3, 4, 4)
PY_350 = sys.version_info >= (3, 5, 0)
PY_352 = sys.version_info >= (3, 5, 2)

AIOHTTP_VERSION = tuple(map(int, aiohttp.__version__.split('.')))


def create_task(*, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    if PY_352:
        return loop.create_task

    if PY_344:
        return partial(asyncio.ensure_future, loop=loop)

    return partial(getattr(asyncio, 'async'), loop=loop)
