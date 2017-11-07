from . import CommandProcessor
import asyncio


class CommandStop(CommandProcessor):
    def __init__(self):
        super().__init__()
        self._name_ = "stop"

    @asyncio.coroutine
    def on_command(self, cmd, arg, commands=None, player=None, message=None, **kwargs):
        if ('stop' in commands and cmd in commands['stop']) or cmd == 'stop':
            if player:
                print("Stopping playback on request from \033[01m{}\033[00m".format(message.author.name))
                player.stop()
        return False
