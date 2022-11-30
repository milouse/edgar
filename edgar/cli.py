import edgar
from .edgar import Edgar
from argparse import ArgumentParser


def run_edgar():
    parser = ArgumentParser(description=edgar.__description__)
    parser.add_argument("-c", "--config",
                        help="Specifies a configuration file to use.")
    parser.add_argument("-o", "--output", default="~/.ssh/config",
                        help="Specifies the SSH config file name to use "
                        "(default: ~/.ssh/config). "
                        "Use - to print on terminal.")
    parser.add_argument("-v", "--version", action="store_true",
                        help="Display %(prog)s version information and exit.")
    parser.add_argument("command", nargs="?", default="store",
                        choices=["store", "show"],
                        help="What to do. (default writes ~/.ssh/config file)")
    args = parser.parse_args()

    if args.version:
        print("{} - v{}".format(edgar.__description__, edgar.__version__))
        return 0

    e = Edgar(args.config, args.output)
    if args.command == "show":
        print(e)
    else:
        e.write()
    return 0
