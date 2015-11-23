"""Sync module tests"""
import unittest

from hubsync import sync


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
            [(1, 1), (1, None)],
            list(sync.zip_pairs([1, 1], [1]))
        )

    def test_non_matching_elements(self):
        self.assertEqual(
            [(None, 2), (1, None)],
            list(sync.zip_pairs([1], [2]))
        )

    def test_unordered_matching(self):
        self.assertEqual(
            [(1, 1), (2, 2)],
            list(sync.zip_pairs([1, 2], [2, 1]))
        )

if __name__ == '__main__':
    unittest.main()
