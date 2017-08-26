from . import MyDiscord
from configparser import ConfigParser, NoSectionError, NoOptionError
from discord import opus, ChannelType, InvalidArgument
from yandex_speech import TTS
from random import randint
import asyncio
from tempfile import gettempdir
import codecs
import os.path
import re

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
config.read_file(codecs.open('config.ini', 'r', 'utf-8'))

client = MyDiscord()
try:
    client.token = config.get('discord', 'token')
except (NoSectionError, NoOptionError):
    print("No config option - discord/token")

voice = None
voice_volume = 1.0
try:
    voice_volume = float(config.get('voice', 'volume')) / 100.0
except (NoSectionError, NoOptionError):
    pass
player = None

voice_messages = dict()
try:
    for msg, entry in config.items('voice-messages'):
        voice_messages[msg] = entry
except NoSectionError:
    pass

greetings = dict()
try:
    for userid, entry in config.items('greetings'):
        greetings[userid] = entry
except NoSectionError:
    pass

greeting_delay = 0.5
try:
    greeting_delay = float(config.get('voice', 'greeting delay'))
except (NoSectionError, NoOptionError):
    pass


def free_player():
    global player
    player = None


def play_file(to_play):
    global player
    if to_play is not None and player is None and voice.is_connected():
        if not os.path.isabs(to_play):
            to_play = os.path.join('media', 'voice', to_play)
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


@asyncio.coroutine
def process_command11(cmd, arg, message):
    print("Got command \033[01m{}\033[00m from \033[01m{}\033[00m with argument \033[01m{}\033[00m"
          .format(cmd, message.author.name, arg))
    if cmd == 'move to' or cmd == 'go to' or cmd == 'пиздуй в':
        try:
            global voice
            ch = client.get_channel(arg)
            if ch is None or ch.type is not ChannelType.voice:
                raise InvalidArgument('Not a voice channel')
            print("\033[01m{}\033[00m requested me to move to \033[01m{channel.name}\033[00m"
                  " on \033[01m{channel.server.name}\033[00m"
                  .format(message.author.name, channel=ch))
            if voice:
                yield from voice.disconnect()
            voice = yield from client.join_voice_channel(ch)
        except InvalidArgument as e:
            yield from client.send_message(message.channel, '\n'.join(e.args))
            pass


@client.async_event
def on_message(message):
    global player
    cmd_ptrn = '^\s*([\w\s]+)\s*:\s*(.*)\s*$'
    if message.author == client.user:
        return
    m = re.findall(cmd_ptrn, message.content)
    if m and message.server is None:
        cmd = m[0][0].lower()
        arg = m[0][1]
        yield from process_command11(cmd, arg, message)
    elif voice.is_connected() and player is None:
        to_play = None
        if message.content.lower() in voice_messages:
            if message.server is None:
                message_author = message.author.name
                message_channel = "private"
            else:
                message_author = message.author.display_name
                message_channel = message.server.name + " / " + message.channel.name
            print("Playing message for \033[01m{}\033[00m at volume \033[01m{}\033[00m"
                  " by \033[01m{}\033[00m at \033[01m{}\033[00m"
                  .format(message.content, voice_volume, message_author, message_channel))
            to_play = voice_messages[message.content.lower()]
        elif message.server is None:
            print("Retrieving TTS for \033[01m{}\033[00m by \033[01m{}\033[00m"
                  .format(message.content, message.author.name))
            try:
                tts_voice = tts_voices[randint(0, len(tts_voices) - 1)]
                key = config.get('tts', 'api key')
                tts = TTS(tts_voice, 'opus', key, lang='ru_RU', emotion='neutral')
                tts.generate(message.content)
                to_play = tts.save(os.path.join(gettempdir(), "tts.opus"))
            except (NoSectionError, NoOptionError):
                pass
        play_file(to_play)


@client.async_event
def on_voice_state_update(before, after):
    if voice and voice.is_connected() and after.voice_channel != before.voice_channel:
        if after == client.user and after.voice_channel != before.voice_channel:
            print("I have been moved to \033[01m{channel.name}\033[00m on \033[01m{channel.server.name}\033[00m"
                  .format(channel=after.voice_channel))
            try:
                play_file(config.get('voice', 'play on join'))
            except NoOptionError:
                pass
        elif after.voice_channel == voice.channel:
            yield from asyncio.sleep(greeting_delay)
            if after.id in greetings.keys():
                play_file(greetings[after.id])
            elif 'default' in greetings.keys():
                play_file(greetings['default'])
