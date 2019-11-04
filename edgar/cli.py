import sys
from .edgar import Edgar


def run_edgar():
    e = Edgar()
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        print(e)
    else:
        e.write()
