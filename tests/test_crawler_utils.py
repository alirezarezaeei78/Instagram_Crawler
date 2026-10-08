from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from crawler_utils import profile_username, validate_configuration


class ConfigurationTests(unittest.TestCase):
    def test_only_profile_urls_are_collected(self):
        self.assertEqual(profile_username('https://www.instagram.com/example.user/?source=dialog'), 'example.user')
        self.assertEqual(profile_username('/sample_user/'), 'sample_user')
        for href in [None, 'https://other.example/user/', '/p/abc/', '/explore/', '/accounts/', '//evil.example/user/', 'javascript:alert(1)']:
            self.assertIsNone(profile_username(href), href)

    def test_invalid_configuration_fails_before_browser_start(self):
        for values in [('', '', 'target', 10), ('user', 'pass', '../bad', 10), ('user', 'pass', 'target', 0)]:
            with self.assertRaises(ValueError):
                validate_configuration(*values)
        validate_configuration('user', 'pass', 'target', 10)


if __name__ == '__main__':
    unittest.main()
