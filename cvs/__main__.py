import argparse
import logging
from cvs import errors
from cvs.app import VersionsSystem
from cvs.view import CliView
from cvs import commands

# tempfile.tempdir


def get_command() -> commands.CvsCommand:
    if args.command == "init" or args.command == "ini":
        return commands.InitCommand(app)
    elif args.command == "add":
        return commands.AddCommand(app, args.path)
    elif args.command == "log":
        return commands.LogCommand(app)
    elif args.command == "commit" or args.command == "com":
        return commands.CommitCommand(app, args.comment)


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
    args = parser.parse_args()
    app = VersionsSystem(CliView())

    logging.basicConfig(format="[%(levelname)s]: %(asctime)s | in %(name)s | %(message)s",
                        level=logging.DEBUG if args.debug else logging.ERROR)
    logger = logging.getLogger(__name__)
    try:
        command = get_command()
        logger.info(f"Executing command: {args.command}")
        command.execute()
    except errors.APIError as e:
        logger.error(f"API error occurred: {str(e)}")
    except Exception as e:
        logger.exception("Exception caught: ", e)
    finally:
        logger.info("Closing application")
        exit()
