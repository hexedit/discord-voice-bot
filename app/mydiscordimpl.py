from . import MyDiscord
from configparser import ConfigParser, NoSectionError, NoOptionError
from discord import opus, ChannelType
from yandex_speech import TTS


if not opus.is_loaded():
    opus.load_opus('voice')

config = ConfigParser()
config.read('config.ini')

client = MyDiscord()
try:
    client.token = config.get('discord', 'token')
except (NoSectionError, NoOptionError):
    print("No config option - discord/token")

voice = None
try:
    voice_volume = float(config.get('voice', 'volume')) / 100.0
except (NoSectionError, NoOptionError):
    voice_volume = 1.0
player = None

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
            print("Connected to voice channel \033[01m{channel.name}\033[00m on \033[01m{channel.server.name}\033[00m"
                  .format(channel=voice_channel))
    except (NoSectionError, NoOptionError):
        pass


def free_player():
    global player
    player = None


@client.async_event
def on_message(message):
    global player
    toplay = None
    if voice.is_connected() and player is None:
        if message.content.lower() in voice_messages:
            print("Playing message for \033[01m{}\033[00m at volume \033[01m{}\033[00m"
                  .format(message.content, voice_volume))
            toplay = 'media/voice/' + voice_messages[message.content.lower()]
        elif message.server is None:
            print("Retrieving TTS for \033[01m{}\033[00m".format(message.content))
            try:
                key = config.get('tts', 'api key')
                tts = TTS('jane', 'opus', key, lang='ru_RU', emotion='neutral')
                tts.generate(message.content)
                toplay = tts.save("/tmp/tts.opus")
            except (NoSectionError, NoOptionError):
                pass
        if toplay is not None:
            player = voice.create_ffmpeg_player(toplay, after=free_player)
            player.volume = voice_volume
            player.start()
