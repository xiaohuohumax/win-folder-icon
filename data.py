from dataclasses import dataclass
from enum import Enum

from util import abs_path


class RuleStatus(Enum):
    """
    执行状态
    """
    DOING = "doing"
    SUCCESS = "success"
    FAIL = "fail"


@dataclass
class Rule:
    # 源信息
    source: str
    # 行数下标
    line_number: int
    # 规则执行状态
    status: RuleStatus = RuleStatus.DOING
    # 待修改图标文件夹路径
    folder_path: str = ""
    # 失败信息
    error_info: str = "None"

    def __post_init__(self):
        self.folder_path = abs_path(self.folder_path)

    def set_error(self, error_info: str) -> None:
        """
        设置异常信息
        :param error_info: 异常信息
        :return:
        """
        self.status = RuleStatus.FAIL
        self.error_info = error_info


@dataclass
class EditRule(Rule):
    """
    修改规则
    """
    # 图标路径
    icon_path: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.icon_path = abs_path(self.icon_path)


@dataclass
class RecoverRule(Rule):
    """
    恢复规则
    """
    ...


@dataclass
class Conf:
    """
    配置信息
    """
    # 修改规则文件路径
    edit_rule_path: str = 'rules/edit_rule.txt'
    # 恢复规则文件路径
    recover_rule_path: str = 'rules/recover_rule.txt'
    # 执行结果路径
    result_path: str = 'result/result.txt'
    # 是否调试模式
    is_debug: bool = False
    # 文件夹不存在时是否创建
    is_make_dirs: bool = False

    def __post_init__(self):
        self.edit_rule_path = abs_path(self.edit_rule_path)
        self.result_path = abs_path(self.result_path)
        self.recover_rule_path = abs_path(self.recover_rule_path)
