import os
import sys


class CommandProcessor(object):
    _modules_ = []

    def __init__(self):
        self._name_ = 'undefined'

    def on_load(self):
        pass

    def on_command(self, cmd, arg, client=None, **kwargs):
        print(client)
        pass

    @staticmethod
    def load_modules():
        mod_list = os.listdir('commands')
        sys.path.insert(0, 'commands')

        for mod in mod_list:
            if not mod.endswith(".py"):
                continue
            print("Found command module: {}".format(mod))
            __import__(os.path.splitext(mod)[0])

        for mod in CommandProcessor.__subclasses__():
            m = mod()
            CommandProcessor._modules_.append(m)
            m.on_load()

    @staticmethod
    def process_command(cmd, arg, **kwargs):
        for m in CommandProcessor._modules_:
            if m.on_command(cmd, arg, **kwargs):
                break
