import builtins
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from enum import auto as enum_auto
import inspect
import sys
import typing
from typing import ForwardRef, Callable
import unittest

from src0.collections.int_int_multimap import IIMM2

Assertions = unittest.TestCase
TestSubject = IIMM2


if __name__ == "__main__":
    orig_stdout = sys.stdout
    def trace_print(*args, **kwargs):
        kwargs["file"] = orig_stdout
        builtins.print(*args, **kwargs)

IIMM2Test = ForwardRef("IIMM2Test")


class MethodList:
    _type: type
    _names: list[str]
    _fn_objs: list[typing.Any]
    _enabled: list[bool]

    def __init__(
        self,
        _type: type,
        exclude_private: bool = True,
        exclude_sunder: bool = True,
        exclude_dunder: bool = True,
        exclude_builtins: bool = True,
        exclude_patterns: Iterable[str] = None,
    ):
        if not isinstance(_type, type):
            raise Exception("Expects class type.")
        self._type = _type
        self._names = list()
        self._fn_objs = list()
        self._enabled = list()
        for name, fn in inspect.getmembers(_type, predicate=inspect.isfunction):
            starts_u1 = name.startswith("_")
            if exclude_private and starts_u1:
                continue
            ends_u1 = name.endswith("_")
            if exclude_sunder and starts_u1 and ends_u1:
                continue
            starts_u2 = starts_u1 and name.startswith("__")
            ends_u2 = ends_u1 and name.endswith("__")
            if exclude_dunder and starts_u2 and ends_u2:
                continue
            if exclude_builtins and inspect.isbuiltin(fn):
                continue
            if exclude_patterns and any(bool(pat in name) for pat in exclude_patterns):
                continue
            self._names.append(name)
            self._fn_objs.append(fn)
            self._enabled.append(True)

    def names(self) -> Iterable[str]:
        for name, enable in zip(self._names, self._enabled):
            if not enable:
                continue
            yield name

    def get_callable(self, instance: typing.Any, name: str) -> Callable:
        if not isinstance(instance, self._type):
            raise Exception("Expects an instance of the class type.")
        bound_fn = getattr(instance, name)
        return bound_fn


@dataclass
class TestData:
    items: Iterable[tuple[int, int]]
    keys: Iterable[int]
    notkeys: Iterable[int]
    values: Iterable[int]
    notvalues: Iterable[int]


class TestDataFactory:
    def __init__(self) -> None:
        pass

    def named_cases(self) -> Iterable[tuple[str, TestData]]:
        methods = MethodList(TestDataFactory)
        for name in methods.names():
            if not name.startswith("create_"):
                continue
            fn = methods.get_callable(self, name)
            data = fn()
            yield (name, data)

    def create_empty(self) -> TestData:
        return TestData(
            items = tuple(),
            keys = tuple(),
            notkeys = (-1, 0, 1, 2, 3),
            values = tuple(),
            notvalues = (-1, 0, 1, 2, 3),
        )

    def create_single_item(self) -> TestData:
        return TestData(
            items = ((1, 2),),
            keys = (1,),
            notkeys = (-1, 0, 2, 3),
            values = (2,),
            notvalues = (-1, 0, 1, 3),
        )

    def create_two_different_keys(self) -> TestData:
        return TestData(
            items = ((1, 2), (3, 4)),
            keys = (1, 3),
            notkeys = (-1, 0, 2, 4),
            values = (2, 4),
            notvalues = (-1, 0, 1, 3),
        )    

    def create_same_key_two_values(self) -> TestData:
        return TestData(
            items = ((1, 2), (1, 3)),
            keys = (1,),
            notkeys = (-1, 0, 2, 3, 4),
            values = (2, 3),
            notvalues = (-1, 0, 1, 4),
        )

    def create_two_symmetric(self) -> TestData:
        return TestData(
            items = ((1, 2), (2, 1),),
            keys = (1, 2),
            notkeys = (-1, 0, 3, 4),
            values = (1, 2),
            notvalues = (-1, 0, 3, 4),
        )


class SubjectInitMode(Enum):
    AT_INIT = "AT_INIT"
    FROM_OTHER = "FROM_OTHER"
    ADD_ITEM_SINGLE = "ADD_ITEM_SINGLE"
    ADD_ITEMS_PLURAL = "ADD_ITEMS_PLURAL"


class TestSubjectFactory:
    _test_data: TestData
    _init_mode: SubjectInitMode
    _subject: TestSubject

    def __init__(self, test_data: TestData, init_mode: SubjectInitMode) -> None:
        assert isinstance(test_data, TestData)
        assert isinstance(init_mode, SubjectInitMode)
        self._test_data = test_data
        self._init_mode = init_mode
        self._subject = None

    @property
    def subject(self) -> TestSubject:
        if self._subject is None:
            items = self._test_data.items
            match self._init_mode:
                case SubjectInitMode.AT_INIT:
                    self._subject = TestSubject(items=items)
                case SubjectInitMode.FROM_OTHER:
                    dummy = TestSubject(items=items)
                    self._subject = TestSubject(other=dummy)
                case SubjectInitMode.ADD_ITEM_SINGLE:
                    self._subject = TestSubject()
                    for key, value in items:
                        self._subject.add_item(key, value)
                case SubjectInitMode.ADD_ITEMS_PLURAL:
                    self._subject = TestSubject()
                    self._subject.add_items(items)
        return self._subject


class SizedChecker:
    _assertions: Assertions
    _subject: TestSubject

    def __init__(self, **kwargs) -> None:
        self._assertions = kwargs["assertions"]
        self._subject = kwargs["subject"]

    def has_len(self):
        _ = len(self._subject)

    def len_returns_int(self):
        value = len(self._subject)
        self._assertions.assertEqual(value, int(value))

    def len_not_negative(self):
        value = len(self._subject)
        self._assertions.assertGreaterEqual(value, 0)


class IterableChecker:
    _assertions: Assertions
    _subject: TestSubject
    _expected_length: int
    _type_check: Callable[[typing.Any], bool]

    def __init__(
        self, 
        assertions: Assertions,
        subject: TestSubject,
        expected_length: int,
        type_check: Callable[[typing.Any], bool],
    ) -> None:
        self._assertions = assertions
        self._subject = subject
        self._expected_length = expected_length
        self._type_check = type_check

    def can_iter_unless_empty(self):
        """Checks that, if the object is presumed to be not empty, its iterator will yield something.
        Conversely, if it is presumed empty, it should not yield anything.
        """
        if self._expected_length > 0:
            for _ in self._subject:
                return ### early out on success
            self._assertions.fail("Expected not empty, but iteration does not yield anything.")
        else:
            for _ in self._subject:
                self._assertions.fail("Expected empty, but iteration yields something.")

    def iter_count_equals_len(self):
        actual_count = 0
        for _ in self._subject:
            actual_count += 1
        self._assertions.assertEqual(actual_count, self._expected_length)

    def iter_type_check(self):
        for iter_content in self._subject:
            self._assertions.assertTrue(self._type_check(iter_content))
     

class MappingChecker:
    _assertions: Assertions
    _subject: TestSubject
    _value_check_fn: Callable[[typing.Any], bool]
    _non_keys: Iterable[typing.Any]

    def __init__(
        self, 
        assertions: Assertions, 
        subject: TestSubject,
        value_check_fn: Callable[[typing.Any], bool],
        non_keys: Iterable[typing.Any],
    ) -> None:
        self._assertions = assertions
        self._subject = subject
        self._value_check_fn = value_check_fn
        self._non_keys = non_keys

    def iter_yields_keys_implies_contains_var1(self):
        for key in self._subject:
            self._assertions.assertTrue(self._subject.__contains__(key))
        
    def iter_yields_keys_implies_contains_var2(self):
        for key in self._subject:
            self._assertions.assertTrue(key in self._subject)

    def iter_yields_keys_implies_contains_var3(self):
        for key in self._subject:
            self._assertions.assertIn(key, self._subject)

    def iter_yields_keys_can_getitem_var1(self):
        for key in self._subject:
            _ = self._subject.__getitem__(key)

    def iter_yields_keys_can_getitem_var2(self):
        for key in self._subject:
            _ = self._subject[key]

    def getitem_type_check(self):
        for key in self._subject:
            value = self._subject[key]
            self._assertions.assertTrue(self._value_check_fn(value))

    def nonkeys_contains_false_var1(self):
        """Checks that, for each of the provided "non-keys",
        the test subject should return false for membership.
        """
        for nk in self._non_keys:
            self._assertions.assertFalse(self._subject.__contains__(nk))

    def nonkeys_contains_false_var2(self):
        for nk in self._non_keys:
            self._assertions.assertFalse(nk in self._subject)

    def nonkeys_contains_false_var3(self):
        for nk in self._non_keys:
            self._assertions.assertNotIn(nk, self._subject)


class IIMM2Test(unittest.TestCase):

    def test(self):
        iterable_checker_methods = MethodList(IterableChecker)
        mapping_checker_methods = MethodList(MappingChecker)
        data_factory = TestDataFactory()
        for data_name, test_data in data_factory.named_cases():
            for init_mode in list(SubjectInitMode):
                init_mode_name = init_mode.name
                subject_factory = TestSubjectFactory(test_data, init_mode)
                ### IterableChecker on subject
                for test_name in iterable_checker_methods.names():
                    full_name = ",".join((data_name, init_mode_name, test_name))
                    trace_print(full_name)
                    with self.subTest(full_name):
                        ### All test code must be inside the subTest() block.
                        subject = subject_factory.subject
                        key_check = lambda k: type(k) == int
                        expected_key_count = len(set(test_data.keys))
                        checker = IterableChecker(self, subject, expected_key_count, key_check)
                        test_method = iterable_checker_methods.get_callable(checker, test_name)
                        test_method()
                ### MappingChecker on subject
                for test_name in mapping_checker_methods.names():
                    full_name = ",".join((data_name, init_mode_name, test_name))
                    trace_print(full_name)
                    with self.subTest(full_name):
                        ### All test code must be inside the subTest() block.
                        subject = subject_factory.subject
                        value_check = lambda vs: all(v in test_data.values for v in vs) and not any(v in vs for v in test_data.notvalues)
                        checker = MappingChecker(self, subject, value_check, test_data.notkeys)
                        test_method = mapping_checker_methods.get_callable(checker, test_name)
                        test_method()


if __name__ == "__main__":
    unittest.main()
