import builtins
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from enum import auto as enum_auto
import inspect
import sys
import typing
from typing import TypeVar, ForwardRef, Callable, Generic
import unittest

from src0.collections.int_int_multimap import IntIntMultimap
from src0.collections.int_int_multimap import ItemsView as IIMM2_ItemsView
from src0.collections.int_int_multimap import ValuesView as IIMM2_ValuesView

IntIntMultimapTest = ForwardRef("IntIntMultimapTest")
Assertions = TypeVar("Assertions", unittest.TestCase, IntIntMultimapTest)
TestSubject = TypeVar("TestSubject", IntIntMultimap, IIMM2_ItemsView, IIMM2_ValuesView)
ContentType = TypeVar("ContentType")
KeyType = TypeVar("KeyType")


if __name__ == "__main__":
    orig_stdout = sys.stdout
    def trace_print(*args, **kwargs):
        kwargs["file"] = orig_stdout
        builtins.print(*args, **kwargs)


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


class TestSubjectFactory():
    _subject_type = IntIntMultimap
    _test_data: TestData
    _init_mode: SubjectInitMode

    def __init__(self, test_data: TestData, init_mode: SubjectInitMode) -> None:
        assert isinstance(test_data, TestData)
        assert isinstance(init_mode, SubjectInitMode)
        self._test_data = test_data
        self._init_mode = init_mode

    def create(self) -> IntIntMultimap:
        items = self._test_data.items
        match self._init_mode:
            case SubjectInitMode.AT_INIT:
                return IntIntMultimap(items=items)
            case SubjectInitMode.FROM_OTHER:
                dummy = IntIntMultimap(items=items)
                return IntIntMultimap(other=dummy)
            case SubjectInitMode.ADD_ITEM_SINGLE:
                subject = IntIntMultimap()
                for key, value in items:
                    subject.add_item(key, value)
                return subject
            case SubjectInitMode.ADD_ITEMS_PLURAL:
                subject = IntIntMultimap()
                subject.add_items(items)
                return subject
            case _:
                raise Exception("Unhandled enum")


class ContainerChecker(Generic[Assertions, TestSubject, ContentType]):
    _assertions: Assertions
    _subject: TestSubject
    _expected_contains: list[ContentType]
    _expected_not_contains: list[ContentType]

    def __init__(
        self, 
        assertions: Assertions, 
        subject: TestSubject, 
        expected_contains: Iterable[ContentType],
        expected_not_contains: Iterable[ContentType],
    ) -> None:
        self._assertions = assertions
        self._subject = subject
        self._expected_contains = list(expected_contains)
        self._expected_not_contains = list(expected_not_contains)

    def expected_contains_returns_true_var1(self):
        for content in self._expected_contains:
            self._assertions.assertTrue(self._subject.__contains__(content))

    def expected_contains_returns_true_var2(self):
        for content in self._expected_contains:
            self._assertions.assertIn(content, self._subject)

    def not_expected_contains_returns_false_var1(self):
        for not_content in self._expected_not_contains:
            self._assertions.assertFalse(self._subject.__contains__(not_content))

    def not_expected_contains_returns_false_var2(self):
        for not_content in self._expected_not_contains:
            self._assertions.assertNotIn(not_content, self._subject)


class SizedChecker(Generic[Assertions, TestSubject]):
    _assertions: Assertions
    _subject: TestSubject

    def __init__(self, assertions: Assertions, subject: TestSubject) -> None:
        self._assertions = assertions
        self._subject = subject

    def has_len(self):
        _ = len(self._subject)

    def len_returns_int(self):
        value = len(self._subject)
        self._assertions.assertEqual(value, int(value))

    def len_not_negative(self):
        value = len(self._subject)
        self._assertions.assertGreaterEqual(value, 0)


class IterableChecker(Generic[Assertions, TestSubject, ContentType]):
    _assertions: Assertions
    _subject: TestSubject
    _expected_length: int
    _iter_content_check: Callable[[ContentType], bool]

    def __init__(
        self, 
        assertions: Assertions,
        subject: TestSubject,
        expected_length: int,
        iter_content_check: Callable[[ContentType], bool],
    ) -> None:
        self._assertions = assertions
        self._subject = subject
        self._expected_length = expected_length
        self._iter_content_check = iter_content_check

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

    def iter_content_type_check(self):
        for iter_content in self._subject:
            self._assertions.assertTrue(self._iter_content_check(iter_content))
     

class MappingChecker(Generic[Assertions, TestSubject, KeyType, ContentType]):
    _assertions: Assertions
    _subject: TestSubject
    _getitem_content_check: Callable[[ContentType], bool]
    _keys: Iterable[KeyType]
    _non_keys: Iterable[KeyType]

    def __init__(
        self, 
        assertions: Assertions, 
        subject: TestSubject,
        getitem_content_check: Callable[[ContentType], bool],
        keys: Iterable[KeyType],
        non_keys: Iterable[KeyType],
    ) -> None:
        self._assertions = assertions
        self._subject = subject
        self._getitem_content_check = getitem_content_check
        self._keys = keys
        self._non_keys = non_keys

    def iter_yields_keys_implies_contains_var1(self):
        for key in self._subject:
            self._assertions.assertIn(key, self._subject)

    @unittest.skip("Redundant because guaranteed by language.")
    def _SKIP_iter_yields_keys_implies_contains_var2(self):
        for key in self._subject:
            self._assertions.assertTrue(self._subject.__contains__(key))

    @unittest.skip("Redundant because guaranteed by language.")
    def _SKIP_iter_yields_keys_implies_contains_var3(self):
        for key in self._subject:
            self._assertions.assertTrue(key in self._subject)

    def iter_yields_keys_can_getitem_var1(self):
        for key in self._subject:
            _ = self._subject.__getitem__(key)

    def _SKIP_iter_yields_keys_can_getitem_var2(self):
        for key in self._subject:
            _ = self._subject[key]

    def getitem_content_check(self):
        for key in self._subject:
            value = self._subject[key]
            self._assertions.assertTrue(self._getitem_content_check(value))

    def keys_in_mapping_returns_false(self):
        for key in self._keys:
            self._assertions.assertIn(key, self._subject)

    def nonkeys_in_mapping_returns_false(self):
        for nk in self._non_keys:
            self._assertions.assertNotIn(nk, self._subject)

    @unittest.skip("Redundant because guaranteed by language.")
    def _SKIP_nonkeys_in_mapping_returns_false_var2(self):
        for nk in self._non_keys:
            self._assertions.assertFalse(self._subject.__contains__(nk))

    @unittest.skip("Redundant because guaranteed by language.")
    def _SKIP_nonkeys_in_mapping_returns_false_var3(self):
        for nk in self._non_keys:
            self._assertions.assertFalse(nk in self._subject)


class IntIntMultimapTest(unittest.TestCase):
    container_checker_methods = MethodList(ContainerChecker)
    sized_checker_methods = MethodList(SizedChecker)
    iterable_checker_methods = MethodList(IterableChecker)
    mapping_checker_methods = MethodList(MappingChecker)

    def setUp(self):
        self.data_factory = TestDataFactory()
        self.named_data_factories = list(self.data_factory.named_cases())
        self.named_subject_factories = [
            (data_name, init_mode.name, test_data, TestSubjectFactory(test_data, init_mode))
            for data_name, test_data in self.named_data_factories
            for init_mode in list(SubjectInitMode)
        ]

    def test_sized_on_iimm(self):
        cur_method_name = inspect.currentframe().f_code.co_name
        methods_list = self.sized_checker_methods
        for test_name in methods_list.names():
            for data_name, init_mode_name, test_data, subject_factory in self.named_subject_factories:
                full_name = ",".join((cur_method_name, data_name, init_mode_name, test_name))
                trace_print(full_name)
                with self.subTest(full_name):
                    ### All test code must be inside the subTest() block.
                    subject = subject_factory.create()
                    checker = SizedChecker(self, subject)
                    test_method = methods_list.get_callable(checker, test_name)
                    test_method()

    def test_iterable_on_iimm(self):
        cur_method_name = inspect.currentframe().f_code.co_name
        methods_list = self.iterable_checker_methods
        for test_name in methods_list.names():
            for data_name, init_mode_name, test_data, subject_factory in self.named_subject_factories:
                full_name = ",".join((cur_method_name, data_name, init_mode_name, test_name))
                trace_print(full_name)
                with self.subTest(full_name):
                    ### All test code must be inside the subTest() block.
                    subject = subject_factory.create()
                    key_check = lambda k: type(k) == int
                    expected_key_count = len(set(test_data.keys))
                    checker = IterableChecker(self, subject, expected_key_count, key_check)
                    test_method = methods_list.get_callable(checker, test_name)
                    test_method()

    def test_mapping_int2valueset_on_iimm(self):
        cur_method_name = inspect.currentframe().f_code.co_name
        methods_list = self.mapping_checker_methods
        for test_name in methods_list.names():
            for data_name, init_mode_name, test_data, subject_factory in self.named_subject_factories:
                full_name = ",".join((cur_method_name, data_name, init_mode_name, test_name))
                trace_print(full_name)
                with self.subTest(full_name):
                    ### All test code must be inside the subTest() block.
                    subject = subject_factory.create()
                    valueset_type_check = lambda vs: all(type(v) == int for v in vs)
                    valueset_content_accepted = lambda vs: all(v in test_data.values for v in vs)
                    valueset_content_not_accepted = lambda vs: not any(v in vs for v in test_data.notvalues)
                    valueset_check = lambda vs: valueset_type_check(vs) and valueset_content_accepted(vs) and valueset_content_not_accepted(vs)
                    checker = MappingChecker(self, subject, valueset_check, test_data.keys, test_data.notkeys)
                    test_method = methods_list.get_callable(checker, test_name)
                    test_method()

    def test_sized_on_itemsview(self):
        cur_method_name = inspect.currentframe().f_code.co_name
        methods_list = self.sized_checker_methods
        for test_name in methods_list.names():
            for data_name, init_mode_name, test_data, subject_factory in self.named_subject_factories:
                full_name = ",".join((cur_method_name, data_name, init_mode_name, test_name))
                trace_print(full_name)
                with self.subTest(full_name):
                    ### All test code must be inside the subTest() block.
                    subject = subject_factory.create()
                    checker = SizedChecker(self, subject.items())
                    test_method = methods_list.get_callable(checker, test_name)
                    test_method()

    def test_iterable_kvp_on_itemsview(self):
        cur_method_name = inspect.currentframe().f_code.co_name
        methods_list = self.iterable_checker_methods
        for test_name in methods_list.names():
            for data_name, init_mode_name, test_data, subject_factory in self.named_subject_factories:
                full_name = ",".join((cur_method_name, data_name, init_mode_name, test_name))
                trace_print(full_name)
                with self.subTest(full_name):
                    ### All test code must be inside the subTest() block.
                    subject = subject_factory.create()
                    kvp_type_check = lambda kv: type(kv) == tuple and len(kv) == 2 and type(kv[0]) == int and type(kv[1]) == int
                    kvp_content_check = lambda kv: kv in test_data.items
                    kvp_check = lambda kv: kvp_type_check(kv) and kvp_content_check(kv)
                    expected_count = len(set(test_data.items))
                    checker = IterableChecker(self, subject.items(), expected_count, kvp_check)
                    test_method = methods_list.get_callable(checker, test_name)
                    test_method()

    def test_container_on_itemsview(self):
        cur_method_name = inspect.currentframe().f_code.co_name
        methods_list = self.container_checker_methods
        for test_name in methods_list.names():
            for data_name, init_mode_name, test_data, subject_factory in self.named_subject_factories:
                full_name = ",".join((cur_method_name, data_name, init_mode_name, test_name))
                trace_print(full_name)
                with self.subTest(full_name):
                    ### All test code must be inside the subTest() block.
                    subject = subject_factory.create()
                    expected_contains = test_data.items
                    expected_not_contains = [
                        (not_key, not_value)
                        for not_key in test_data.notkeys
                        for not_value in test_data.notvalues
                    ]
                    checker = ContainerChecker(self, subject.items(), expected_contains, expected_not_contains)
                    test_method = methods_list.get_callable(checker, test_name)
                    test_method()

    ### TODO : tests on discard(), discard_item(), discard_items(), clear(), total()


if __name__ == "__main__":
    unittest.main()
