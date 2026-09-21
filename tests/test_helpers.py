import unittest

from app.helpers import center_text, display_char, smoothstep


class HelperTests(unittest.TestCase):
    def test_smoothstep_stays_between_zero_and_one(self):
        self.assertEqual(smoothstep(0), 0)
        self.assertEqual(smoothstep(1), 1)
        self.assertEqual(smoothstep(0.5), 0.5)

    def test_center_text_returns_requested_width(self):
        result = center_text("MDR", 7)

        self.assertEqual(len(result), 7)
        self.assertEqual(result, "  MDR  ")

    def test_display_char_supports_small_and_large_digits(self):
        self.assertEqual(display_char(12, False), "2")
        self.assertEqual(display_char(12, True), "２")


if __name__ == "__main__":
    unittest.main()
