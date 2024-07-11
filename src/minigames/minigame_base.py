import builtins
from collections.abc import Sequence, Callable
import inspect
from typing import Literal

from src.textio_sys import TextInputOutputBase

class MiniGameBase:
    MAX_BAD_INPUT_ABORT: Literal[20] = 20
    player_io: TextInputOutputBase

    def __init__(
        self,
        player_io: TextInputOutputBase,
        *args,
        **kwargs,
    ) -> None:
        self.player_io = player_io

    def run_minigame_menu(
        self,
        menu_items: Sequence[tuple[str, str, Sequence[Callable[[], None]]]],
    ) -> str:
        """Asks player to choose from a menu.
        Each menu item is defined as:
            cmdkey: str
                An abbrevation or initialism for this command. Must be unique.
            cmdname: str
                Description of what this command does.
            commit_fn_list: Sequence of no-argument, no-output callables.
                Code that will be executed when the command is selected.
        """
        assert all(
            (
                type(cmdkey) == str and 
                type(cmdname) == str and 
                all(
                    builtins.callable(commit_fn) 
                    for commit_fn in commit_fn_list
                )
            )
            for cmdkey, cmdname, commit_fn_list in menu_items
        )
        player_io = self.player_io
        cmd_dict = {
            cmdkey.upper() : cmd_index
            for cmd_index, (cmdkey, _, _) in enumerate(menu_items)
        }
        player_io.print("[[MENU_ITEMS_BEGIN]]")
        for cmdkey, cmdname, _ in menu_items:
            player_io.print(f"[[{cmdkey}]] : {cmdname}")
        player_io.print("[[MENU_ITEMS_END]]")
        asked_count = 0
        choice_made = False
        while not choice_made:
            choice = player_io.input()
            choice = choice.upper()
            choice_made = choice in cmd_dict
            if choice_made:
                choice_index = cmd_dict[choice]
                choice_key = menu_items[choice_index][0]
                break
            else:
                player_io.print("[[BAD_INPUT]]")
                asked_count += 1
                if asked_count >= self.MAX_BAD_INPUT_ABORT:
                    player_io.print("[[BAD_INPUT_COUNT_EXCEED]]")
                    raise Exception("[[BAD_INPUT_COUNT_EXCEED]]")
            pass # while(not choice_made)
        print(f"[[DEBUG]] choice_index={choice_index}, choice_key={choice_key}")
        print("[[DEBUG]] started executing menu commit functions")
        chosen_commit_fn_list = menu_items[choice_index][2]
        for commit_fn in chosen_commit_fn_list:
            print(f"[[INSPECT]] {inspect.getsource(commit_fn)}")
            commit_fn()
        print("[[DEBUG]] finished executing menu commit functions")
        return choice_key
