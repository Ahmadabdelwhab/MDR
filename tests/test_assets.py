import unittest

from app.assets import BIN_COUNT, BIN_NAMES


class AssetTests(unittest.TestCase):
    def test_refinement_uses_four_baskets(self):
        self.assertEqual(BIN_COUNT, 4)
        self.assertEqual(set(BIN_NAMES), {1, 2, 3, 4})
        self.assertNotIn("Birr", BIN_NAMES.values())


if __name__ == "__main__":
    unittest.main()
