"""
In some games the game state is not critical, it is ok to drop all and ask the
player to start from scratch. In that case just use
:py:class:`telegram_game.game.BaseGame`, and store state in the `start` coroutine
local variables or `self` attributes.

But in some games it is crucial to save the state
between different bot runs. In that case you can use :py:class:`RedisGame`.
"""

import os

import redis
import msgpack

from telegram_game.game import BaseGame


class RedisGame(BaseGame):
    """Game with persistent fields stored in Redis.

    You can define persistent fields with telegram_game.redis_game.RedisField,
    and use them as the usual variables in your game logic code:

    .. code-block:: python

        class Game(RedisGame):
            score = RedisField(initial=0)
            level = RedisField(initial=1)

            async def start(self):
                self.score += 1
                await self.reply(self.level)

    Field values are serialised with `msgpack`_. Think of it like about a
    trivial ORM.

    .. note::

        It is recommened to run the redis server on the same host, where the game
        bot is running (to reduce latency). In this case it should be ok to use a
        blocking redis client for the sake of simplicity.

    .. _msgpack: http://msgpack.org/
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'REDIS_URL' in os.environ:
            self.redis = redis.from_url(os.environ['REDIS_URL'])
        else:
            self.redis = redis.Redis()

    def __getattribute__(self, key):
        value = super().__getattribute__(key)
        if isinstance(value, RedisField):
            ret = self.redis.get('tg:%s:%s' % (self.chat_id, key))
            if ret is None:
                return value.initial
            return msgpack.loads(ret)
        return value

    def __setattr__(self, key, value):
        sup = super()
        if hasattr(self, key) and isinstance(sup.__getattribute__(key), RedisField):
            self.redis.set('tg:%s:%s' % (self.chat_id, key), msgpack.dumps(value))
        else:
            sup.__setattr__(key, value)


class RedisField:
    """Define a `RedisGame` field as a persistent field."""
    def __init__(self, initial):
        self.initial = initial
