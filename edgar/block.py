from .formatter import format_with_item, format_body_line


class Block(object):
    """An OpenSSH config block wrapper.

OpenSSH client config are organized as a long listing of options
separated into "blocks".  By block we are referring to group of options
related to a specific `Match` or `Host` option.
    """
    def __init__(self, block):
        self.name = None
        self.internals = {}
        self.config = block

        self.clean_config()
        self.extract_name_and_type()

    def clean_config(self):
        internal_options = [
            "blocks", "hide", "item", "prefix", "prefix_value"
        ]
        self.internals = {key: self.config.pop(key)
                          for key in internal_options
                          if key in self.config}
        # Support old hosts option
        if "hosts" in self.config:
            self.internals["blocks"] = self.config.pop("hosts")

    def extract_name_and_type(self):
        for option in ["Host", "Match", "host", "match"]:
            self.name = self.config.pop(option, None)
            if self.name is None:
                continue
            self.internals["type"] = option.title()
            break
        if self.name is None:
            self.name = "*"
            self.internals["type"] = "Host"
            return
        prefix = self.get("prefix_value") or ""
        self.name = prefix + self.name

    def get(self, key, default=None):
        return self.internals.get(key, default)

    def header(self):
        return "{} {}".format(
            self.internals["type"],
            format_with_item(self.name, self.get("item"))
        )

    def body(self):
        body = set()
        for option, value in self.config.items():
            line = format_body_line(option, value, self.get("item"))
            if line is not None:
                body.add(line)
        return body

    def children_config(self):
        if self.name == "*":
            return {}
        new_config = self.config
        if self.internals.get("prefix", True):
            new_config["prefix_value"] = self.name
        return new_config
