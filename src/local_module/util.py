import os

import yaml


def mkdir(dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)


class YamlConfig:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def load(self) -> dict:
        """
        yamlファイルを読み辞書形式で結果を返す
        :return: yamlファイルのデータ構造（辞書）
        """
        with open(self.file_path, mode="r", encoding="utf-8") as yf:
            return yaml.safe_load(yf)

    def write(self, data: dict) -> None:
        """
        yamlを書き出す
        :param data: yamlで出力するデータをまとめた辞書
        """
        with open(self.file_path, "w") as yf:
            yaml.safe_dump(data, yf, default_flow_style=False)
