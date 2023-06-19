import subprocess

openssh_options = subprocess.run(
    "zcat /usr/share/man/man5/ssh_config.5.gz | sed -n 's/^.It Cm \\([^ ]*\\)$/\\1/p'",
    shell=True, text=True, capture_output=True
).stdout.strip()

lines = [f"    \"{option.lower()}\": \"{option}\""
         for option in openssh_options.split("\n")]
lines.append("    \"viaproxy\": \"ViaProxy\"")
content = ",\n".join(lines)
print(f"VALID_SSH_OPTIONS = {{\n{content}\n}}")
