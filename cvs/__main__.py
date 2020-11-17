import argparse
import logging
import os
from cvs import errors
from cvs.app import VersionsSystem


def init_command(args):
    if os.path.exists(".cvs"):
        raise errors.RepoAlreadyExistError(os.getcwd())


def add_command(args):
    if not os.path.exists(args.path):
        raise FileNotFoundError(args.path)
    dir_to_add = os.path.realpath(args.path)
    if os.getcwd() != os.path.commonpath([os.getcwd(), dir_to_add]):
        raise errors.RepoNotFoundError(dir_to_add)


def log_command(args):
    if not os.path.exists(".cvs"):
        raise errors.RepoNotFoundError(os.getcwd())


def commit_command(args):
    if not os.path.exists(".cvs"):
        raise errors.RepoNotFoundError(os.getcwd())


def set_up_arguments():
    subparsers = parser.add_subparsers()
    parser_init = subparsers.add_parser("init", help="Инициализировать репозиторий", aliases=["ini"])
    parser_commit = subparsers.add_parser("commit", help="Сделать коммит", aliases=["com"])
    parser_add = subparsers.add_parser("add", help="Индексировать файл(ы)")
    parser_log = subparsers.add_parser("log", help="Вывести историю коммитов")

    parser.add_argument("-d", "--debug", action="store_true", help="Запуск в режиме отладки")
    parser_add.add_argument("path", type=str, help="Путь к файлу/директории")
    parser_commit.add_argument("comment", type=str, help="Комментарий к коммиту")

    parser_init.set_defaults(validate=init_command)
    parser_add.set_defaults(validate=add_command)
    parser_log.set_defaults(validate=log_command)
    parser_commit.set_defaults(validate=commit_command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    set_up_arguments()
    cmd_args = parser.parse_args()
    logging.basicConfig(format="[%(levelname)s]: %(asctime)s | in %(name)s | %(message)s",
                        level=logging.DEBUG if cmd_args.debug else logging.ERROR)
    logger = logging.getLogger(__name__)
    try:
        logger.info("Validating arguments")
        cmd_args.validate(cmd_args)
        logger.info("Executing command")
        cmd_args.execute(cmd_args)
    except errors.APIError as e:
        logger.error(f"API error occurred: {str(e)}")
    except Exception as e:
        logger.exception("Exception caught: ", e)
    finally:
        logger.info("Closing application")
        exit()
