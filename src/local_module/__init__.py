from . import util

YC = util.YamlConfig(file_path="./config.yml")
config: dict = YC.load()


def write_config(new_config: dict):
    YC.write(data=new_config)
