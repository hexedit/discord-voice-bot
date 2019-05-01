#!bin/python
""" Bot startup """

import signal

from app import app


def _finish(sig, frame):
    del sig, frame
    print("Terminate signal received. Stopping...")
    app.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, _finish)
    signal.signal(signal.SIGINT, _finish)
    while True:
        try:
            app.run()
            print("Graceful shutdown, exiting")
        except:  # pylint: disable=bare-except
            print("Unhandled exception, exiting")
            break
