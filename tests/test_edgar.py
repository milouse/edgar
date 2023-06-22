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
        self.assertIn("Host name", e.config.keys())
        result = "Host name\n  Hostname 127.0.0.1"
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
Host name
  Hostname 127.0.0.1

Host *
  Compression yes
"""
        self.assertEqual(str(e), result.strip())

    def test_03_parse_wildcard(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: name
  HostName: 127.0.0.1
- Host: "*"
  ServerAliveCountMax: 2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host name
  Hostname 127.0.0.1

Host *
  Compression yes
  ServerAliveCountMax 2
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
Host name
  Hostname 127.0.0.1

Host nameq
  Hostname node-1
  ProxyCommand ssh -W %h:%p env1

Host *
  Compression yes
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
Host nameq
  Hostname node-1
  ProxyCommand ssh -W %h:%p env1

Host *
  Compression yes
"""
        self.assertEqual(str(e), result.strip())

    def test_06_parse_with_items(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: m
  User: edgar
  hide: yes
  hosts:
  - Host: e{item}
    HostName: 10.10.0.{item}
    ViaProxy: gw2
    with_items: [1, 2]
- Host: blog
  User: sa
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host me1
  Hostname 10.10.0.1
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host me2
  Hostname 10.10.0.2
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host blog
  User sa

Host *
  Compression yes
"""
        self.assertEqual(str(e), result.strip())

    def test_07_parse_with_items_with_range(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: m
  User: edgar
  hide: yes
  hosts:
  - Host: e{item}
    Hostname: 10.10.0.{item}
    ViaProxy: gw2
    with_items: range(2)
- Host: blog
  User: sa
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host me0
  Hostname 10.10.0.0
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host me1
  Hostname 10.10.0.1
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host blog
  User sa

Host *
  Compression yes
"""
        self.assertEqual(str(e), result.strip())

    def test_08_parse_with_items_with_dict(self, mock_path):
        test = """---
Compression: yes
hosts:
- Host: m
  User: edgar
  hide: yes
  hosts:
  - Host: e{item.name}
    Hostname: 10.10.0.{item.id}
    ViaProxy: gw2
    with_items:
    - id: 1
      name: toto
    - id: 2
      name: tata
- Host: blog
  User: sa
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host metoto
  Hostname 10.10.0.1
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host metata
  Hostname 10.10.0.2
  ProxyCommand ssh -W %h:%p gw2
  User edgar

Host blog
  User sa

Host *
  Compression yes
"""
        self.assertEqual(str(e), result.strip())

    def test_09_parse_hide_feature(self, mock_path):
        test = """---
- Host: name
  User: edgar
  hide: yes
  hosts:
  - Host: q
    Hostname: 127.0.0.1
  - Host: r
    Hostname: 127.0.0.2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host nameq
  Hostname 127.0.0.1
  User edgar

Host namer
  Hostname 127.0.0.2
  User edgar
"""
        self.assertEqual(str(e), result.strip())

    def test_10_parse_prefix_feature(self, mock_path):
        test = """---
- Host: name
  User: edgar
  prefix: no
  hosts:
  - Host: q
    Hostname: 127.0.0.1
  - Host: r
    Hostname: 127.0.0.2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host name
  User edgar

Host q
  Hostname 127.0.0.1
  User edgar

Host r
  Hostname 127.0.0.2
  User edgar
"""
        self.assertEqual(str(e), result.strip())

    def test_11_parse_with_hide_prefix(self, mock_path):
        test = """---
- Host: name
  User: edgar
  hide: yes
  prefix: no
  hosts:
  - Host: q
    Hostname: 127.0.0.1
  - Host: r
    Hostname: 127.0.0.2
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host q
  Hostname 127.0.0.1
  User edgar

Host r
  Hostname 127.0.0.2
  User edgar
"""
        self.assertEqual(str(e), result.strip())

    def test_12_parse_match_block(self, mock_path):
        test = """---
- Host: name
  HostName: 127.0.0.1

- Match: "Host *.example.com"
  User: test
"""
        with open(".edgarrc", "w") as f:
            f.write(test)
        e = Edgar()
        result = """
Host name
  Hostname 127.0.0.1

Match Host *.example.com
  User test
"""
        self.assertEqual(str(e), result.strip())
