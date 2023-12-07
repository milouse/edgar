import io
import unittest
from unittest.mock import patch
from edgar.formatter import format_with_item, format_value, format_body_line
from edgar.errors import EdgarNotValidSSHKeywordError


class TestFormatter(unittest.TestCase):
    def test_01_format_with_item_with_none(self):
        self.assertEqual(
            format_with_item("Lorem ipsum", None),
            "Lorem ipsum"
        )
        self.assertEqual(
            format_with_item("Lorem {item}", None),
            "Lorem {item}"
        )
        self.assertEqual(
            format_with_item("Lorem {test}", None),
            "Lorem {test}"
        )

    def test_02_format_with_item_with_str(self):
        self.assertEqual(
            format_with_item("Lorem ipsum", "test"),
            "Lorem ipsum"
        )
        self.assertEqual(
            format_with_item("Lorem {item}", "test"),
            "Lorem test"
        )
        with self.assertRaises(KeyError):
            format_with_item("Lorem {test}", "test")

    def test_03_format_with_item_with_dict(self):
        self.assertEqual(
            format_with_item(
                "Lorem ipsum", {"test": "amet", "bibendum": "fringilla"}
            ),
            "Lorem ipsum"
        )
        # Weird known case. No way to improve it.
        self.assertEqual(
            format_with_item(
                "Lorem {item}", {"test": "amet", "bibendum": "fringilla"}
            ),
            "Lorem Item(test='amet', bibendum='fringilla')"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {test}", {"test": "amet", "bibendum": "fringilla"}
            ),
            "Lorem amet"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {test} netus {bibendum}",
                {"test": "amet", "bibendum": "fringilla"}
            ),
            "Lorem amet netus fringilla"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {item.test}", {"test": "amet", "bibendum": "fringilla"}
            ),
            "Lorem amet"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {item.test} netus {item.bibendum}",
                {"test": "amet", "bibendum": "fringilla"}
            ),
            "Lorem amet netus fringilla"
        )

    def test_04_format_with_item_with_something_else(self):
        self.assertEqual(
            format_with_item(
                "Lorem ipsum", ["test", "amet", "bibendum", "fringilla"]
            ),
            "Lorem ipsum"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {item}", ["test", "amet", "bibendum", "fringilla"]
            ),
            "Lorem ['test', 'amet', 'bibendum', 'fringilla']"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {item}", True
            ),
            "Lorem True"
        )
        self.assertEqual(
            format_with_item(
                "Lorem {item}", False
            ),
            "Lorem False"
        )

    def test_05_format_value(self):
        self.assertEqual(format_value(True, None), "yes")
        self.assertEqual(format_value(True, "test"), "yes")
        self.assertEqual(format_value(False, None), "no")
        self.assertEqual(format_value(False, "test"), "no")
        self.assertEqual(format_value("Lorem {item}", None), "Lorem {item}")
        self.assertEqual(format_value("Lorem {item}", "test"), "Lorem test")
        self.assertEqual(
            format_value(["Lorem", "Ipsum"], None),
            "['Lorem', 'Ipsum']"
        )
        self.assertEqual(
            format_value(["Lorem", "Ipsum"], "test"),
            "['Lorem', 'Ipsum']"
        )
        self.assertEqual(
            format_value(["Lorem", "{item}"], None),
            "['Lorem', '{item}']"
        )
        self.assertEqual(
            format_value(["Lorem", "{item}"], "test"),
            "['Lorem', 'test']"
        )

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_06_format_body_line(self, mock_stderr):
        self.assertEqual(
            format_body_line("hostname", "test", None),
            "Hostname test"
        )
        self.assertEqual(
            format_body_line("hostname", "test{item}", 42),
            "Hostname test42"
        )
        line = format_body_line("UseRoaming", True, None)
        self.assertEqual(
            mock_stderr.getvalue(),
            "UseRoaming is deprecated and will be ignored by OpenSSH, "
            "you should remove it now from your configuration as it "
            "may break in a future version.\n"
        )
        self.assertIsNone(line)
        with self.assertRaises(EdgarNotValidSSHKeywordError):
            format_body_line("AbsolutelyNotAnOption", "test", None)
