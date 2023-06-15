import os
import yaml
import datetime
from collections import namedtuple


VALID_SSH_OPTIONS = {
    "AddKeysToAgent",
    "AddressFamily",
    "BatchMode",
    "BindAddress",
    "BindInterface",
    "CanonicalDomains",
    "CanonicalizeFallbackLocal",
    "CanonicalizeHostname",
    "CanonicalizeMaxDots",
    "CanonicalizePermittedCNAMEs",
    "CASignatureAlgorithms",
    "CertificateFile",
    "CheckHostIP",
    "Ciphers",
    "ClearAllForwardings",
    "Compression",
    "ConnectionAttempts",
    "ConnectTimeout",
    "ControlMaster",
    "ControlPath",
    "ControlPersist",
    "DynamicForward",
    "EnableEscapeCommandline",
    "EnableSSHKeysign",
    "EscapeChar",
    "ExitOnForwardFailure",
    "FingerprintHash",
    "ForkAfterAuthentication",
    "ForwardAgent",
    "ForwardX11",
    "ForwardX11Timeout",
    "ForwardX11Trusted",
    "GatewayPorts",
    "GlobalKnownHostsFile",
    "GSSAPIAuthentication",
    "GSSAPIDelegateCredentials",
    "HashKnownHosts",
    "Host",
    "HostbasedAcceptedAlgorithms",
    "HostbasedAuthentication",
    "HostKeyAlgorithms",
    "HostKeyAlias",
    "Hostname",
    "IdentitiesOnly",
    "IdentityAgent",
    "IdentityFile",
    "IgnoreUnknown",
    "Include",
    "IPQoS",
    "KbdInteractiveAuthentication",
    "KbdInteractiveDevices",
    "KexAlgorithms",
    "KnownHostsCommand",
    "LocalCommand",
    "LocalForward",
    "LogLevel",
    "LogVerbose",
    "MACs",
    "Match",
    "NoHostAuthenticationForLocalhost",
    "NumberOfPasswordPrompts",
    "PasswordAuthentication",
    "PermitLocalCommand",
    "PermitRemoteOpen",
    "PKCS11Provider",
    "Port",
    "PreferredAuthentications",
    "ProxyCommand",
    "ProxyJump",
    "ProxyUseFdpass",
    "PubkeyAcceptedAlgorithms",
    "PubkeyAuthentication",
    "RekeyLimit",
    "RemoteCommand",
    "RemoteForward",
    "RequestTTY",
    "RequiredRSASize",
    "RevokedHostKeys",
    "SecurityKeyProvider",
    "SendEnv",
    "ServerAliveCountMax",
    "ServerAliveInterval",
    "SessionType",
    "SetEnv",
    "StdinNull",
    "StreamLocalBindMask",
    "StreamLocalBindUnlink",
    "StrictHostKeyChecking",
    "SyslogFacility",
    "TCPKeepAlive",
    "Tunnel",
    "TunnelDevice",
    "UpdateHostKeys",
    "User",
    "UserKnownHostsFile",
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
in `~/.edgarrc`. This source file must be a valid YAML document. A
specific source file can be given with the `config_file` argument.

You can specifies the SSH config file name to use with `output_file`
argument. It defaults to `~/.ssh/config`. If the value `-` is given,
the result will be printed on the standard output."""
    def __init__(self, config_file=None, output_file=None):
        self.config_file = self.prepare_config_file(config_file)
        self.output = self.prepare_output(output_file)

        with open(self.config_file, "r") as f:
            conf = yaml.safe_load(f) or {}
        self.config = {}
        self.parse(conf)

    def __str__(self):
        return self.stringify()

    def compile_time(self):
        return datetime.datetime.utcnow().isoformat()

    def write(self):
        if self.output == "-":
            print(self.stringify())
            return
        header = """# Generated by Edgar on {date}
#
# Be aware that any manual change to it may be overwritten.
# Source: {source}

""".format(date=self.compile_time(),
           source=self.config_file)
        outputdir = os.path.dirname(self.output)
        if outputdir != "" and not os.path.exists(outputdir):
            os.mkdir(outputdir)
        with open(self.output, "w") as f:
            f.write(header)
            f.write(self.stringify() + "\n")

    def parse(self, hosts, prefix="", config={}):
        if isinstance(hosts, list):
            for h in hosts:
                c = config.copy()
                if isinstance(h, str):
                    # We are only dealing with a list of hostname
                    c.update({"Host": h})
                else:
                    c.update(h)
                self.parse_block(c, prefix)
            return
        self.parse_block(hosts, prefix)

    def prepare_config_file(self, config_file):
        candidates = ["~/.config/edgar.yml", "~/.edgarrc"]
        if config_file is not None:
            candidates.insert(0, config_file)

        for f in candidates:
            conffile = os.path.expanduser(f)
            if os.path.exists(conffile):
                return conffile

        raise EdgarNoConfigFileFoundError(
            "None of the following has been found: {}".format(
                ", ".join(candidates)
            )
        )

    def prepare_output(self, output):
        if not output:
            output = "~/.ssh/config"
        if output == "-":
            return "-"
        return os.path.expanduser(output)

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

    def format_with_item(self, text, item):
        if item is None:
            return text
        if isinstance(item, dict):
            item_type = namedtuple("Item", item.keys())
            item = item_type(**item)
        return text.format(item=item)

    def store_block(self, name, block):
        curitem = block.pop("item", None)
        name = self.format_with_item(name, curitem)
        if name not in self.config:
            self.config[name] = set()
        for opt, value in block.items():
            if isinstance(value, bool):
                value = "yes" if value else "no"
            elif not isinstance(value, str):
                value = str(value)
            else:
                value = self.format_with_item(value, curitem)
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
            config["item"] = i
            self.process_block(name, block, config)
