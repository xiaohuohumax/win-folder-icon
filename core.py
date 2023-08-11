import os
import sys

import numpy as np
import win32api
import win32con

from data import EditRule, RuleStatus, Conf, RecoverRule
from log import logger
from util import *


class WinFolderIconTool:
    """
    window 文件夹图标工具
    """
    # 配置
    _conf: Conf
    # 修改规则集合
    _edit_rule_list: List[EditRule] = []
    # 恢复规则集合
    _recover_rule_list: List[RecoverRule] = []
    # 规则忽略标识字符
    _rule_ignore_flag: str = "#"
    # 规则分割标识字符
    _rule_item_split_flag: str = ":"

    # desktop.ini
    # [.ShellClassInfo]
    # IconResource = xxx.ico,0

    _section_shell_class_info: str = ".ShellClassInfo"
    _option_icon_resource: str = "IconResource"

    def __init__(self, config: Conf):
        self._conf = config
        logger.debug(f"配置信息:{self._conf}")
        if not sys.platform.startswith("win"):
            raise Exception("更换图标只支持window环境")

    def _init_edit_rule_list(self) -> None:
        """
        解析修改图标规则文件
        :return:
        """
        logger.debug("开始解析规则文件")
        if not file_exists(self._conf.edit_rule_path):
            raise Exception(f"修改规则文件不存在:{self._conf.edit_rule_path}")

        map_lines = read_file_lines(self._conf.edit_rule_path)

        for index, line in enumerate([line.strip() for line in map_lines]):
            if line.startswith(self._rule_ignore_flag) or line == "":
                continue

            line_attrs = [map_attr.strip() for map_attr in line.split(self._rule_item_split_flag)]
            line_attrs = [map_attr for map_attr in line_attrs if map_attr != ""]

            if len(line_attrs) != 2:
                logger.debug(f"格式错误:{line}")
                self._edit_rule_list.append(EditRule(line, index + 1, RuleStatus.FAIL, error_info="规则格式错误"))
                continue

            folder_path = abs_path(line_attrs[0])
            icon_path = abs_path(line_attrs[1])

            self._edit_rule_list.append(EditRule(line, index + 1, folder_path=folder_path, icon_path=icon_path))

        logger.debug("解析规则文件完成")

    def _init_recover_rule_list(self) -> None:
        """
        解析恢复图标规则文件
        :return:
        """
        logger.debug("开始解析规则文件")
        if not file_exists(self._conf.recover_rule_path):
            raise Exception(f"恢复规则文件不存在:{self._conf.recover_rule_path}")

        map_lines = read_file_lines(self._conf.recover_rule_path)

        for index, line in enumerate([line.strip() for line in map_lines]):
            if line.startswith(self._rule_ignore_flag) or line == "":
                continue

            self._recover_rule_list.append(RecoverRule(line, index + 1, folder_path=line))

        logger.debug("解析规则文件完成")

    def _generate_result(self, is_edit_mode: bool) -> None:
        """
        生成结果报告
        :return:
        """
        # 表头/表身
        t_titles = ["[status]", "[folder abs path]", "[line number]", "[source]", "[error info]"]
        t_body: List[List[str]] = [
            [rule.status.value, rule.folder_path, str(rule.line_number), rule.source, rule.error_info]
            for rule in (self._edit_rule_list if is_edit_mode else self._recover_rule_list)
        ]

        # 计算表格每一列字符串宽带最大值
        col_max = np.amax(np.array([[len(item) for item in rule] for rule in [t_titles, *t_body]]), axis=0)

        logger.debug(f"表格列宽度:{col_max}")

        steep = " | "
        steep_size = sum(col_max) + len(steep) * (len(col_max) - 1)

        result_lines = [
            "修改图标结果统计" if is_edit_mode else "恢复默认图标结果统计",
            "=" * steep_size,
            steep.join([title.ljust(col_max[index], " ") for index, title in enumerate(t_titles)]),
            "-" * steep_size,
            *[steep.join([title.ljust(col_max[index], " ") for index, title in enumerate(item)]) for item in t_body],
            "=" * steep_size
        ]

        write_file_lines(self._conf.result_path, result_lines)
        logger.info(f"执行结果打印:{self._conf.result_path}")

    def _update_desktop_ini(self, folder_path: str, icon_path: str) -> None:
        """
        更新desktop.ini配置文件
        :param folder_path: 文件夹路径
        :param icon_path: 图标路径
        :return:
        """
        ini_path = path_join(folder_path, "desktop.ini")

        if file_exists(ini_path):
            # 设置为正常文件
            win32api.SetFileAttributes(ini_path, win32con.FILE_ATTRIBUTE_NORMAL)
            ini_tmp = read_ini(ini_path)
        else:
            ini_tmp = init_ini()

        if not ini_tmp.has_section(self._section_shell_class_info):
            ini_tmp.add_section(self._section_shell_class_info)

        ini_tmp.set(self._section_shell_class_info, self._option_icon_resource, f"{icon_path},0")

        write_ini(ini_tmp, ini_path)

        # 设置ini属性 隐藏+系统文件
        win32api.SetFileAttributes(ini_path, win32con.FILE_ATTRIBUTE_HIDDEN + win32con.FILE_ATTRIBUTE_SYSTEM)

    @staticmethod
    def _copy_icon_to_target(target_path: str, icon_path) -> str:
        """
        将图标拷贝到目标文件夹下(图标文件不是ico格式则自动转换)
        :param target_path: 目标文件夹路径
        :param icon_path: 图标文件路径
        :return: 图标名称
        """
        is_icon = file_suffix(icon_path) == "ico"

        # 改名为 name + .ico
        ico_name = file_name(icon_path) if is_icon else f"{file_name(icon_path)}.ico"
        target_ico_path = path_join(target_path, ico_name)

        if file_exists(target_ico_path):
            # 修改正常文件方便操作文件
            win32api.SetFileAttributes(target_ico_path, win32con.FILE_ATTRIBUTE_NORMAL)

        if is_icon:
            file_copy(icon_path, target_ico_path)
        else:
            try:
                logger.debug(f"图标格式不为ico尝试转换并转移到目标文件:{icon_path} => {target_ico_path}")
                img2ico(icon_path, target_ico_path)
            except Exception as err:
                raise Exception(f"转换格式异常[{icon_path}]:{err}")

        # 设置ico属性 隐藏
        win32api.SetFileAttributes(target_ico_path, win32con.FILE_ATTRIBUTE_HIDDEN)

        return ico_name

    def _edit_icon_item(self, rule: EditRule) -> None:
        """
        替换图标
        :param rule: 规则
        :return:
        """
        try:
            if not file_exists(rule.folder_path):
                if self._conf.is_make_dirs:
                    logger.warning(f"目标文件夹不存在,已创建:{rule.folder_path}")
                    os.makedirs(rule.folder_path)
                else:
                    logger.error(f"目标文件夹不存在{rule.folder_path}")
                    rule.set_error("目标文件夹不存在")
                    return
            if not file_exists(rule.icon_path):
                logger.error(f"图标不存在{rule.icon_path}")
                rule.set_error("图标不存在")
                return

            # 拷贝图标到目标目录
            icon_name = self._copy_icon_to_target(rule.folder_path, rule.icon_path)

            # 更新 desktop.ini
            self._update_desktop_ini(rule.folder_path, icon_name)

            # 刷新目标文件夹更新图标
            win32api.SetFileAttributes(rule.folder_path, win32con.FILE_ATTRIBUTE_READONLY)
            logger.info(f"图标设置成功:{rule.folder_path}")
            rule.status = RuleStatus.SUCCESS
        except Exception as err:
            logger.error(f"图标设置失败:{err}")
            rule.set_error(f"{err}")

    def edit_icon(self) -> None:
        """
        替换图标
        :return:
        """
        self._init_edit_rule_list()
        logger.info("开始修改图标!!!")
        [self._edit_icon_item(rule) for rule in self._edit_rule_list if rule.status == RuleStatus.DOING]
        logger.info("修改图标完成!!!")
        self._generate_result(True)

    def _recover_icon_item(self, rule: RecoverRule) -> None:
        """
        恢复图标
        :param rule: 规则
        :return:
        """
        try:
            if not file_exists(rule.folder_path):
                logger.warning(f"目标文件夹不存在{rule.folder_path}")
                return

            ini_path = path_join(rule.folder_path, "desktop.ini")
            if not file_exists(ini_path):
                logger.warning(f"目标文件夹配置文件不存在{ini_path}")
                return

            before_attr = win32api.GetFileAttributes(ini_path)

            win32api.SetFileAttributes(ini_path, win32con.FILE_ATTRIBUTE_NORMAL)
            ini = read_ini(ini_path)

            if ini.has_section(self._section_shell_class_info) \
                    and ini.has_option(self._section_shell_class_info, self._option_icon_resource):
                ini.remove_option(self._section_shell_class_info, self._option_icon_resource)
                write_ini(ini, ini_path)

                win32api.SetFileAttributes(ini_path, before_attr)

                logger.info(f"文件夹已恢复默认图标:{rule.folder_path}")
            else:
                logger.warning(f"配置文件不存在相关参数:{ini_path}")

            rule.status = RuleStatus.SUCCESS
        except Exception as err:
            logger.warning(f"文件恢复异常:{err}")
            rule.set_error(f"{err}")

    def recover_icon(self) -> None:
        """
        恢复图标
        :return:
        """
        self._init_recover_rule_list()
        logger.info("开始恢复默认图标!!!")
        [self._recover_icon_item(rule) for rule in self._recover_rule_list if rule.status == RuleStatus.DOING]
        logger.info("恢复默认图标完成!!!")
        self._generate_result(False)
