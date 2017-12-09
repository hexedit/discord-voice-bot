#!bin/python

from app import app
import signal


def finish(sig, frame):
    del sig, frame
    print("Terminate signal received. Stopping...")
    app.stop()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, finish)
    signal.signal(signal.SIGINT, finish)
    while True:
        try:
            app.run()
        finally:
            print("Graceful shutdown, exiting")
            break
