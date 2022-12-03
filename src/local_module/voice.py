import os
import re
from datetime import datetime

import pyttsx3

from . import config
from .util import YamlConfig


settings: dict = config["voice"]["settings"]


def rm_custom_emoji(text):
    """
    絵文字IDは読み上げないようにする
    :param text: オリジナルのテキスト
    :return: 絵文字IDを除去したテキスト
    """
    pattern = r"<:[a-zA-Z0-9_]+?:>"
    return re.sub(pattern, '', text)


def omit_code_block(text):
    """
    コードブロックを省略する
    :param text: オリジナルのテキスト
    :return: URLの省略したテキスト
    """
    pattern = r"`{3}.+?`{3}"
    return re.sub(pattern, "コードブロック省略", text, flags=re.DOTALL)


def omit_url(text):
    """
    URLを省略する
    :param text: オリジナルのテキスト
    :return: URLの省略したテキスト
    """
    pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    return re.sub(pattern, "URL省略", text)  # 置換処理


def rm_picture(text):
    """
    画像の読み上げを止める
    :param text: オリジナルのテキスト
    :return: 画像の読み上げを省略したテキスト
    """
    pattern = r".*(\.jpg|\.jpeg|\.gif|\.png|\.bmp)"
    return re.sub(pattern, "", text)  # 置換処理


def rm_command(text):
    """
    コマンドの読み上げを止める
    :param text: オリジナルのテキスト
    :return: コマンドを省略したテキスト
    """
    return re.sub(r"^(!|\?|$|\.|>).*", "", text, flags=re.DOTALL)  # 置換処理


def rm_symbol(text):
    """
    読み上げない記号を除去する
    :param text: オリジナルのテキスト
    :return: 記号を省略したテキスト
    """
    return text.replace("`", "")


def rm_mention(text):
    pattern = r"<@\d+?>"
    return re.sub(pattern, "", text, flags=re.DOTALL)


def user_custom(text, gid):
    """
    辞書のデータを読み上げる
    :param text:
    :return:
    """
    user_dict_path: str = f"./dict/{gid}_dict.yml"
    if not os.path.exists(user_dict_path):
        return text
    yc = YamlConfig(user_dict_path)
    user_dict: dict = yc.load()
    for k, v in user_dict.items():
        text = text.replace(k, v)
    print(f"置換後のtext: {text}")
    return text


def gen_mp3(text, path):
    engine = pyttsx3.init()
    # rate = engine.getProperty("rate")
    engine.setProperty("rate", settings["rate"])
    engine.save_to_file(text, path)
    engine.runAndWait()
    print(f"save: {path}")


def create_mp3(name, input_text, output_path, gid) -> bool:
    """
    message.contentをテキストファイルと音声ファイルに書き込む
    :param input_text: 読み上げ内容のテキスト
    :param output_path: mp3ファイルの出力先
    :return: 音声の出力があるか
    """
    # message.contentをテキストファイルに書き込み
    fxs = (rm_command, omit_code_block, omit_url, rm_symbol,
           rm_picture, rm_mention, rm_custom_emoji)
    for fx in fxs:
        input_text = fx(input_text)
    input_text = user_custom(input_text, gid)
    if input_text:
        msg: str = f"{name}, {input_text}"
        gen_mp3(msg, output_path)
        print(msg)
        return True
    return False


if __name__ == '__main__':
    from util import mkdir
    mkdir("./dict/")
    mkdir("./output/")
    now = datetime.now()
    create_mp3("K", "テスト", f"../output/output_{now:%Y%m%d_%H%M%S}.mp3")
