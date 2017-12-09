import discord
import asyncio


class MyDiscord(discord.Client):
    def __init__(self):
        super().__init__()
        self._token = ""
        self._stop = False

    @asyncio.coroutine
    def _wait_for_stop(self):
        while True:
            if self._stop:
                yield from self.logout()
                print("Logged out")
                break
            yield from asyncio.sleep(1)

    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, val):
        self._token = val

    def run(self):
        self.loop.create_task(self._wait_for_stop())
        super().run(self._token)

    def stop(self):
        self._stop = True
