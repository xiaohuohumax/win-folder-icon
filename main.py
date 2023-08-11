import argparse
import logging
import sys

from dacite import from_dict

from data import Conf
from core import WinFolderIconTool
from log import logger, update_level

if __name__ == '__main__':
    try:
        epilog = "玩的开心(^v^)"

        pr = argparse.ArgumentParser(add_help=False, epilog=epilog, description="Windows 文件夹图标工具")
        pr.set_defaults(func=lambda _: pr.print_help())

        add_subparsers = pr.add_subparsers(help="模式选择")

        # 公共参数
        pr.add_argument('-h', '--help', action='help', help='显示帮助信息')

        pr.add_argument('-s', '--result-path', metavar='', type=str, default=Conf.result_path,
                        help=f"执行结果路径[默认:{Conf.result_path}]")
        pr.add_argument('-d', '--debug', action='store_true', dest="is_debug", help="是否调试[默认:否]")

        # 修改模式参数
        pr_edit = add_subparsers.add_parser("edit", help="修改模式(将文件夹图标修改为指定图标)", add_help=False,
                                            description="替换图标模式", epilog=epilog)
        pr_edit.add_argument('-h', '--help', action='help', help='显示帮助信息')
        pr_edit.add_argument('-e', '--edit-rule-path', metavar='', type=str, default=Conf.edit_rule_path,
                             help=f"修改规则文件路径[默认:{Conf.edit_rule_path}]")
        pr_edit.add_argument('-m', '--make-dirs', action='store_true', dest="is_make_dirs",
                             help="文件夹不存时是否创建[默认:否]")
        pr_edit.set_defaults(func=lambda x: pr_edit.print_help() or WinFolderIconTool(config=x).edit_icon())

        # 恢复模式参数
        pr_recover = add_subparsers.add_parser("recover", help="恢复模式(将文件夹图标恢复为系统默认图标)", add_help=False,
                                               description="恢复图标模式", epilog=epilog)
        pr_recover.add_argument('-h', '--help', action='help', help='显示帮助信息')
        pr_recover.add_argument('-r', '--recover-rule-path', metavar='', type=str, default=Conf.recover_rule_path,
                                help=f"恢复规则文件路径[默认:{Conf.recover_rule_path}]")
        pr_recover.set_defaults(func=lambda x: pr_recover.print_help() or WinFolderIconTool(config=x).recover_icon())

        args = pr.parse_args()
        conf = from_dict(data_class=Conf, data=vars(args))

        if conf.is_debug:
            update_level(logging.DEBUG)

        args.func(conf)
    except Exception as e:
        logger.error(f"工具执行异常:{e}")
        sys.exit(-1)
