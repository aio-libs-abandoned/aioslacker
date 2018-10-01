aioslacker
==========

:info: slacker wrapper for asyncio

.. image:: https://travis-ci.org/aio-libs/aioslacker.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aioslacker

.. image:: https://img.shields.io/pypi/v/aioslacker.svg
    :target: https://pypi.python.org/pypi/aioslacker

Installation
------------

.. code-block:: shell

    pip install aioslacker

Usage
-----

.. code-block:: python

    import asyncio

    from aioslacker import Slacker

    TOKEN = 'xxxxx'

    async def go():
        async with Slacker(TOKEN) as slack:
            await slack.chat.post_message('#general', 'Hello fellow slackers!')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(go())
    loop.close()

Thanks
------

The library was donated by `Ocean S.A. <https://ocean.io/>`_

Thanks to the company for contribution.
