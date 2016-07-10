import logging
import random

from tg import fields, BaseGame, Messages


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
    BAD_INPUT = [
        "Are you cheating?!",
    ]
    SUCCESS = "You guessed! You guessed the number {0} times for {1} tries!"


class Game(BaseGame):

    guessed = fields.Integer(0)
    tries = fields.Integer(0)

    async def start(self):

        while True:

            num = random.randint(1, 10)

            await self.send(M.PREAMBLE)

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
                    await self.send(M.SUCCESS, self.guessed, self.tries)
                    break
                elif guess < num:
                    await self.send(M.GREATER)
                else:
                    await self.send(M.LESS)
