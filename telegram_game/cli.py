#!/usr/bin/env python

from importlib import import_module
import asyncio
import os
import logging

import click

from telegram_game.dispatcher import GameDispatcher


@click.command()
@click.argument('game')
@click.option('--token', default=os.environ.get('TELEGRAM_TOKEN'),
              help='Telegram Bot API token (get it from http://telegram.me/BotFather)')
@click.option('--debug', is_flag=True)
def main(game, token, debug):
    """Start a game bot server

    Pass a game module name to it, for example:

    > telegram-game telegram_game.examples.quiz
    """
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(name)-16s %(levelname)-8s %(message)s"
    )
    game = import_module(game)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(GameDispatcher(game.Game, api_token=token).run())


if __name__ == "__main__":
    main()
