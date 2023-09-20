from pathlib import Path
from random import randint


class Emoji(str):
    """A type to represent an Emoji character"""

    ...


# Emojis copied from https://c.r74n.com/emoji
EMOJI_PATH = Path.cwd() / Path("src") / "emoji.txt"
with open(EMOJI_PATH, "r") as file:
    ALL_EMOJIS = file.read()


def get_random_emoji() -> Emoji:
    index = randint(0, len(ALL_EMOJIS) - 2)
    return Emoji(ALL_EMOJIS[index])
