from . import MyDiscord
from configparser import ConfigParser, NoSectionError, NoOptionError
from discord import opus, ChannelType


if not opus.is_loaded():
    opus.load_opus('voice')

config = ConfigParser()
config.read('config.ini')

token = None
try:
    token = config.get('discord', 'token')
except (NoSectionError, NoOptionError):
    print("No config option - discord/token");
    exit(1)

client = MyDiscord()
client.token = token
voice = None

voice_messages = dict()
try:
    for msg, entry in config.items('voice-messages'):
        voice_messages[msg] = entry
except NoSectionError:
    pass

@client.async_event
def on_ready():
    print("Logged in as {user.name}".format(user=client.user))
    print("Authorized on servers:")
    for server in client.servers:
        print("\t- {server.name}".format(server=server))
    try:
        global voice
        voice_channel = client.get_channel(config.get('discord', 'channel'))
        if voice_channel is not None and voice_channel.type is ChannelType.voice:
            voice = yield from client.join_voice_channel(voice_channel)
        if voice is not None:
            print("Connected to voice channel {channel.name} on {channel.server.name}".format(channel=voice_channel))
    except NoOptionError:
        pass

@client.async_event
def on_message(message):
    if message.content in voice_messages and voice.is_connected():
        print("Playing message for " + message.content)
        player = voice.create_ffmpeg_player('media/voice/' + voice_messages[message.content])
        player.start()
