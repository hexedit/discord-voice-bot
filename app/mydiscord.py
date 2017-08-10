import discord


class MyDiscord(discord.Client):
    def __init__(self):
        super().__init__()
        self._token = ""

    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, val):
        self._token = val

    def run(self):
        super().run(self._token)
