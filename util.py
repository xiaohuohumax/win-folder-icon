import configparser
import os
import shutil
import subprocess
from pathlib import Path
from typing import List

from PIL import Image


def abs_path(rel_path: str) -> str:
    """
    获取绝对路径
    :param rel_path: 绝对/相对路径
    :return: 绝对路径
    """
    return rel_path if os.path.isabs(rel_path) else str(Path(Path(__file__).parent, rel_path))


def run_cmd(cmd: List[str], decode: str = "utf-8") -> (int, str):
    """
    调用命令行 适配中文忽略异常
    :param decode: 编码格式
    :param cmd: 命令
    :return: (状态码,返回信息)
    """
    with subprocess.Popen(' '.join(cmd), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          shell=True) as proc:
        info, _ = proc.communicate()
        return proc.returncode, info.decode(decode, errors='ignore')


def init_ini() -> configparser.ConfigParser:
    """
    初始ini配置
    :return: 配置
    """
    conf = configparser.ConfigParser()
    conf.optionxform = str
    return conf


def read_ini(ini_path: str) -> configparser.ConfigParser:
    """
    读取ini配置文件
    :param ini_path: ini配置文件路径
    :return: 配置信息
    """
    conf = init_ini()
    conf.read(ini_path)
    return conf


def write_ini(ini_conf: configparser.ConfigParser, ini_path: str) -> None:
    """
    保存ini配置信息
    :param ini_conf: 配置信息
    :param ini_path: 配置文件路径
    :return:
    """
    ini_conf.write(open(ini_path, 'w', encoding="utf-8"))


def read_file_lines(file_path) -> List[str]:
    """
    读取文件信息
    :param file_path: 文件路径
    :return: 文件内容
    """
    with open(file_path, encoding="utf-8") as file:
        return file.readlines()


def write_file_lines(file_path: str, lines: List[str]) -> None:
    """
    写文件
    :param file_path: 文件保存路径
    :param lines: 文件内容
    :return:
    """
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write('\n'.join(lines))


def file_exists(file_path: str) -> bool:
    """
    判断文件是否存在
    :param file_path: 文件
    :return: 是否存在
    """
    return Path(file_path).exists()


def img2ico(img_path: str, ico_save_path: str) -> None:
    """
    图片转ico
    :param img_path: 图片路径
    :param ico_save_path: ico保存路径
    :return:
    """
    with Image.open(img_path) as img:
        img.save(ico_save_path, format="ICO", sizes=[(256, 256)])


def path_join(*paths) -> str:
    """
    路径拼接
    :param paths: 路径
    :return: 拼接路径
    """
    return str(Path(*paths))


def file_name(file_path: str) -> str:
    """
    获取文件名称
    :param file_path: 文件路径
    :return: 文件名称
    """
    return Path(file_path).name


def file_suffix(file_path: str) -> str:
    """
    获取文件后缀名
    :param file_path: 文件路径
    :return: 文件后缀名
    """
    return Path(file_path).suffix.lower().replace(".", "")


def file_copy(file_path: str, target_path: str) -> None:
    """
    文件复制
    :param file_path: 文件路径 
    :param target_path: 目标路径
    :return:
    """
    shutil.copy(file_path, target_path)
