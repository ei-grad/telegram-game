import random
import logging

import asyncio

from telegram_game.api import Chat


logger = logging.getLogger(__name__)


class BaseGame:
    """The base Game class

    Each player works with his own Game() instance.
    """

    def __init__(self, chat_id, queue, api):
        self.chat_id = chat_id
        self.queue = queue
        self.api = api
        self.chat = Chat(api, chat_id)
        self.restart_timeout = 5

    async def __call__(self):
        while True:
            try:
                await self.start()
            except:
                logger.error("%s.start() raised exception, restarting in %ss",
                             self, self.restart_timeout, exc_info=True)
                await asyncio.sleep(self.restart_timeout)

    def __str__(self):
        return 'Game(chat_id={})'.format(self.chat_id)

    @classmethod
    async def prepare(self, loop):
        """Prepare the game

        Use this method to prepare common game resources, establish the database
        connection, and so on.
        """
        pass

    async def send(self, msg, *args, **kwargs):
        if isinstance(msg, list):
            msg = random.choice(msg)
        return await self.chat.sendMessage(msg.format(*args, **kwargs))

    async def recv(self):
        """Get the next message from player."""
        return await self.queue.get()

    async def start(self):
        """Game logic implementation starts here.

        Use `await self.recv()` to get input from player, and `await
        self.chat.sendMessage()` to send a reply.
        """
        raise NotImplementedError()
