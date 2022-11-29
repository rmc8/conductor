import datetime
from . import util

rt = datetime.datetime.now()
YC = util.YamlConfig(file_path="./config.yml")


def write_config(new_config: dict):
    YC.write(data=new_config)


config: dict = YC.load()
