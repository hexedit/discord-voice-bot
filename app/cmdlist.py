import asyncio

import discord

from . import CommandProcessor


class CommandList(CommandProcessor):
    def __init__(self):
        super().__init__()
        self._name_ = "list"

    @asyncio.coroutine
    def on_command(self, cmd, arg,
                   commands=None,
                   voice_messages=None,
                   client=None,
                   message=None,
                   **kwargs):
        if ('list' in commands and cmd in commands['list']) or cmd == 'list':
            if voice_messages:
                answer = ""
                msglist = list(voice_messages.keys())
                for mx in range(0, len(msglist)):
                    answer += "{n}\t{m}\n".format(n=mx, m=msglist[mx])
                answer = discord.Embed(title="Voice messages",
                                       description=answer)
                yield from client.send_message(message.channel, embed=answer)
            return True
        return False
