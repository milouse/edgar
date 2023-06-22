import re
import requests


OPENSSH_VERSION = "V_9_3"

data = requests.get(f"https://anongit.mindrot.org/openssh.git/plain/readconf.c?h={OPENSSH_VERSION}")

known_derivation = {
    "gssapiauthentication": "GSSAPIAuthentication",
    "gssapidelegatecredentials": "GSSAPIDelegateCredentials",
    "identityfile2": "IdentityFile2",
    "macs": "MACs",
    "syslogfacility": "SyslogFacility",
    "updatehostkeys": "UpdateHostKeys"
}

tokens = []
keywords = {}
parser_step = 0

keyword_rx = re.compile("\\A\\s+{ \"(\\w+)\", o(\\w+) },(?:\\s+/\\*.+)?\\Z")

for line in data.text.splitlines():
    if line == "typedef enum {":
        parser_step = 1
        continue
    if line == "} keywords[] = {":
        parser_step = 2
        continue
    if line == "} OpCodes;":
        parser_step = 0
        continue

    if parser_step == 0:
        continue
    if parser_step == 1:
        for token in line.split(","):
            clean_token = token.strip()
            if clean_token == "":
                continue
            tokens.append(clean_token)
        continue

    # We can only be there in parser_step == 2
    if line == "};":
        break
    match = keyword_rx.match(line)
    if not match:
        continue
    if match[2] == "Unsupported":
        if match[1] in keywords:
            continue
    elif match[1] in known_derivation:
        keywords[match[1]] = known_derivation[match[1]]
    else:
        keywords[match[1]] = match[2]

# import subprocess
# openssh_options = subprocess.run(
#     "zcat /usr/share/man/man5/ssh_config.5.gz | sed -n 's/^.It Cm \\([^ ]*\\)$/\\1/p'",
#     shell=True, text=True, capture_output=True
# ).stdout.strip()
#
# lines = [f"    \"{option.lower()}\": \"{option}\""
#          for option in openssh_options.split("\n")]

lines = [f"    \"{keyword}\": \"{option}\""
         for keyword, option in keywords.items()
         if keyword not in ["host", "match"]]
lines.sort()
lines.insert(0, "    \"match\": \"Match\"")
lines.insert(0, "    \"host\": \"Host\"")
lines.append("    \"viaproxy\": \"ViaProxy\"")
content = ",\n".join(lines)
print(f"VALID_SSH_OPTIONS = {{\n{content}\n}}")
