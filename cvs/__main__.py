import argparse
import logging
import os
from cvs import errors
from cvs.app import VersionsSystem
from cvs.validator import CommandValidator

# tempfile.tempdir
def validate_args(args) -> None:
    app = VersionsSystem()
    if args.command == "init" or args.command == "ini":
        CommandValidator.validate_init()
        app.init_command()
    elif args.command == "add":
        CommandValidator.validate_add(args.path)
        app.add_command(args.path)
    elif args.command == "log":
        CommandValidator.validate_log()
        app.log_command()
    elif args.command == "commit" or args.command == "com":
        CommandValidator.validate_commit()
        app.make_commit(args.comment)


def set_up_arguments() -> None:
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init", help="Инициализировать репозиторий", aliases=["ini"])
    parser_commit = subparsers.add_parser("commit", help="Сделать коммит", aliases=["com"])
    parser_add = subparsers.add_parser("add", help="Индексировать файл(ы)")
    subparsers.add_parser("log", help="Вывести историю коммитов")

    parser.add_argument("-d", "--debug", action="store_true", help="Запуск в режиме отладки")
    parser_add.add_argument("path", type=str, help="Путь к файлу/директории")
    parser_commit.add_argument("comment", type=str, help="Комментарий к коммиту")


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
        validate_args(cmd_args)
        logger.info("Executing command")

    except errors.APIError as e:
        logger.error(f"API error occurred: {str(e)}")
    except Exception as e:
        logger.exception("Exception caught: ", e)
    finally:
        logger.info("Closing application")
        exit()
