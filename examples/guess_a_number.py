import logging
import random
import asyncio

from telegram_game import Messages
from telegram_game.redis_game import RedisGame, RedisField


logger = logging.getLogger(__name__)


class M(Messages):
    PREAMBLE = "I'm thinking of a number from 1 to 10! Try to guess it!"
    LESS = [
        "You didn't guess right!",
        "You failed!",
        "Too high!",
    ]
    GREATER = [
        "Wrong!",
        "No.",
        "Too low!",
    ]
    BAD_INPUT = "Are you cheating?!",
    SUCCESS = "You guessed! You guessed the number {0} times for {1} tries!"
    AGAIN = "Let's try again?"


KEYBOARD = {
    'keyboard': [['1', '2', '3', '4', '5'],
                 ['6', '7', '8', '9', '10']]
}


class Game(RedisGame):

    guessed = RedisField(0)
    tries = RedisField(0)

    async def start(self):

        await self.chat.sendChatAction('typing')

        await asyncio.sleep(4)

        num = random.randint(1, 10)

        await self.send(M.PREAMBLE, reply_markup=KEYBOARD)

        while True:

            msg = await self.recv()

            try:
                guess = int(msg['message']['text'])
            except (KeyError, ValueError):
                await self.send(M.BAD_INPUT)
                continue

            self.tries += 1

            if guess == num:
                self.guessed = self.guessed + 1
                await self.send(M.SUCCESS.format(self.guessed, self.tries))
                break
            elif guess < num:
                await self.send(random.choice(M.GREATER), reply_markup=KEYBOARD)
            else:
                await self.send(random.choice(M.LESS), reply_markup=KEYBOARD)

        await self.chat.sendChatAction('typing')

        await asyncio.sleep(2)

        await self.send(M.AGAIN)
