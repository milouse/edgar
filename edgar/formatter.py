import sys
from collections import namedtuple

from .errors import EdgarNotValidSSHKeywordError


VALID_SSH_OPTIONS = {
    "host": "Host",
    "match": "Match",
    "addkeystoagent": "AddKeysToAgent",
    "addressfamily": "AddressFamily",
    "batchmode": "BatchMode",
    "bindaddress": "BindAddress",
    "bindinterface": "BindInterface",
    "canonicaldomains": "CanonicalDomains",
    "canonicalizefallbacklocal": "CanonicalizeFallbackLocal",
    "canonicalizehostname": "CanonicalizeHostname",
    "canonicalizemaxdots": "CanonicalizeMaxDots",
    "canonicalizepermittedcnames": "CanonicalizePermittedCNAMEs",
    "casignaturealgorithms": "CASignatureAlgorithms",
    "certificatefile": "CertificateFile",
    "challengeresponseauthentication": "KbdInteractiveAuthentication",
    "checkhostip": "CheckHostIP",
    "cipher": "Deprecated",
    "ciphers": "Ciphers",
    "clearallforwardings": "ClearAllForwardings",
    "compression": "Compression",
    "connectionattempts": "ConnectionAttempts",
    "connecttimeout": "ConnectTimeout",
    "controlmaster": "ControlMaster",
    "controlpath": "ControlPath",
    "controlpersist": "ControlPersist",
    "dsaauthentication": "PubkeyAuthentication",
    "dynamicforward": "DynamicForward",
    "enableescapecommandline": "EnableEscapeCommandline",
    "enablesshkeysign": "EnableSSHKeysign",
    "escapechar": "EscapeChar",
    "exitonforwardfailure": "ExitOnForwardFailure",
    "fallbacktorsh": "Deprecated",
    "fingerprinthash": "FingerprintHash",
    "forkafterauthentication": "ForkAfterAuthentication",
    "forwardagent": "ForwardAgent",
    "forwardx11": "ForwardX11",
    "forwardx11timeout": "ForwardX11Timeout",
    "forwardx11trusted": "ForwardX11Trusted",
    "gatewayports": "GatewayPorts",
    "globalknownhostsfile": "GlobalKnownHostsFile",
    "globalknownhostsfile2": "Deprecated",
    "gssapiauthentication": "GSSAPIAuthentication",
    "gssapidelegatecredentials": "GSSAPIDelegateCredentials",
    "hashknownhosts": "HashKnownHosts",
    "hostbasedacceptedalgorithms": "HostbasedAcceptedAlgorithms",
    "hostbasedauthentication": "HostbasedAuthentication",
    "hostbasedkeytypes": "HostbasedAcceptedAlgorithms",
    "hostkeyalgorithms": "HostKeyAlgorithms",
    "hostkeyalias": "HostKeyAlias",
    "hostname": "Hostname",
    "identitiesonly": "IdentitiesOnly",
    "identityagent": "IdentityAgent",
    "identityfile": "IdentityFile",
    "identityfile2": "IdentityFile2",
    "ignoreunknown": "IgnoreUnknown",
    "include": "Include",
    "ipqos": "IPQoS",
    "kbdinteractiveauthentication": "KbdInteractiveAuthentication",
    "kbdinteractivedevices": "KbdInteractiveDevices",
    "keepalive": "TCPKeepAlive",
    "kexalgorithms": "KexAlgorithms",
    "knownhostscommand": "KnownHostsCommand",
    "localcommand": "LocalCommand",
    "localforward": "LocalForward",
    "loglevel": "LogLevel",
    "logverbose": "LogVerbose",
    "macs": "MACs",
    "nohostauthenticationforlocalhost": "NoHostAuthenticationForLocalhost",
    "numberofpasswordprompts": "NumberOfPasswordPrompts",
    "passwordauthentication": "PasswordAuthentication",
    "permitlocalcommand": "PermitLocalCommand",
    "permitremoteopen": "PermitRemoteOpen",
    "pkcs11provider": "PKCS11Provider",
    "port": "Port",
    "preferredauthentications": "PreferredAuthentications",
    "protocol": "Ignore",
    "proxycommand": "ProxyCommand",
    "proxyjump": "ProxyJump",
    "proxyusefdpass": "ProxyUseFdpass",
    "pubkeyacceptedalgorithms": "PubkeyAcceptedAlgorithms",
    "pubkeyacceptedkeytypes": "PubkeyAcceptedAlgorithms",
    "pubkeyauthentication": "PubkeyAuthentication",
    "rekeylimit": "RekeyLimit",
    "remotecommand": "RemoteCommand",
    "remoteforward": "RemoteForward",
    "requesttty": "RequestTTY",
    "requiredrsasize": "RequiredRSASize",
    "revokedhostkeys": "RevokedHostKeys",
    "rhostsauthentication": "Deprecated",
    "securitykeyprovider": "SecurityKeyProvider",
    "sendenv": "SendEnv",
    "serveralivecountmax": "ServerAliveCountMax",
    "serveraliveinterval": "ServerAliveInterval",
    "sessiontype": "SessionType",
    "setenv": "SetEnv",
    "skeyauthentication": "KbdInteractiveAuthentication",
    "smartcarddevice": "PKCS11Provider",
    "stdinnull": "StdinNull",
    "streamlocalbindmask": "StreamLocalBindMask",
    "streamlocalbindunlink": "StreamLocalBindUnlink",
    "stricthostkeychecking": "StrictHostKeyChecking",
    "syslogfacility": "SyslogFacility",
    "tcpkeepalive": "TCPKeepAlive",
    "tisauthentication": "KbdInteractiveAuthentication",
    "tunnel": "Tunnel",
    "tunneldevice": "TunnelDevice",
    "updatehostkeys": "UpdateHostKeys",
    "useprivilegedport": "Deprecated",
    "user": "User",
    "userknownhostsfile": "UserKnownHostsFile",
    "userknownhostsfile2": "Deprecated",
    "useroaming": "Deprecated",
    "usersh": "Deprecated",
    "verifyhostkeydns": "VerifyHostKeyDNS",
    "visualhostkey": "VisualHostKey",
    "xauthlocation": "XAuthLocation",
    "viaproxy": "ViaProxy"
}


def format_with_item(text, item):
    if item is None:
        return text
    if isinstance(item, dict):
        try:
            return text.format(**item)
        except KeyError:
            item_type = namedtuple("Item", item.keys())
            item = item_type(**item)
    return text.format(item=item)


def format_value(value, item):
    if isinstance(value, bool):
        return value and "yes" or "no"
    if not isinstance(value, str):
        value = str(value)
    return format_with_item(value, item)


def format_body_line(option, value, item):
    lower_opt = option.lower()
    if lower_opt not in VALID_SSH_OPTIONS:
        raise EdgarNotValidSSHKeywordError(
            f"{option} is not a valid option"
        )
    clean_option = VALID_SSH_OPTIONS[lower_opt]
    if clean_option in ["Deprecated", "Ignore"]:
        print(
            f"{option} is deprecated and will be ignored by OpenSSH, "
            "you should remove it now from your configuration as it "
            "may break in a future version.",
            file=sys.stderr
        )
        return None
    value = format_value(value, item)
    if clean_option == "ViaProxy":
        clean_option = "ProxyCommand"
        value = "ssh -W %h:%p " + value
    return f"{clean_option} {value}"


def format_block(header, body):
    lines = [f"  {line}" for line in sorted(body)]
    lines.insert(0, header)
    return "\n".join(lines)
