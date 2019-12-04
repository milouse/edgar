import os
import yaml
import datetime


VALID_SSH_OPTIONS = {
    "AddKeysToAgent",
    "AddressFamily",
    "BatchMode",
    "BindAddress",
    "ChallengeResponseAuthentication",
    "CheckHostIP",
    "CertificateFile",
    "Cipher",
    "Ciphers",
    "Compression",
    "CompressionLevel",
    "ConnectionAttempts",
    "ConnectTimeout",
    "ControlMaster",
    "ControlPath",
    "DynamicForward",
    "EnableSSHKeysign",
    "EscapeChar",
    "ExitOnForwardFailure",
    "ForwardAgent",
    "ForwardX11",
    "ForwardX11Trusted",
    "GatewayPorts",
    "GlobalKnownHostsFile",
    "GSSAPIAuthentication",
    "GSSAPIKeyExchange",
    "GSSAPIClientIdentity",
    "GSSAPIDelegateCredentials",
    "GSSAPIRenewalForcesRekey",
    "GSSAPITrustDns",
    "HashKnownHosts",
    "HostbasedAuthentication",
    "HostKeyAlgorithms",
    "HostKeyAlias",
    "Host",
    "HostName",
    "IdentitiesOnly",
    "IdentityFile",
    "KbdInteractiveAuthentication",
    "KbdInteractiveDevices",
    "KexAlgorithms",
    "LocalCommand",
    "LocalForward",
    "LogLevel",
    "MACs",
    "NoHostAuthenticationForLocalhost",
    "NumberOfPasswordPrompts",
    "PasswordAuthentication",
    "PermitLocalCommand",
    "Port",
    "PreferredAuthentications",
    "Protocol",
    "ProxyCommand",
    "PubkeyAuthentication",
    "RekeyLimit",
    "RemoteForward",
    "RhostsRSAAuthentication",
    "RSAAuthentication",
    "SendEnv",
    "ServerAliveCountMax",
    "ServerAliveInterval",
    "SmartcardDevice",
    "StrictHostKeyChecking",
    "TCPKeepAlive",
    "Tunnel",
    "TunnelDevice",
    "UsePrivilegedPort",
    "User",
    "UserKnownHostsFile",
    "UseRoaming",
    "VerifyHostKeyDNS",
    "VisualHostKey",
    "XAuthLocation",
    "ViaProxy"
}


class EdgarNoConfigFileFoundError(FileNotFoundError):
    pass


class EdgarNotValidSSHKeywordError(KeyError):
    pass


class Edgar(object):
    """A SSH config file compiler.

Edgar compiles its source file into a valid OpenSSH config file and
optionally write the results in `~/.ssh/config`.

Edgar expects its source file to be either in `~/.config/edgar.yml` or
in `~/.edgarrc`. This source file must be a valid YAML document."""
    def __init__(self, config_file=None):
        candidates = ["~/.config/edgar.yml", "~/.edgarrc"]
        if config_file is not None:
            candidates.insert(0, config_file)
        self.conffile = None
        for f in candidates:
            conffile = os.path.expanduser(f)
            if os.path.exists(conffile):
                self.conffile = conffile
                break
        if self.conffile is None:
            raise EdgarNoConfigFileFoundError(
                "None of the following has been found: {}".format(
                    ", ".join(candidates)
                )
            )
        with open(self.conffile) as f:
            conf = yaml.safe_load(f) or {}
        self.config = {}
        self.parse(conf)

    def __str__(self):
        return self.stringify()

    def compile_time(self):
        return datetime.datetime.utcnow().isoformat()

    def write(self):
        header = """# Generated by Edgar on {date}
#
# Be aware that any manual change to it may be overwritten.
# Source: {source}

""".format(date=self.compile_time(),
           source=self.conffile)
        outputdir = os.path.expanduser("~/.ssh")
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        with open(outputdir + "/config", "w") as f:
            f.write(header)
            f.write(self.stringify() + "\n")

    def parse(self, hosts, prefix="", config={}):
        if isinstance(hosts, list):
            for h in hosts:
                c = config.copy()
                c.update(h)
                self.parse_block(c, prefix)
            return
        self.parse_block(hosts, prefix)

    def clean_block(self, block):
        cleaned_block = {}
        for opt in block.keys():
            if opt in ["hide", "hosts", "prefix", "with_items"]:
                # Quietly remove edgar instructions
                continue
            elif opt != "item" and opt not in VALID_SSH_OPTIONS:
                raise EdgarNotValidSSHKeywordError(
                    "{} is not a valid option".format(opt)
                )
            cleaned_block[opt] = block[opt]
        return cleaned_block

    def stringify(self):
        content = ""
        for host, conf in self.config.items():
            content += "Host {}\n  ".format(host)
            content += "\n  ".join(sorted(conf)) + "\n\n"
        return content.strip()

    def store_block(self, name, block):
        curitem = block.pop("item", None)
        if curitem is not None:
            name = name.format(item=curitem)
        if name not in self.config:
            self.config[name] = set()
        for opt, value in block.items():
            if isinstance(value, bool):
                value = "yes" if value else "no"
            elif not isinstance(value, str):
                value = str(value)
            elif curitem is not None:
                value = value.format(item=curitem)
            if opt == "ViaProxy":
                opt = "ProxyCommand"
                value = "ssh -W %h:%p " + value
            optline = "{option} {value}".format(option=opt, value=value)
            self.config[name].add(optline)

    def process_block(self, name, block, config):
        if not block.get("hide", False):
            self.store_block(name, config)
        subhosts = block.get("hosts", [])
        if len(subhosts) == 0:
            return
        if name == "*":
            self.parse(subhosts)
        elif block.get("prefix", True):
            self.parse(subhosts, name, config)
        else:
            self.parse(subhosts, "", config)

    def parse_block(self, block, prefix):
        name = block.pop("Host", None)
        if name is None:
            name = "*"
        else:
            name = prefix + name
        config = self.clean_block(block)
        with_items = block.get("with_items", None)
        if with_items is None:
            self.process_block(name, block, config)
            return
        loopiterator = with_items
        if isinstance(with_items, str):
            loopiterator = eval(with_items)
        for i in loopiterator:
            config["item"] = str(i)
            self.process_block(name, block, config)
