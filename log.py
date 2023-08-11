import logging
from typing import Union


def init_logger(level: Union[int, str] = logging.DEBUG) -> logging.Logger:
    """
    创建日志工具
    :param level: 日志等级
    :return: 日志工具
    """
    root = logging.getLogger(__name__)
    define_format = logging.Formatter(fmt='%(asctime)s %(levelname)-10s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(define_format)

    root.addHandler(console_handler)
    root.setLevel(level)

    return root


def update_level(level: Union[int, str] = logging.DEBUG) -> None:
    """
    更新日志等级
    :param level:
    :return:
    """
    global logger
    logger.setLevel(level)


logger = init_logger(logging.INFO)
