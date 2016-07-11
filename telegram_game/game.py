import random

from telegram_game.api import Chat
from telegram_game.fields import Field


class BaseGame:
    """The base Game class

    Each player works with his own Game() instance.

    Use :py:mod:`telegram_game.fields` to add a persistent attributes to Game, see
    py:mod:`telegram_game.examples`.
    """

    def __init__(self, chat_id, queue, api):
        self.chat_id = chat_id
        self.queue = queue
        self.api = api
        self.chat = Chat(api, chat_id)

    def __getattribute__(self, key):
        value = super().__getattribute__(key)
        if isinstance(value, Field):
            return value.get(self, key)
        return value

    def __setattr__(self, key, value):
        if hasattr(self, key):
            attr = super().__getattribute__(key)
            if isinstance(attr, Field):
                attr.set(self, key, value)
                return
        super().__setattr__(key, value)

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
