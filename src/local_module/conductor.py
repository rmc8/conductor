import asyncio
import platform
# from glob import glob
# from datetime import datetime
# from typing import Optional, Union

import discord
# import pandas as pd
# from pandas import DataFrame
# from discord.ext import commands

from . import config, write_config, voice

import discord

print(config)
print(write_config)
print(voice)


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")


def run():
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    intents = discord.Intents.default()
    intents.typing = False
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run("my token goes here")
