import os
import unittest
from unittest.mock import patch
from edgar.edgar import Edgar


def local_expanduser(path):
    return path.replace("~/", "")


@patch('os.path.expanduser', side_effect=local_expanduser)
class TestEdgar(unittest.TestCase):
    def tearDown(self):
        os.unlink(".edgarrc")

    def test_01_simple_parse(self, mock_path):
        test = """---
- Host: name
  HostName: 127.0.0.1
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        self.assertIn("name", e.config.keys())
        result = "Host name\n  HostName 127.0.0.1"
        self.assertEqual(str(e), result.strip())

    def test_02_simple_sub_list_parse(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: name
  HostName: 127.0.0.1
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host *
  Compression yes

Host name
  HostName 127.0.0.1
"""
        self.assertEqual(str(e), result.strip())

    def test_03_parse_wildcard(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: name
  HostName: 127.0.0.1
- Host: "*"
  CompressionLevel: 9
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host *
  Compression yes
  CompressionLevel 9

Host name
  HostName 127.0.0.1
"""
        self.assertEqual(str(e), result.strip())

    def test_04_parse_sub_sub_list(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: name
  HostName: 127.0.0.1
  hosts:
  - Host: q
    ViaProxy: env1
    HostName: node-1
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host *
  Compression yes

Host name
  HostName 127.0.0.1

Host nameq
  HostName node-1
  ProxyCommand ssh -W %h:%p env1
"""
        self.assertEqual(str(e), result.strip())

    def test_05_parse_via_proxy(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: name
  HostName: 127.0.0.1
  hide: yes
  hosts:
  - Host: q
    ViaProxy: env1
    HostName: node-1
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host *
  Compression yes

Host nameq
  HostName node-1
  ProxyCommand ssh -W %h:%p env1
"""
        self.assertEqual(str(e), result.strip())

    def test_06_parse_with_items(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: m
  User: edgar
  Protocol: 2
  hide: yes
  hosts:
  - Host: e{item}
    HostName: 10.10.0.{item}
    ViaProxy: gw2
    with_items: range(2)
- Host: blog
  User: sa
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host *
  Compression yes

Host me0
  HostName 10.10.0.0
  Protocol 2
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host me1
  HostName 10.10.0.1
  Protocol 2
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host blog
  User sa
"""
        self.assertEqual(str(e), result.strip())

    def test_07_parse_hide_feature(self, mock_path):
        test = """---
- Host: name
  User: edgar
  hide: yes
  hosts:
  - Host: q
    HostName: 127.0.0.1
  - Host: r
    HostName: 127.0.0.2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host nameq
  HostName 127.0.0.1
  User edgar

Host namer
  HostName 127.0.0.2
  User edgar
"""
        self.assertEqual(str(e), result.strip())

    def test_08_parse_prefix_feature(self, mock_path):
        test = """---
- Host: name
  User: edgar
  prefix: no
  hosts:
  - Host: q
    HostName: 127.0.0.1
  - Host: r
    HostName: 127.0.0.2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host name
  User edgar

Host q
  HostName 127.0.0.1
  User edgar

Host r
  HostName 127.0.0.2
  User edgar
"""
        self.assertEqual(str(e), result.strip())

    def test_09_parse_with_hide_prefix(self, mock_path):
        test = """---
- Host: name
  User: edgar
  hide: yes
  prefix: no
  hosts:
  - Host: q
    HostName: 127.0.0.1
  - Host: r
    HostName: 127.0.0.2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host q
  HostName 127.0.0.1
  User edgar

Host r
  HostName 127.0.0.2
  User edgar
"""
        self.assertEqual(str(e), result.strip())


if __name__ == '__main__':
    unittest.main()
