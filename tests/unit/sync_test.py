"""Sync module tests"""
import unittest

from hubsync import sync


class SyncTestCase(unittest.TestCase):
    def test_yesno_as_boolean_yes(self):
        self.assertTrue(sync.yesno_as_boolean("yes"))

    def test_yesno_as_boolean_no(self):
        self.assertFalse(sync.yesno_as_boolean("no"))


class ZipPairsTestCase(unittest.TestCase):
    def test_empty_lists(self):
        self.assertEqual(
            [],
            list(sync.zip_pairs([], []))
        )

    def test_empty_first_list(self):
        self.assertEqual(
            [(1, None)],
            list(sync.zip_pairs([1], []))
        )

    def test_empty_second_list(self):
        self.assertEqual(
            [(None, 1)],
            list(sync.zip_pairs([], [1]))
        )

    def test_single_element_lists(self):
        self.assertEqual(
            set([(1, 1), (1, None)]),
            set(sync.zip_pairs([1, 1], [1]))
        )

    def test_non_matching_elements(self):
        self.assertEqual(
            set([(None, 2), (1, None)]),
            set(sync.zip_pairs([1], [2]))
        )

    def test_unordered_matching(self):
        self.assertEqual(
            set([(1, 1), (2, 2)]),
            set(sync.zip_pairs([1, 2], [2, 1]))
        )

    def test_diff_length_non_matching_lower(self):
        self.assertEqual(
            set([('etcaterva', 'etcaterva'), ('aa', None)]),
            set(sync.zip_pairs(['aa', 'etcaterva'], ['etcaterva']))
        )

    def test_diff_length_non_matching_higher(self):
        self.assertEqual(
            set([('zz', None), ('etcaterva', 'etcaterva')]),
            set(sync.zip_pairs(['zz', 'etcaterva'], ['etcaterva']))
        )

if __name__ == '__main__':
    unittest.main()
