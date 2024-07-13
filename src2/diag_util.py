import builtins
from collections.abc import Iterable
from typing import Any, Optional, Union


class TextDiagnosticsInternals:
    excluded_names: set[str]
    excluded_types: set[type]

    def __init__(
        self,
        excluded_names: Iterable[str],
        excluded_types: Iterable[type],
    ) -> None:
        self.excluded_names = set(excluded_names)
        self.excluded_types = set(excluded_types)

    def classdict_formatter(
        self,
        classname: str,
        classdict: dict[str, Any],
        use_skip: bool = False,
    ) -> Iterable[str]:
        prefix_str = (" " * 4)
        for attrname, attrval in classdict.items():
            if attrname in self.excluded_names:
                continue
            if type(attrval) in self.excluded_types:
                continue
            yield classname
            yield "."
            yield attrname
            yield ":"
            yield "\n" ### must be on its own, workaround for newline segmentation
            yield from self.recursive_list_formatter(
                attrval, 
                prefix_str=prefix_str,
                use_skip=use_skip,
            )

    def recursive_list_formatter(
        self,
        arg: Union[Iterable, Any], 
        prefix_str: Optional[str] = None,
        use_skip: bool = False,
    ) -> Iterable[str]:
        prefix_str = prefix_str or ""
        if isinstance(arg, Iterable):
            was_skipped = False
            for idx, item in enumerate(arg):
                if type(item) in self.excluded_types:
                    continue
                if not use_skip or self.idx_filter(idx):
                    was_skipped = False
                    prefix_str_2 = prefix_str + f"[{idx}]"
                    yield from self.recursive_list_formatter(
                        item, 
                        prefix_str=prefix_str_2,
                    )
                else:
                    if not was_skipped:
                        prefix_str_2 = prefix_str + f"[{idx}...] ..."
                        yield prefix_str_2
                        yield "\n" ### must be on its own, workaround for newline segmentation
                        was_skipped = True
        else:
            if prefix_str:
                yield prefix_str
                yield " "
            yield str(arg)
            yield "\n" ### must be on its own, workaround for newline segmentation

    @classmethod
    def idx_filter(cls, idx: int) -> bool:
        assert type(idx) == int
        if idx <= 8:
            return True
        while (idx >= 16) and ((idx & 1) == 0):
            idx >>= 1
        return idx in (0, 3, 7, 12)


class TextDiagnosticsHelper:
    _target: Any
    _excluded_names: list[str]
    _excluded_types: list[type]
    _internals: TextDiagnosticsInternals

    def __init__(
        self,
        target: Any,
        excluded_names: list[str] = None,
        excluded_types: list[type] = None,
    ) -> None:
        self._target = target
        self._excluded_names = list(excluded_names or [])
        self._excluded_types = list(excluded_types or [])
        self._excluded_types.extend([
            TextDiagnosticsInternals,
            TextDiagnosticsHelper,
            SupportsTextDiagnostics,
        ])
        self._internals = TextDiagnosticsInternals(
            self._excluded_names,
            self._excluded_types,
        )

    def print(self, print_fn = builtins.print) -> None:
        ### BUG: when printing a very long string with many newlines
        ###      to console, the output is truncated.
        ### FIXME: strings must be segmented by newlines and then
        ###        converted into separate print() statements
        classname = type(self._target).__qualname__
        classdict = self._target.__dict__
        strs = self._internals.classdict_formatter(
            classname, 
            classdict, 
            use_skip=False,
        )
        buffer: list[str] = list()
        for s in strs:
            if s == "\n":
                print_fn("".join(buffer))
                buffer.clear()
            else:
                buffer.append(s)
        if buffer:
            print_fn("".join(buffer))

    def str(self) -> str:
        ### BUG: when printing a very long string with many newlines
        ###      to console, the output is truncated.
        ### FIXME: When __str__() is used, the caller will not be
        ###        able to print very long strings to the console.
        ###        Therefore, only shorter strings can be returned.
        classname = type(self._target).__qualname__
        classdict = self._target.__dict__
        strs = self._internals.classdict_formatter(
            classname, 
            classdict, 
            use_skip=True,
        )
        return "".join(strs)


class SupportsTextDiagnostics:
    textdiag: TextDiagnosticsHelper

    def __init__(self):
        self.textdiag = TextDiagnosticsHelper(self)
