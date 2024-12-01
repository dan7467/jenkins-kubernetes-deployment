from logging import log

from asyncio import run
from contextlib import AsyncContextDecorator

class Context(AsyncContextDecorator):
    async def __aenter__(self):  # Starting async action
        return self

    async def __aexit__(self, *exc):  # Ending async action
        return False