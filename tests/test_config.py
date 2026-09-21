import json
import os
import tempfile
import unittest

from app.config import load_config


class ConfigTests(unittest.TestCase):
    def test_default_config_has_expected_values(self):
        config = load_config(os.path.join("app", "config.json"))

        self.assertEqual(config["fps"], 24)
        self.assertEqual(config["idle_min"], 1.2)
        self.assertIsNone(config["image"])

    def test_custom_config_overrides_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as config_file:
                json.dump({"fps": 30, "image": "art.png"}, config_file)

            config = load_config(path)

        self.assertEqual(config["fps"], 30)
        self.assertEqual(config["image"], "art.png")
        self.assertEqual(config["idle_min"], 1.2)

    def test_invalid_fps_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w", encoding="utf-8") as config_file:
                json.dump({"fps": 0}, config_file)

            with self.assertRaisesRegex(ValueError, "fps"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
