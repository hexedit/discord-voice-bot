from . import MyDiscord
from configparser import ConfigParser


client = MyDiscord()
config = ConfigParser()

config.read('config.ini')
client.token = config.get('discord', 'token')
