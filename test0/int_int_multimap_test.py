from collections.abc import Iterable
import typing
import unittest


from src0.collections.int_int_multimap import IntIntMultimap

class IntIntMultimapEmptyTest(unittest.TestCase):
    def test_smoke(self):
        _ = IntIntMultimap()

    def test_len_is_zero(self):
        obj = IntIntMultimap()
        self.assertEqual(len(obj), 0)

    def test_iter_expect_noexec(self):
        obj = IntIntMultimap()
        for _ in obj:
            self.fail("When empty, iterating on obj.__iter__() should not have received values.")

    def test_items_expect_noexec(self):
        obj = IntIntMultimap()
        for _, _ in obj.items():
            self.fail("When empty, iterating on obj.items() should not have received values.")

    def test_contains_key(self):
        obj = IntIntMultimap()
        for k in range(-10, 11):
            self.assertFalse(k in obj, "When empty, __contains__(key) should return false.")
    
    def test_contains_item(self):
        obj = IntIntMultimap()
        for k in range(-10, 11):
            for v in range(-10, 11):
                self.assertFalse(obj.contains_item(k, v), "When empty, contains_item(key, value) should return false.")

    def test_clear_smoke_1(self):
        obj = IntIntMultimap()
        obj.clear()

    def test_copy_smoke_1(self):
        obj = IntIntMultimap()
        _ = obj.copy()


class IntIntMultimapSingleItemReadTest(unittest.TestCase):

    def setUp(self):
        self.key_one = 1
        self.value_two = 2

    def create_object(self) -> IntIntMultimap:
        obj = IntIntMultimap()
        obj.add(self.key_one, self.value_two)
        return obj

    def test_smoke(self):
        obj = self.create_object()

    def test_len_is_one(self):
        obj = self.create_object()
        self.assertEqual(len(obj), 1)

    def test_iter_expect_one(self):
        obj = self.create_object()
        for key in obj:
            self.assertEqual(key, self.key_one)

    def test_items_expect_one(self):
        obj = self.create_object()
        for key, value in obj.items():
            self.assertEqual((key, value), (self.key_one, self.value_two))

    def test_contains_key(self):
        obj = self.create_object()
        self.assertTrue(self.key_one in obj)

    def test_contains_key_not(self):
        obj = self.create_object()
        self.assertFalse(self.value_two in obj)

    def test_contains_item(self):
        obj = self.create_object()
        self.assertTrue(obj.contains_item(self.key_one, self.value_two))

    def test_contains_item_not(self):
        obj = self.create_object()
        self.assertFalse(obj.contains_item(self.value_two, self.key_one))

    def test_clear_smoke_1(self):
        obj = self.create_object()
        obj.clear()

    def test_clear_len_is_zero(self):
        obj = self.create_object()
        obj.clear()
        self.assertEqual(len(obj), 0)

    def test_copy_smoke_1(self):
        obj = self.create_object()
        copied = obj.copy()

    def test_copy_len_is_one(self):
        obj = self.create_object()
        copied = obj.copy()
        for key, value in copied.items():
            self.assertEqual((key, value), (self.key_one, self.value_two))


class IntIntMultimapSingleItemIdempotentTest(unittest.TestCase):

    def setUp(self):
        self.key_one = 1
        self.value_two = 2

    def create_object(self) -> IntIntMultimap:
        obj = IntIntMultimap()
        obj.add(self.key_one, self.value_two)
        obj.add(self.key_one, self.value_two)
        return obj

    def test_smoke(self):
        obj = self.create_object()

    def test_len_is_one(self):
        obj = self.create_object()
        self.assertEqual(len(obj), 1)

    def test_iter_expect_one(self):
        obj = self.create_object()
        iter_count = 0
        for key in obj.keys():
            self.assertEqual(key, self.key_one)
            iter_count += 1
        self.assertEqual(iter_count, 1)

    def test_items_expect_one(self):
        obj = self.create_object()
        iter_count = 0
        for key, value in obj.items():
            self.assertEqual((key, value), (self.key_one, self.value_two))
            iter_count += 1
        self.assertEqual(iter_count, 1)

    def test_contains_key(self):
        obj = self.create_object()
        self.assertTrue(self.key_one in obj)

    def test_contains_key_not(self):
        obj = self.create_object()
        self.assertFalse(self.value_two in obj)

    def test_contains_item(self):
        obj = self.create_object()
        self.assertTrue(obj.contains_item(self.key_one, self.value_two))

    def test_contains_item_not(self):
        obj = self.create_object()
        self.assertFalse(obj.contains_item(self.value_two, self.key_one))

    def test_clear_smoke_1(self):
        obj = self.create_object()
        obj.clear()

    def test_clear_len_is_zero(self):
        obj = self.create_object()
        obj.clear()
        self.assertEqual(len(obj), 0)

    def test_copy_smoke_1(self):
        obj = self.create_object()
        copied = obj.copy()

    def test_copy_len_is_one(self):
        obj = self.create_object()
        copied = obj.copy()
        iter_count = 0
        for key, value in copied.items():
            self.assertEqual((key, value), (self.key_one, self.value_two))
            iter_count += 1
        self.assertEqual(iter_count, 1)

class IntIntMultimapMultiKeyReadTest(unittest.TestCase):

    def setUp(self):
        self._kv_1_2 = (1, 2)
        self._kv_3_4 = (3, 4)
    
    def create_object(self) -> IntIntMultimap:
        obj = IntIntMultimap()
        obj.add(*self._kv_1_2)
        obj.add(*self._kv_3_4)
        return obj

    def test_smoke(self):
        obj = self.create_object()

    def test_len_is_two(self):
        obj = self.create_object()
        self.assertEqual(len(obj), 2)

    def test_iter_expect_two(self):
        obj = self.create_object()
        expected_keyset = set([
            self._kv_1_2[0],
            self._kv_3_4[0],
        ])
        iter_count = 0
        for key in obj.keys():
            self.assertIn(key, expected_keyset)
            iter_count += 1
        self.assertEqual(iter_count, 2)

    def test_items_expect_one(self):
        obj = self.create_object()
        expected_itemset = set([
            self._kv_1_2,
            self._kv_3_4,
        ])
        iter_count = 0
        for key, value in obj.items():
            self.assertIn((key, value), expected_itemset)
            iter_count += 1
        self.assertEqual(iter_count, 2)

    def test_contains_key(self):
        obj = self.create_object()
        expected_keyset = set([
            self._kv_1_2[0],
            self._kv_3_4[0],
        ])
        for expected_key in expected_keyset:
            self.assertIn(expected_key, obj)

    def test_contains_key_not(self):
        obj = self.create_object()
        not_expected_keyset = set([
            self._kv_1_2[1],
            self._kv_3_4[1],
        ])
        for not_expected_key in not_expected_keyset:
            self.assertNotIn(not_expected_key, obj)

    def test_contains_item(self):
        obj = self.create_object()
        expected_itemset = set([
            self._kv_1_2,
            self._kv_3_4,
        ])
        for key, value in expected_itemset:
            self.assertTrue(obj.contains_item(key, value))

    def test_contains_item_not(self):
        obj = self.create_object()
        not_expected_itemset = set([
            tuple(reversed(self._kv_1_2)),
            tuple(reversed(self._kv_3_4)),
        ])
        for not_key, not_value in not_expected_itemset:
            self.assertFalse(obj.contains_item(not_key, not_value))

    def test_clear_smoke_1(self):
        obj = self.create_object()
        obj.clear()

    def test_clear_len_is_zero(self):
        obj = self.create_object()
        obj.clear()
        self.assertEqual(len(obj), 0)

    def test_copy_smoke_1(self):
        obj = self.create_object()
        copied = obj.copy()

    def test_copy_len_is_two(self):
        obj = self.create_object()
        copied = obj.copy()
        expected_itemset = set([
            self._kv_1_2,
            self._kv_3_4,
        ])
        iter_count = 0
        for key, value in copied.items():
            self.assertIn((key, value), expected_itemset)
            iter_count += 1
        self.assertEqual(iter_count, 2)


# class IntIntMultimapMultiValueReadTest(unittest.TestCase):

#     def setUp(self):
#         self._kv_1_2 = (1, 2)
#         self._kv_1_4 = (1, 4)
    
#     def create_object(self) -> IntIntMultimap:
#         obj = IntIntMultimap()
#         obj.add(*self._kv_1_2)
#         obj.add(*self._kv_1_4)
#         return obj

#     def test_smoke(self):
#         obj = self.create_object()

#     def test_len_is_two(self):
#         obj = self.create_object()
#         self.assertEqual(len(obj), 2)

#     def test_iter_expect_one(self):
#         obj = self.create_object()
#         expected_keyset = set([
#             self._kv_1_2[0],
#             self._kv_1_4[0],
#         ])
#         iter_count = 0
#         for key in obj:
#             self.assertIn(key, expected_keyset)
#             iter_count += 1
#         self.assertEqual(iter_count, 1)

#     def test_items_expect_one(self):
#         obj = self.create_object()
#         expected_itemset = set([
#             self._kv_1_2,
#             self._kv_3_4,
#         ])
#         iter_count = 0
#         for key, value in obj.items():
#             self.assertIn((key, value), expected_itemset)
#             iter_count += 1
#         self.assertEqual(iter_count, 2)

#     def test_contains_key(self):
#         obj = self.create_object()
#         expected_keyset = set([
#             self._kv_1_2[0],
#             self._kv_3_4[0],
#         ])
#         for expected_key in expected_keyset:
#             self.assertIn(expected_key, obj)

#     def test_contains_key_not(self):
#         obj = self.create_object()
#         not_expected_keyset = set([
#             self._kv_1_2[1],
#             self._kv_3_4[1],
#         ])
#         for not_expected_key in not_expected_keyset:
#             self.assertNotIn(not_expected_key, obj)

#     def test_contains_item(self):
#         obj = self.create_object()
#         expected_itemset = set([
#             self._kv_1_2,
#             self._kv_3_4,
#         ])
#         for key, value in expected_itemset:
#             self.assertTrue(obj.contains_item(key, value))

#     def test_contains_item_not(self):
#         obj = self.create_object()
#         not_expected_itemset = set([
#             tuple(reversed(self._kv_1_2)),
#             tuple(reversed(self._kv_3_4)),
#         ])
#         for not_key, not_value in not_expected_itemset:
#             self.assertFalse(obj.contains_item(not_key, not_value))

#     def test_clear_smoke_1(self):
#         obj = self.create_object()
#         obj.clear()

#     def test_clear_len_is_zero(self):
#         obj = self.create_object()
#         obj.clear()
#         self.assertEqual(len(obj), 0)

#     def test_copy_smoke_1(self):
#         obj = self.create_object()
#         copied = obj.copy()

#     def test_copy_len_is_two(self):
#         obj = self.create_object()
#         copied = obj.copy()
#         expected_itemset = set([
#             self._kv_1_2,
#             self._kv_3_4,
#         ])
#         iter_count = 0
#         for key, value in copied.items():
#             self.assertIn((key, value), expected_itemset)
#             iter_count += 1
#         self.assertEqual(iter_count, 2)


if __name__ == "__main__":
    unittest.main()
