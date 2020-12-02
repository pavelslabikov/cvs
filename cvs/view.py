import abc


class BaseView(abc.ABC):
    @abc.abstractmethod
    def display_text(self, text: str) -> None:
        pass


class CliView(BaseView):
    def display_text(self, text: str) -> None:
        print(text)


class TestView(BaseView):
    def __init__(self):
        self.buffer = []

    def display_text(self, text: str) -> None:
        self.buffer.append(text)
