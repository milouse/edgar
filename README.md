# Edgar

`edgar` is a small utility to help one maintain their huge SSH config
file. It's heavilly inspired by [concierge](https://github.com/9seconds/concierge)
(even the tests are directly taken from the `concierge` examples!).

## Installation

`edgar` only support python3. We are now in 2019!

```sh
$ python -m venv edgar-venv
$ source edgar-venv/bin/activate
$ pip install --upgrade pip build
$ python -m build
$ pip install dist/edgar-x.y.tar.gz
```

Unit tests can be run with `python -m unittest`.

## Usage

Contrary to `concierge`, there is no inotify support. The main idea is
that you are not always modifying your SSH config file and it's not that
hard to just call manually `edgar` when your config template is ready.

`edgar` rely on a config file stored in your `~/.config` folder:
`~/.config/edgar.yml`. As its name show it, this is a YAML file.

This file should contain a list of host configurations. Thus the most
simple config file may be:

```yml
---
- Host: m1
  Hostname: 192.168.1.42
  User: edgar
- Host: m2
  Hostname: 192.168.1.43
  User: edgar
```

Which will output the following:

```
Host m1
  Hostname 192.168.1.42
  User edgar

Host m2
  Hostname 192.168.1.43
  User edgar
```

If the main object is not a list, it is taken as a primary host
configuration named `*`:

```yml
---
CheckHostIP: yes
Compression: yes
StrictHostKeyChecking: accept-new
ServerAliveInterval: 120
ServerAliveCountMax: 2
HashKnownHosts: yes
IdentitiesOnly: yes
AddKeysToAgent: yes

hosts:
  - Host: m1
    Hostname: 192.168.1.42
    User: edgar
  - Host: m2
    Hostname: 192.168.1.43
    User: edgar
```

Which will output the following:

```
Host m1
  Hostname 192.168.1.42
  User edgar

Host m2
  Hostname 192.168.1.43
  User edgar

Host *
  AddKeysToAgent yes
  CheckHostIP yes
  Compression yes
  HashKnownHosts yes
  IdentitiesOnly yes
  ServerAliveCountMax 2
  ServerAliveInterval 120
  StrictHostKeyChecking accept-new
```

Finally, `edgar` understands sub-hosts and ansible-like `loop` (or
legacy `with_items`) processing:

```yml
---
CheckHostIP: yes
Compression: yes
StrictHostKeyChecking: accept-new
ServerAliveInterval: 120
ServerAliveCountMax: 2
HashKnownHosts: yes
IdentitiesOnly: yes
AddKeysToAgent: yes

hosts:
  - Host: m
    User: edgar
    hide: yes
    hosts:
      - Host: e{item}
        Hostname: 10.10.0.{item}
        ViaProxy: gw2
        loop: range(2)
  - Host: blog
    User: sa
```

Which will output the following:

```
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
  AddKeysToAgent yes
  CheckHostIP yes
  Compression yes
  HashKnownHosts yes
  IdentitiesOnly yes
  ServerAliveCountMax 2
  ServerAliveInterval 120
  StrictHostKeyChecking accept-new
```

## Reference

`edgar` understands all config options from an up-to-date OpenSSH config
options list. As for OpenSSH itself, option names are case
insensitive. However, during config generation process, option names
will be written following the OpenSSH naming convention and
alphabetically sorted under `Host` or `Match` blocks. The `Host` and
`Match` blocks order is kept as provided, but all "orphaned" options are
gathered inside a single `Host *` block, which is always output last.

It also understands the following supplementary options:

- `blocks` :: define a listing of `Host` or `Match` block, each of them
  will inherit from the current block parameters. For historical reason,
  this option can be named `hosts`, but this is deprecated.
- `hide` :: whether a specific configuration for the current block
  should be output or if it should be only used for factorization
  purpose of its sub-block. Value must be a boolean. Default is `no`
  (false).
- `prefix` :: whether the current block name should be concatenated with
  it's sub-blocks name. Value must be a boolean. Default is `yes`
  (true).
- `loop` :: (or legacy `with_items`) define that the current block
  configuration must be duplicated for each item of this list. Value
  must be something python is able to iterate over (a list, a range
  expression…). You can use the `{item}` tag in any option value of the
  same block.
- `ViaProxy <host>` :: shortcut helper, which expands to
  `ProxyCommand ssh -W %h:%p <host>`.

## FAQ

- **Edgar crash with a weird error message about YAML parser**
  1. Don't forget to add the colon between the SSH parameter and its
     value.
  2. Some values must be protected, like the one with `*`. For exemple:
     `Host: "*.toto.com"`.
