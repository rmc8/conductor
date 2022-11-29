import re
import asyncio
import pathlib
import platform
from datetime import datetime
# from glob import glob
# from datetime import datetime
# from typing import Optional, Union

import discord
from discord.ext import commands
# import pandas as pd
# from pandas import DataFrame

from . import config, voice  # , write_config


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix=".")
client = discord.Client(intents=discord.Intents.all())


@bot.command()
async def aw(ctx, arg1, arg2):
    with open('./dict/dict.csv', mode='a', encoding='utf-8') as f:
        f.write(f'{arg1},{arg2}\n')
        print(f'dic.txtに書き込み：\n{arg1}, {arg2}')
    await ctx.send(f'`{arg1}`を`{arg2}`として登録しました')


@bot.command()
async def dw(ctx, arg1):
    pass


@bot.event
async def on_ready():
    print(f"Logged on as {client.user}!")


@bot.event
async def on_message(message):
    print("---on_message_start---")
    mute_id: list = config["voice"]["mute"]
    do_mute: bool = message.author.id in mute_id
    msg_client = message.guild.voice_client
    now = datetime.now()
    mp3_path: str = f"./output/output_{now:%Y%m%d_%H%M%S}.mp3"
    if message.content.strip() and message.content.startswith(";"):
        return  # SKIP
    elif message.content.strip().lower() == ".join" and message.guild.voice_client is None:
        await message.author.voice.channel.connect()
    elif message.content.strip().lower() == ".bye" and message.guild.voice_client is not None:
        await message.guild.voice_client.disconnect()
    elif re.match(r"(\d{5,6})", message.content.strip()) and not message.author.bot:
        room_num: str = message.content.strip()
        category_id = message.channel.category_id
        live_conf: dict = config["prsk"]["live"]
        print(message.author.name, )
        nvcid = live_conf["normal"]["vc_id"]
        cvcid = live_conf["cheerful"]["vc_id"]
        if category_id == live_conf["normal"]["category_id"]:
            tch = bot.get_channel(live_conf["normal"]["room_ch_id"])
            await tch.send(room_num)
            vch = bot.get_channel(nvcid)
            room_fmt = live_conf["cheerful"]["vc_fmt"]
            await vch.edit(name=room_fmt.format(room_num=room_num))
        elif category_id == live_conf["cheerful"]["category_id"]:
            tch = bot.get_channel(live_conf["cheerful"]["room_ch_id"])
            await tch.send(room_num)
            vch = bot.get_channel(cvcid)
            room_fmt = live_conf["cheerful"]["vc_fmt"]
            await vch.edit(name=room_fmt.format(room_num=room_num))
    elif not message.content.startswith(".") and msg_client and not do_mute:
        print("#message.content:" + message.content)
        dn : str = message.author.display_name
        display_name : str = "" if dn in ("Conductor", "ConductorDev") else dn
        exists: bool = voice.create_mp3(
            display_name,
            message.content,
            mp3_path,
        )
        if exists:
            p = pathlib.Path(mp3_path)
            print(p.resolve())
            source = discord.FFmpegPCMAudio(str(p.resolve()))
            message.guild.voice_client.play(source)
    await bot.process_commands(message)
    print("---on_message_end---")


@bot.event
async def on_message_edit(before, after):
    print("---on_message_edit_start---")
    print(f"BEFORE: {before}")
    print(f"AFTER:  {after}")
    print("---on_message_edit_end---")


@bot.event
async def on_message_delete(message):
    print("---on_message_delete_start---")
    print(f"DELETE: {message}")
    print("---on_message_delete_end---")


@bot.event
async def on_voice_state_update(member, before, after):
    print("---on_voice_state_update_start---")
    msg: str = ""

    if before.channel is None and after.channel:
        msg += f"`{member.name}`が`{after.channel.name}`に参加しました。"
    elif after.channel is None and after.channel:
        msg += f"`{member.name}`が`{before.channel.name}`から退出しました。"
    # elif before.channel is not None and after.channel is not None:
    #    msg += f"`{member.name}`が`{before.channel.name}`から`{after.channel.name}`に移動しました。"
    if msg:
        text_ch = member.guild.get_channel(config["log"]["voice_state_update"])
        await asyncio.sleep(1)
        await text_ch.send(msg)
    print("---on_voice_state_update_end---")


@bot.command()
async def join(ctx):
    print("---join_start---")
    vc = ctx.author.voice.channel
    await vc.connect()
    print("---join_end---")


@bot.command()
async def bye(ctx):
    print("---bye_start---")
    await ctx.voice_client.disconnect()
    print("---bye_end---")


async def run():
    async with bot:
        await bot.start(config["token"])
