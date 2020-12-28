import argparse
import logging

from cvs import errors
from cvs.app import VersionsSystem
from cvs.view import CliView
from cvs import commands


def extract_arguments(command_name: str) -> tuple:
    if command_name == "add":
        return raw_args.path,
    elif command_name == "commit":
        return raw_args.comment,


def set_up_arguments() -> None:
    subparsers = parser.add_subparsers(
        dest="command", required=True, metavar="<command>"
    )
    subparsers.add_parser(
        "init", help="Инициализировать репозиторий"
    )
    parser_commit = subparsers.add_parser(
        "commit", help="Сделать коммит"
    )
    parser_add = subparsers.add_parser("add", help="Индексировать файл(ы)")
    subparsers.add_parser("log", help="Вывести историю коммитов")
    subparsers.add_parser("status", help="Показать статус")

    parser.add_argument(
        "-d", "--debug", action="store_true", help="Запуск в режиме отладки"
    )
    parser_add.add_argument("path", type=str, help="Путь к файлу/директории")
    parser_commit.add_argument(
        "comment", type=str, help="Комментарий к коммиту"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    set_up_arguments()
    raw_args = parser.parse_args()
    app = VersionsSystem(CliView())

    logging.basicConfig(
        level=logging.DEBUG if raw_args.debug else logging.ERROR
    )
    logger = logging.getLogger(__name__)
    try:
        command = commands.REGISTRY[raw_args.command](app)
        command(*extract_arguments(raw_args.command))
    except errors.APIError as e:
        logger.error(f"API error occurred: {str(e)}")
    except Exception as e:
        logger.exception("Exception caught: ", e)
    finally:
        logger.info("Closing application")
        exit()
