import builtins
from typing import Callable

from src.textio_sys import TextInputOutputBase

class TextInputOutputHistory:
    _data: list[tuple[bool, str]]
    def __init__(self) -> None:
        self._data = []
    
    def print(self, s: str) -> None:
        self._data.append((False, s))

    def post_input(self, s: str) -> None:
        self._data.append((True, s))

    def tail(
        self,
        max_count: int = 50,
        include_prints: bool = True,
        include_inputs: bool = True,
        menus_only: bool = False,
    ) -> list[str]:
        data = self._data
        data_len = len(data)
        selected: list[int] = []
        has_menu_started = False
        for reverse_idx in range(data_len):
            idx = data_len - 1 - reverse_idx
            item = data[idx]
            item_is_input = item[0]
            item_is_print = not item_is_input
            item_str = item[1]
            if item_is_input and not include_inputs:
                continue
            if item_is_print and not include_prints:
                continue
            if menus_only:
                if "[[MENU_ITEMS_END]]" in item_str:
                    has_menu_started = True
                    selected.append(idx)
                elif "[[MENU_ITEMS_BEGIN]]" in item_str:
                    has_menu_started = False
                    selected.append(idx)
                    break # for(reverse_idx)
                elif has_menu_started:
                    selected.append(idx)
                else:
                    pass
            else:
                selected.append(idx)
                if len(selected) >= max_count:
                    break # for(reverse_idx)
            pass # for(reverse_idx)
        return [data[idx][1] for idx in selected[::-1]]

class AgentHistoryTextInputOutput(TextInputOutputBase):
    input_fn: Callable[[TextInputOutputHistory], str]
    history: TextInputOutputHistory

    def __init__(self, input_fn: Callable[[TextInputOutputHistory], str]):
        assert builtins.callable(input_fn)
        self.input_fn = input_fn
        self.history = TextInputOutputHistory()

    def print(self, *args) -> None:
        filtered_args = []
        for arg in args:
            if arg is None:
                continue
            s_arg = arg if (type(arg) == str) else str(arg)
            if len(s_arg) == 0:
                continue
            filtered_args.append(s_arg)
        s = " ".join(filtered_args)
        self.history.print(s)
        builtins.print(s)

    def input(self) -> str:
        return self.input_fn(self.history)
