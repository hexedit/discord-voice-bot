#!bin/python

from app import app

if __name__ == '__main__':
    while True:
        try:
            app.run()
        finally:
            break
