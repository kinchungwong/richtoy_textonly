import builtins
from abc import ABC, abstractmethod

class TextInputOutputBase(ABC):
    @abstractmethod
    def print(self, *args) -> None:
        pass
    
    @abstractmethod
    def input(self) -> str:
        pass

class DefaultTextInputOutput(TextInputOutputBase):
    print_prefix: str
    auto_enter: bool

    def __init__(
        self,
        print_prefix: str = None,
        auto_enter: bool = False,
    ) -> None:
        self.print_prefix = ("[[" + print_prefix + "]]") if print_prefix else None
        self.auto_enter = auto_enter

    def print(self, *args) -> None:
        builtins.print(self.print_prefix, *args)
    
    def input(self) -> str:
        if self.auto_enter:
            return ""
        need_prefix = len(self.print_prefix) > 0
        if need_prefix:
            self.print("[[READLINE_START]]")
        s = builtins.input()
        if need_prefix:
            self.print("[[READLINE_FINISH]]")
        return s

class BroadcastTextInputOutput(TextInputOutputBase):
    items: list[TextInputOutputBase]

    def __init__(
        self, 
    ) -> None:
        self.items = []

    def add(self, item: TextInputOutputBase) -> None:
        assert isinstance(item, TextInputOutputBase)
        self.items.append(item)

    def print(self, *args) -> None:
        for item in self.items:
            item.print(*args)
    
    def input(self) -> str:
        raise NotImplementedError(self.input.__qualname__)
