import asyncio

import discord

from .cmdprocessor import CommandProcessor


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
                msglist = list(voice_messages.keys())
                msgcount = len(msglist)
                mx = 0
                for _px in range(0, int((len(msglist) + 49) / 50)):
                    answer = ""
                    for _sx in range(0, 50 if msgcount > 50 else msgcount):
                        answer += "{n}\t{m}\n".format(n=mx, m=msglist[mx])
                        mx += 1
                    embed = discord.Embed(title="Voice messages",
                                          description=answer)
                    yield from client.send_message(message.channel,
                                                   embed=embed)
                    msgcount -= 50
            return True
        return False
