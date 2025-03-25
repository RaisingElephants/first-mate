"""
first-mate

Find yourself some friends on campus at UNSW.
"""

import dotenv
dotenv.load_dotenv()

from .server import app  # noqa: E402


def main():
    # logging.basicConfig(level="DEBUG")
    app.run()


if __name__ == "__main__":
    main()
