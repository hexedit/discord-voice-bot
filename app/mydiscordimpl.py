from . import MyDiscord
from configparser import ConfigParser, NoSectionError, NoOptionError
from discord import opus, ChannelType
from yandex_speech import TTS
from random import randint

tts_voices = [
    'jane',
    'oksana',
    'alyss',
    'omazh',
    'zahar',
    'ermil'
]

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


def free_player():
    global player
    player = None


def play_file(to_play):
    global player
    if to_play is not None and player is None and voice.is_connected():
        if not to_play.startswith('/'):
            to_play = 'media/voice/' + to_play
        player = voice.create_ffmpeg_player(to_play, after=free_player)
        player.volume = voice_volume
        player.start()


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
            try:
                play_file(config.get('voice', 'play on join'))
            except NoOptionError:
                pass
    except (NoSectionError, NoOptionError):
        pass


@client.async_event
def on_message(message):
    global player
    toplay = None
    if voice.is_connected() and player is None:
        if message.content.lower() in voice_messages:
            if message.server is None:
                message_author = message.author.name
                message_channel = "private"
            else:
                message_author = message.author.display_name
                message_channel = message.server.name + " / " + message.channel.name
            print("Playing message for \033[01m{}\033[00m at volume \033[01m{}\033[00m by \033[01m{}\033[00m at \033[01m{}\033[00m"
                  .format(message.content, voice_volume, message_author, message_channel))
            toplay = voice_messages[message.content.lower()]
        elif message.server is None:
            print("Retrieving TTS for \033[01m{}\033[00m by \033[01m{}\033[00m".format(message.content,message.author.name))
            try:
                tts_voice = tts_voices[randint(0, len(tts_voices) - 1)]
                key = config.get('tts', 'api key')
                tts = TTS(tts_voice, 'opus', key, lang='ru_RU', emotion='neutral')
                tts.generate(message.content)
                toplay = tts.save("/tmp/tts.opus")
            except (NoSectionError, NoOptionError):
                pass
        play_file(toplay)
