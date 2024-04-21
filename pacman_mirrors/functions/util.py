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

"""Pacman-Mirrors Utility Functions"""

import platform
import shutil
import subprocess
import os
import configparser
from pacman_mirrors.api import apifn
from pacman_mirrors.constants import txt


def extract_mirror_url(data: str) -> str:
    """Extract mirror url from data"""
    line = data.strip()
    if line.startswith("Server"):
        return line[9:].replace("$branch/$repo/$arch", "")


def get_country(data: str) -> str:
    """Extract mirror country from data"""
    line = data.strip()
    if line.startswith("[") and line.endswith("]"):
        return line[1:-1]

    elif line.startswith("## Country") or line.startswith("## Location"):
        return line[19:]


def get_protocol(url: str) -> str:
    """Extract protocol from url"""
    pos = url.find(":")
    return url[:pos]


def get_protocol_from_url(url: str) -> str:
    """
    Splits an url
    :param url:
    :returns protocol eg. http
    """
    colon = url.find(":")
    if colon:
        return url[:colon]

    return url


def location_from_url(url: str) -> str:
    """
    Splits an url
    :param url:
    :returns url string without protocol
    """
    colon = url.find(":")
    if colon:
        return url[colon:]

    return url


def aarch64_check(self, write: bool = False) -> None:
    if platform.machine() == "aarch64":
        self.config["arm"] = True
        branch = self.config["branch"]
        if "arm" not in branch:
            branch = f"arm-{branch}"
            if write:
                apifn.write_config_branch(
                    branch, self.config["config_file"], quiet=True
                )


def internet_message(tty: bool = False) -> None:
    """Message when internet connection is down"""
    msg(f"{txt.INTERNET_DOWN}", urgency=txt.INF_CLR, tty=tty)
    msg(f"{txt.MIRROR_RANKING_NA}", urgency=txt.INF_CLR, tty=tty)
    msg(f"{txt.INTERNET_ALTERNATIVE}", urgency=txt.INF_CLR, tty=tty)


def msg(
    message: str,
    urgency: str = "",
    tty: bool = False,
    color: str = "",
    newline: bool = False,
) -> None:
    """Helper for printing messages
    :param message:
    :param urgency:
    :param tty:
    :param color:
    :param newline:
    """
    reset = "\033[1;m"
    if urgency and color:
        color = ""
    if tty:
        if newline:
            print("\n")

        print(f"::{message}")

    else:
        if urgency:
            if newline:
                print("\n")

            print(f"::{urgency} {message}")

        else:
            if newline:
                print("\n")

            print(f"::{color}{message}{reset}")


def strip_protocol(url: str) -> str:
    return url.split("//")[1]


def terminal_size() -> tuple:
    """get terminal size"""
    # http://www.programcreek.com/python/example/85471/shutil.get_terminal_size
    cols = shutil.get_terminal_size().columns
    lines = shutil.get_terminal_size().lines
    result = (cols, lines)
    return result


def build_static_from_config(static: str) -> list:
    urls = static.split(",")
    result = []
    for url in urls:
        if not str(url).endswith("/"):
            url = f"{url}/"
        temp = {
            "branches": [1, 1, 1],
            "country": "StaticConfig",
            "protocols": [str(url).split(":")[0]],
            "last_sync": "00:05",
            "resp_time": 0.555,
            "url": url
        }
        result.append(temp)
    return result


def user_agent(config: dict) -> str:
    sys_info = system_info(config)
    return f"{sys_info['arch']}/{sys_info['session']}/"\
           f"{sys_info['os']}/{sys_info['branch']}/{sys_info['desktop']}/"\
           f"{sys_info['kernel']}/{sys_info['chassis']}-{sys_info['vendor']}"


def system_info(config: dict) -> dict:
    def proc(cmd):
        return subprocess.check_output(cmd).decode()

    info = proc(["hostnamectl"]).split()

    def chassis():
        for index, line in enumerate(info):
            if "Chassis" in line:
                return info[index + 1]

    def vendor():
        for index, line in enumerate(info):
            if "Vendor" in line:
                return info[index + 1]

    branch = config["branch"]
    kernel = proc(["uname", "-r"])
    arch = proc(["uname", "-m"])
    codename = proc(["lsb_release", "-c"]).replace("Codename:\t", "").replace("\n", "")
    version = proc(["lsb_release", "-r"]).replace("Release:\t", "").replace("\n", "")
    session_type = os.getenv("XDG_SESSION_TYPE")
    de = os.getenv("XDG_CURRENT_DESKTOP")
    _os_ = f"{codename}-{version}"

    if session_type is None:
        session_type = "tty"

    return {
        "arch": arch.strip("\n"),
        "session": session_type.strip("\n"),
        "os": _os_,
        "branch": branch,
        "desktop": de.strip("\n"),
        "kernel": kernel.strip("\n"),
        "vendor": vendor(),
        "chassis": chassis()
    }
