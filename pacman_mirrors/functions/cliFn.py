#!/usr/bin/env python
#
# This file is part of pacman-mirrors.
#
# pacman-mirrors is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pacman-mirrors is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pacman-mirrors.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Frede Hundewadt <echo ZmhAbWFuamFyby5vcmcK | base64 -d>

"""Pacman-Mirrors Command Line Parser"""

# TODO add missing translations to help section

import argparse
import os
import sys
from pacman_mirrors import __version__
from pacman_mirrors.api import api_handler
from pacman_mirrors.functions import customFn
from pacman_mirrors.constants import txt
from pacman_mirrors.functions import outputFn
from pacman_mirrors.functions import mirror_status
from pacman_mirrors.functions import printFn
from pacman_mirrors.translation.custom_help_formatter import CustomHelpFormatter


def parse_command_line(self, gtk_available: bool) -> None:
    """Read the arguments of the command line"""

    args_summary = (
        f"[-h] [-f [{txt.NUMBER}]] [-i [-d]] [-m {txt.METHOD}] [--status]\n"
        f"\t\t[-c {txt.COUNTRY} [{txt.COUNTRY}...] | [--timezone] | [--continent]]\n"
        f"\t\t[-l] [-lc] [-q] [-t {txt.SECONDS}] [-v] [-n]\n"
        f"\t\t[--api] [-S/-B {txt.BRANCH}] [-p {txt.PREFIX}]\n"
        f"\t\t\t[-P {txt.PROTO} [{txt.PROTO}...]] [-R] [-U {txt.URL}]"
    )

    usage_header = f"\rVersion {__version__}\n{txt.USAGE}:\n pacman-mirrors"
    usage = f"{usage_header} {args_summary}"

    parser = argparse.ArgumentParser(
        formatter_class=CustomHelpFormatter, add_help=False, usage=usage
    )

    # Method arguments
    methods = parser.add_argument_group(txt.METHODS)
    methods.add_argument(
        "-i", "--interactive", action="store_true", help=txt.HLP_ARG_INTERACTIVE
    )

    methods_exclusive = methods.add_mutually_exclusive_group()
    methods_exclusive.add_argument(
        "-f",
        "--fasttrack",
        nargs="?",
        const=-1,
        type=int,
        metavar=txt.NUMBER,
        help=f"{txt.HLP_ARG_FASTTRACK} {txt.OVERRIDE_OPT}",
    )

    methods_exclusive.add_argument(
        "-c",
        "--country",
        type=str,
        nargs="+",
        metavar=txt.COUNTRY,
        help=txt.HLP_ARG_COUNTRY,
    )

    methods_exclusive.add_argument(
        "-z", "--timezone", action="store_true", help=txt.HLP_ARG_TIMEZONE
    )

    methods_exclusive.add_argument(
        "--continent", action="store_true", help=txt.HLP_ARG_CONTINENT
    )

    api = parser.add_argument_group(txt.API)
    api.add_argument(
        "-a",
        "--api",
        action="store_true",
        help=f"[-p {txt.PREFIX}][-R][-S/-B|-G {txt.BRANCH}][-P {txt.PROTO} [{txt.PROTO} ...]]",
    )

    api.add_argument(
        "-S",
        "-B",
        "--set-branch",
        choices=["stable", "testing", "unstable"],
        help=f"{txt.API}: {txt.HLP_ARG_API_SET_BRANCH}",
    )

    api.add_argument(
        "-p",
        "--prefix",
        type=str,
        metavar=txt.PREFIX,
        help=f"{txt.API}: {txt.HLP_ARG_API_PREFIX} {txt.PREFIX_TIP}",
    )

    api.add_argument(
        "-P",
        "--proto",
        "--protocols",
        choices=["all", "http", "https", "ftp", "ftps"],
        type=str,
        nargs="+",
        help=f"{txt.API}: {txt.HLP_ARG_API_PROTOCOLS}",
    )

    api.add_argument(
        "-R",
        "--re-branch",
        action="store_true",
        help=f"{txt.API}: {txt.HLP_ARG_API_RE_BRANCH}",
    )

    api.add_argument(
        "-U",
        "--url",
        type=str,
        metavar=txt.URL,
        help=f"{txt.API}: {txt.HLP_ARG_API_URL}",
    )

    misc = parser.add_argument_group(txt.MISC)
    misc.add_argument(
        "-G", "--get-branch", action="store_true", help=txt.HLP_ARG_API_GET_BRANCH
    )

    misc.add_argument(
        "-d",
        "--default",
        action="store_true",
        help=f"INTERACTIVE: {txt.HLP_ARG_DEFAULT}",
    )

    misc.add_argument("-h", "--help", action="store_true")
    misc.add_argument(
        "-l", "--list", "--country-list", action="store_true", help=txt.HLP_ARG_LIST
    )

    misc.add_argument(
        "-lc",
        "--country-config",
        action="store_true",
        help=txt.HLP_ARG_LIST_COUNTRIES,
    )

    misc.add_argument(
        "-m", "--method", type=str, choices=["rank", "random"], help=txt.HLP_ARG_METHOD
    )

    misc.add_argument(
        "-n", "--no-mirrorlist", action="store_true", help=txt.HLP_ARG_NO_MIRRORLIST
    )

    misc.add_argument("-q", "--quiet", action="store_true", help=txt.HLP_ARG_QUIET)

    misc.add_argument("-s", "--no-status", action="store_true", help=txt.HLP_ARG_STATUS)

    misc.add_argument(
        "-t", "--timeout", type=int, metavar=txt.SECONDS, help=txt.HLP_ARG_TIMEOUT
    )

    misc.add_argument("-v", "--version", action="store_true", help=txt.HLP_ARG_VERSION)

    misc.add_argument("--no-color", action="store_true")

    misc.add_argument("--interval", type=int, help=txt.HLP_ARG_INTERVAL)

    misc.add_argument("-g", action="store_true", help=txt.HLP_ARG_GENERATE)

    misc.add_argument("--status", action="store_true", help=txt.HLP_ARG_MIRROR_STATUS)

    misc.add_argument("-fc", action="store_true")

    args = parser.parse_args()

    # No root required
    if len(sys.argv) == 1:
        printFn.blue_msg(f"Pacman-mirrors version {__version__}")
        exit_code = mirror_status.print_status(self)
        sys.exit(exit_code)

    if args.help:
        parser.print_help()
        sys.exit(0)

    if args.version:
        print(__version__)
        sys.exit(0)

    if args.list:
        outputFn.tty_default_pool(self)
        sys.exit(0)

    if args.country_config:
        outputFn.tty_custom_pool(self)
        sys.exit(0)

    if args.get_branch:
        print(self.config["branch"])
        sys.exit(0)

    if args.no_color:
        self.tty = args.no_color

    if args.status:
        self.status = args.status
        exit_code = mirror_status.print_status(self)
        sys.exit(exit_code)

    # Validate arg combinations
    # If --set-branch, --protocols, --url, --prefix and not --api reject
    if args.set_branch or args.proto or args.url or args.prefix:
        if not args.api:
            print(f"Version {__version__}\nUSAGE:\n pacman-mirrors {args_summary}")
            print("{}".format(txt.API_ARGUMENTS_ERROR))
            sys.exit(1)

    # If --default and not --interactive reject
    if args.default:
        if not args.interactive:
            print(f"Version {__version__}\nUSAGE:\n pacman-mirrors {args_summary}")
            print(txt.INTERACTIVE_ARGUMENTS_ERROR)
            sys.exit(1)

    # If --interval and not --no-status reject
    if args.interval and not args.no_status:
        print(f"Version {__version__}\nUSAGE:\n pacman-mirrors {args_summary}")
        print("Invalid arguments: `--interval` argument only valid with `-s`")
        sys.exit(1)

    # Root required
    if os.getuid() != 0:
        print(f".: {txt.ERR_CLR} {txt.MUST_BE_ROOT}")
        sys.exit(1)

    if args.continent:
        self.continent = True

    if args.timezone:
        self.use_timezone = True

    if args.method:
        self.config["method"] = args.method

    if args.no_mirrorlist:
        self.no_mirrorList = True

    if args.quiet:
        self.quiet = True

    if args.timeout:
        self.max_wait_time = args.timeout
        self.config["timeout"] = args.timeout

    if args.no_status:
        self.no_status = True

    if args.interval:
        self.interval = args.interval
    else:
        self.interval = None

    # Generation methods
    if args.country:
        self.use_timezone = False
        if "," in args.country[0]:
            self.config["country_pool"] = args.country[0].split(",")
        else:
            self.config["country_pool"] = args.country

        if self.config["country_pool"] == ["all"]:
            customFn.delete_custom_pool(self)

    if args.fasttrack is not None:
        self.use_timezone = False
        if args.no_status:
            print(f"Version {__version__}\nUSAGE:\n pacman-mirrors {args_summary}")
            print(f"{txt.FASTTRACK_ARGUMENTS_ERROR}")
            sys.exit(1)

        self.fasttrack = args.fasttrack
        self.config["method"] = "rank"

    if args.interactive:
        self.interactive = True
        if args.default:
            self.default = True

        # wayland - sway - console - gtk
        if (
            os.environ.get("XDG_SESSION_TYPE") == "wayland"
            or os.environ.get("XDG_SESSION_TYPE") == "tty"
            or not os.environ.get("DISPLAY")
            or not gtk_available
        ):
            self.no_display = True

    if args.fc:
        self.no_display = True

    # API handling
    # Setup variables for passing to the api_config function
    if args.api:
        rebranch = False
        url = args.url
        setbranch = args.set_branch
        setprotocols = bool(args.proto)

        if args.re_branch:
            rebranch = True
        if args.proto:
            if "all" in args.proto:
                self.config["protocols"] = []
            else:
                if "," in args.proto:
                    self.config["protocols"] = args.proto.split(",")
                else:
                    self.config["protocols"] = args.proto

        api_handler.set_config(
            self,
            set_pfx=args.prefix,
            set_branch=setbranch,
            re_branch=rebranch,
            set_protocols=setprotocols,
            set_url=url,
        )
