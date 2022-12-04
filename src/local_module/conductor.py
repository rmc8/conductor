import os
import re
import asyncio
import pathlib
import platform
from datetime import datetime
from collections import defaultdict, deque

import discord
from discord.ext import commands

from . import config, rt, voice
from .util import YamlConfig


queue_dict = defaultdict(deque)

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix=".")
client = discord.Client(intents=discord.Intents.all())
log_path = f"./log/{rt:%Y%m%d_%H%M%S}_{{log_type}}.txt"


def write_log(*args, log_type: str):
    with open(log_path.format(log_type=log_type), mode="a", encoding="utf-8") as f:
        print(*args, file=f)


def play(vc, queue):
    if not queue or vc.is_playing():
        return
    source = queue.popleft()
    vc.play(source, after=lambda e: play(vc, queue))


def enqueue(vc, guild, source):
    queue = queue_dict[guild.id]
    queue.append(source)
    if not vc.is_playing():
        play(vc, queue)


def get_user_dict_path_from_ctx(ctx) -> str:
    gid = ctx.guild.id
    return f"./dict/{gid}_dict.yml"


@bot.command()
async def aw(ctx, arg1, arg2):
    user_dict_path = get_user_dict_path_from_ctx(ctx)
    yc = YamlConfig(file_path=user_dict_path)
    user_dict = yc.load()
    print(user_dict)
    user_dict[arg1] = arg2
    print(user_dict)
    yc.write(user_dict)
    await ctx.send(f";`{arg1}`を`{arg2}`として登録しました")


@bot.command()
async def dw(ctx, arg1):
    user_dict_path = get_user_dict_path_from_ctx(ctx)
    yc = YamlConfig(file_path=user_dict_path)
    user_dict = yc.load()
    msg: str = f";`{arg1}`が辞書内に見つかりませんでした"
    if arg1 in user_dict.keys():
        del user_dict[arg1]
        msg = f";`{arg1}`を辞書から削除しました"
    yc.write(user_dict)
    await ctx.send(msg)


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


def user_dict_init(guild_id):
    user_dict_path = f"./dict/{guild_id}_dict.yml"
    if not os.path.exists(user_dict_path):
        with open(user_dict_path, mode="w", encoding="utf-8") as f:
            print(f"_{guild_id}_user_dict_init_: _\n", file=f, end="")


@bot.event
async def on_message(message):
    print("---on_message_start---")
    user_dict_init(message.guild.id)
    write_log(message.content, log_type="message")
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
    elif re.match(r"(\d{5,6})$", message.content.strip()) and not message.author.bot:
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
            message.guild.id,
        )
        if exists:
            p = pathlib.Path(mp3_path)
            source = discord.FFmpegPCMAudio(str(p.resolve()))
            # message.guild.voice_client.play(source)
            enqueue(
                vc=message.guild.voice_client,
                guild=message.guild,
                source=source,
            )
    await bot.process_commands(message)
    print("---on_message_end---")


@bot.event
async def on_message_edit(before, after):
    print("---on_message_edit_start---")
    write_log(before, after, log_type="edit")
    print("---on_message_edit_end---")


@bot.event
async def on_message_delete(message):
    print("---on_message_delete_start---")
    write_log(f"{message}", log_type="delete")
    print("---on_message_delete_end---")


@bot.event
async def on_voice_state_update(member, before, after):
    print("---on_voice_state_update_start---")
    msg: str = ""

    if before.channel is None and after.channel:
        msg += f"`{member.display_name}`が`{after.channel.name}`に参加しました。"
    elif after.channel is None and after.channel:
        msg += f"`{member.display_name}`が`{before.channel.name}`から退出しました。"
    # elif before.channel is not None and after.channel is not None:
    #    msg += f"`{member.name}`が`{before.channel.name}`から`{after.channel.name}`に移動しました。"
    if msg:
        text_ch = member.guild.get_channel(config["log"]["voice_state_update"])
        # await asyncio.sleep(1)
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
