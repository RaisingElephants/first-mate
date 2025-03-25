"""
first-mate

Find yourself some friends on campus at UNSW.
"""
import logging
from .server import app

def main():
    logging.basicConfig(level="DEBUG")
    app.run()


if __name__ == "__main__":
    main()
