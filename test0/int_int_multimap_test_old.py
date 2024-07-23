import builtins
from collections.abc import Iterable
from dataclasses import dataclass
import inspect
import sys
from typing import ForwardRef
import unittest


from src0.collections.int_int_multimap_old import IntIntMultimapOld


IntIntMultimapTest = ForwardRef("IntIntMultimapTest")


if __name__ == "__main__":
    orig_stdout = sys.stdout
    def trace_print(*args, **kwargs):
        kwargs["file"] = orig_stdout
        builtins.print(*args, **kwargs)


@dataclass
class _TestData:
    _items: Iterable[tuple[int, int]]
    _keys: tuple[int, ...]
    _notkeys: tuple[int, ...]
    _values: tuple[int, ...]
    _notvalues: tuple[int, ...]


class TestData:
    @staticmethod
    def empty() -> _TestData:
        trace_print(inspect.currentframe().f_code.co_name)
        return _TestData(
            _items = tuple(),
            _keys = tuple(),
            _notkeys = (-1, 0, 1, 2, 3),
            _values = tuple(),
            _notvalues = (-1, 0, 1, 2, 3),
        )

    @staticmethod
    def single_item() -> _TestData:
        trace_print(inspect.currentframe().f_code.co_name)
        return _TestData(
            _items = ((1, 2),),
            _keys = (1,),
            _notkeys = (-1, 0, 2, 3),
            _values = (2,),
            _notvalues = (-1, 0, 1, 3),
        )

    @staticmethod
    def two_different_keys() -> _TestData:
        trace_print(inspect.currentframe().f_code.co_name)
        return _TestData(
            _items = ((1, 2), (3, 4)),
            _keys = (1, 3),
            _notkeys = (-1, 0, 2, 4),
            _values = (2, 4),
            _notvalues = (-1, 0, 1, 3),
        )    

    @staticmethod
    def same_key_two_values() -> _TestData:
        trace_print(inspect.currentframe().f_code.co_name)
        return _TestData(
            _items = ((1, 2), (1, 3)),
            _keys = (1,),
            _notkeys = (-1, 0, 2, 3, 4),
            _values = (2, 3),
            _notvalues = (-1, 0, 1, 4),
        )

    @staticmethod
    def two_symmetric() -> _TestData:
        trace_print(inspect.currentframe().f_code.co_name)
        return _TestData(
            _items = ((1, 2), (2, 1),),
            _keys = (1, 2),
            _notkeys = (-1, 0, 3, 4),
            _values = (1, 2),
            _notvalues = (-1, 0, 3, 4),
        )

class TestMethods:
    @staticmethod
    def test_init(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimapOld()
        assertions.assertEqual(obj.total, 0)
        for key in obj.keys():
            assertions.fail()
        for key, value in obj.items():
            assertions.fail()
    
    @staticmethod
    def test_add_smoke(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimapOld()
        for key, value in data._items:
            obj.add(key, value)

    @staticmethod
    def test_total(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimapOld()
        for key, value in data._items:
            obj.add(key, value)
        assertions.assertEqual(obj.total, len(data._items))

    @staticmethod
    def test_keys(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimapOld()
        for key, value in data._items:
            obj.add(key, value)
        keys_from_obj = obj.keys()
        for key in keys_from_obj:
            assertions.assertIn(key, data._keys)
            assertions.assertNotIn(key, data._notkeys)
        for key in data._keys:
            assertions.assertIn(key, keys_from_obj)
        for notkey in data._notkeys:
            assertions.assertNotIn(notkey, keys_from_obj)

    @staticmethod
    def test_clear(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimapOld()
        for key, value in data._items:
            obj.add(key, value)
        obj.clear()
        assertions.assertEqual(obj.total, 0)
        keys_from_obj = obj.keys()
        assertions.assertEqual(len(keys_from_obj), 0)
        for key in keys_from_obj:
            assertions.fail()
        assertions.assertEqual(len(obj.items()), 0)
        for key, value in obj.items():
            assertions.fail()
        assertions.assertEqual(len(obj.value_sets()), 0)
        for key in data._keys:
            assertions.assertNotIn(key, keys_from_obj)
        value_sets_from_pbj = obj.value_sets()
        for key in value_sets_from_pbj:
            assertions.fail()
        for key in data._keys:
            assertions.assertNotIn(key, value_sets_from_pbj)

    @staticmethod
    def test_discard_iter(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimapOld()
        for key, value in data._items:
            obj.add(key, value)
        for key, value in data._items:
            obj.discard(key, value)
        assertions.assertEqual(obj.total, 0)
        for key in obj.keys():
            assertions.fail()
        for key, value in obj.items():
            assertions.fail()
        for key in data._keys:
            assertions.assertNotIn(key, obj.keys())
        ### TODO check if value_sets() can iterate on (key, values)
        # for key, values in obj.value_sets():
        #     assertions.fail()
        

class IntIntMultimapTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_all(self):
        trace_print(inspect.currentframe().f_code.co_name)
        data_methods = [
            TestData.empty,
            TestData.single_item,
            TestData.two_different_keys,
            TestData.same_key_two_values,
            TestData.two_symmetric,
        ]
        assert_methods = [
            TestMethods.test_init,
            TestMethods.test_add_smoke,
            TestMethods.test_total,
            TestMethods.test_keys,
            TestMethods.test_clear,
            TestMethods.test_discard_iter,
        ]
        for data_idx, data_method in enumerate(data_methods):
            for assert_idx, assert_method in enumerate(assert_methods):
                data_name = f"[{data_idx}]{data_method.__name__}"
                assert_name = f"[{assert_idx}]{assert_method.__name__}"
                with self.subTest(",".join((data_name, assert_name))):
                    data = data_method()
                    assert_method(self, data)


if __name__ == "__main__":
    unittest.main()
   
