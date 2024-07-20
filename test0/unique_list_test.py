from typing import Union
import unittest


from src0.collections.unique_list import UniqueList


class UniqueListTest(unittest.TestCase):

    def test_init_noarg(self):
        obj = UniqueList[int]()

    def test_init_item_notc(self):
        items = [3, 1, 4, 2]
        obj = UniqueList[int](items)
        self.assertEqual(len(obj), len(items))
        for idx in range(len(items)):
            self.assertEqual(items[idx], obj[idx], "Bad result: UniqueList.__getitem__(idx)")
        for expect_idx, item in enumerate(items):
            actual_idx = obj.index(item)
            self.assertEqual(expect_idx, actual_idx, "Bad result: UniqueList.index(item)")

    def test_init_item_tc_1_shouldpass(self):
        items = [3, 1, 4, 2]
        obj = UniqueList[int](items, typecheck=int)
        self.assertEqual(len(obj), len(items))

    def test_init_item_tc_2_shouldpass(self):
        items = ["s3", "s1", "s4", "s2"]
        obj = UniqueList[str](items, typecheck=str)
        self.assertEqual(len(obj), len(items))

    @unittest.expectedFailure
    def test_init_item_tc_mismatch_1_shouldfail(self):
        items = [3, 1, 4, 2]
        _ = UniqueList[str](items, typecheck=str)

    @unittest.expectedFailure
    def test_init_item_tc_mismatch_2_shouldfail(self):
        items = ["s3", "s1", "s4", "s2"]
        _ = UniqueList[int](items, typecheck=int)

    def test_init_item_tc_true_shouldpass(self):
        items = [3, 1, 4, 2]
        obj = UniqueList[int](items, typecheck=True)
        self.assertEqual(len(obj), len(items))

    @unittest.skip("Not supported as of Python 3.11")
    @unittest.expectedFailure
    def test_init_item_tc_true_not_supported(self):
        items = ["s3", "s1", "s4", "s2"]
        obj = UniqueList[int](items, typecheck=True)
        self.assertEqual(len(obj), len(items))

    def test_init_item_tc_multi_shouldpass(self):
        items = [3, 1, "s4", 2]
        obj = UniqueList[Union[int, str]](items, typecheck=(int, str))
        self.assertEqual(len(obj), len(items))

    @unittest.expectedFailure
    def test_init_item_tc_multi_1_shouldfail(self):
        items = [3, 1, "s4", 2.5]
        _ = UniqueList[Union[int, str]](items, typecheck=(int, str))

    @unittest.expectedFailure
    def test_init_item_tc_multi_2_shouldfail(self):
        items = [3, 1, "s4", 2.5]
        _ = UniqueList[Union[int, float]](items, typecheck=(int, float))

    @unittest.expectedFailure
    def test_init_item_tc_multi_3_shouldfail(self):
        items = [3, 1, "s4", 2.5]
        _ = UniqueList[Union[str, float]](items, typecheck=(str, float))

    @unittest.expectedFailure
    def test_init_item_tc_union_1_shouldfail(self):
        items = [3, 1, "s4", 2.5]
        _ = UniqueList[Union[int, str]](items, typecheck=Union[int, str])

    @unittest.expectedFailure
    def test_init_item_tc_union_2_shouldfail(self):
        items = [3, 1, "s4", 2.5]
        _ = UniqueList[Union[int, float]](items, typecheck=Union[int, float])

    @unittest.expectedFailure
    def test_init_item_tc_union_3_shouldfail(self):
        items = [3, 1, "s4", 2.5]
        _ = UniqueList[Union[str, float]](items, typecheck=Union[str, float])

    class ItemParent:
        pass

    class ItemChild(ItemParent):
        pass

    class ItemOtherChild(ItemParent):
        pass

    class ItemNotChild:
        pass

    def test_init_item_tc_checkparent_shouldpass(self):
        items = [
            self.ItemParent(),
            self.ItemChild(),
        ]
        obj = UniqueList[self.ItemParent](items, typecheck=self.ItemParent)
        self.assertEqual(len(items), len(obj))

    @unittest.expectedFailure
    def test_init_item_tc_checkchild_shouldfail(self):
        items = [
            self.ItemParent(),
        ]
        _ = UniqueList[self.ItemChild](items, typecheck=self.ItemChild)

    @unittest.expectedFailure
    def test_init_item_tc_checkotherchild_shouldfail(self):
        items = [
            self.ItemChild(),
        ]
        _ = UniqueList[self.ItemOtherChild](items, typecheck=self.ItemOtherChild)

    @unittest.expectedFailure
    def test_init_item_tc_checknotchild_1_shouldfail(self):
        items = [
            self.ItemChild(),
        ]
        _ = UniqueList[self.ItemNotChild](items, typecheck=self.ItemNotChild)

    @unittest.expectedFailure
    def test_init_item_tc_checknotchild_2_shouldfail(self):
        items = [
            self.ItemNotChild(),
        ]
        _ = UniqueList[self.ItemChild](items, typecheck=self.ItemChild)

if __name__ == "__main__":
    unittest.main()
