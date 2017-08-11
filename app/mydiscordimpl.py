from . import MyDiscord
from configparser import ConfigParser, NoSectionError, NoOptionError
from discord import opus, ChannelType


if not opus.is_loaded():
    opus.load_opus('voice')

config = ConfigParser()
config.read('config.ini')

client = MyDiscord()
try:
    client.token = config.get('discord', 'token')
except (NoSectionError, NoOptionError):
    print("No config option - discord/token");

voice = None
try:
    voice_volume = float(config.get('voice', 'volume')) / 100.0
except:
    voice_volume = 1.0

voice_messages = dict()
try:
    for msg, entry in config.items('voice-messages'):
        voice_messages[msg] = entry
except NoSectionError:
    pass

@client.async_event
def on_ready():
    print("Logged in as \033[01m{user.name}\033[00m".format(user=client.user))
    print("Authorized on servers:")
    for server in client.servers:
        print("\t- \033[01m{server.name}\033[00m".format(server=server))
    try:
        global voice
        voice_channel = client.get_channel(config.get('voice', 'channel'))
        if voice_channel is not None and voice_channel.type is ChannelType.voice:
            voice = yield from client.join_voice_channel(voice_channel)
        if voice is not None:
            print("Connected to voice channel \033[01m{channel.name}\033[00m on \033[01m{channel.server.name}\033[00m".format(channel=voice_channel))
    except:
        pass

@client.async_event
def on_message(message):
    if message.content in voice_messages and voice.is_connected():
        print("Playing message for \033[01m{}\033[00m at volume \033[01m{}\033[00m".format(message.content, voice_volume));
        player = voice.create_ffmpeg_player('media/voice/' + voice_messages[message.content])
        player.volume = voice_volume
        player.start()
