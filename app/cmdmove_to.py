import asyncio

from discord import ChannelType, InvalidArgument

from .cmdprocessor import CommandProcessor
from .mydiscordimpl import switch_voice_channel


class CommandMoveTo(CommandProcessor):
    def __init__(self):
        super().__init__()
        self._name_ = "move to"

    @asyncio.coroutine
    def on_command(self, cmd, arg,
                   commands=None,
                   client=None,
                   voice=None,
                   message=None,
                   **kwargs):
        if ('move to' in commands and cmd in commands['move to']) \
                or cmd == 'move to':
            try:
                ch = client.get_channel(arg)
                if ch is None or ch.type is not ChannelType.voice:
                    raise InvalidArgument('Not a voice channel')
                print("\033[01m{}\033[00m requested me to move to "
                      "\033[01m{channel.name}\033[00m"
                      " on \033[01m{channel.server.name}\033[00m"
                      .format(message.author.name, channel=ch))
                yield from switch_voice_channel(ch)
                return True
            except InvalidArgument as e:
                yield from client.send_message(message.channel,
                                               '\n'.join(e.args))
        return False
