class APIError(Exception):
    arg: str


class RepoAlreadyExistError(APIError):
    def __init__(self, current_directory: str):
        self.arg = current_directory

    def __str__(self):
        return f"В директории {self.arg} уже инициализирован репозиторий"


class RepoNotFoundError(APIError):
    def __init__(self, directory: str):
        self.arg = directory

    def __str__(self):
        return f"Не удалось найти репозиторий в {self.arg}"


class InvalidPathError(APIError):
    def __init__(self, path: str):
        self.arg = path

    def __str__(self):
        return f"Недопустимый путь для индексирования - {self.arg}"


class IndexFileNotFoundError(APIError):
    def __init__(self, path: str):
        self.arg = path

    def __str__(self):
        return f"Не удалось найти файл индекса в {self.arg}"
