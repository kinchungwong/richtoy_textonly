import builtins
from collections.abc import Iterable
from dataclasses import dataclass
import inspect
import sys
from typing import ForwardRef
import unittest


from src0.collections.int_int_multimap import IntIntMultimap


IntIntMultimapTest = ForwardRef("IntIntMultimapTest")

    def test_items_expect_noexec(self):
        obj = IntIntMultimap()
        for _, _ in obj.items():
            self.fail("When empty, iterating on obj.items() should not have received values.")

    def test_contains_key(self):
        obj = IntIntMultimap()
        assertions.assertEqual(obj.total, 0)
        for key in obj.keys():
            assertions.fail()
        for key, value in obj.items():
            assertions.fail()
    
    @staticmethod
    def test_add_smoke(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimap()
        for key, value in data._items:
            obj.add(key, value)

    @staticmethod
    def test_total(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimap()
        for key, value in data._items:
            obj.add(key, value)
        assertions.assertEqual(obj.total, len(data._items))

    @staticmethod
    def test_keys(assertions: unittest.TestCase, data: _TestData):
        trace_print(inspect.currentframe().f_code.co_name)
        obj = IntIntMultimap()
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
        obj = IntIntMultimap()
        for key, value in data._items:
            obj.add(key, value)
        obj.clear()
        assertions.assertEqual(obj.total, 0)
        keys_from_obj = obj.keys()
        assertions.assertEqual(len(keys_from_obj), 0)
        for key in keys_from_obj:
            assertions.fail()
        for key, value in obj.items():
            pass
        

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
   
