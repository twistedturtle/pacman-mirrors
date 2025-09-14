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
from pacman_mirrors.api import apifn
from pacman_mirrors.constants import txt
from pacman_mirrors.functions import httpFn


def get_zone_countries() -> list:
    """
    Retrieves a list of countries with their associated timezones and related details.

    This function processes and collects country information including timezones,
    continent, region, country name, and country code. Valid timezones are
    filtered for each country, and the information is organized into a dictionary
    format. The result is a list containing these dictionaries for all available
    countries.

    Returns:
        list: A list of dictionaries where each dictionary contains the following:
            - timezones (list): A list of timezone strings associated with a country.
            - continent (str): The continent derived from the first timezone of the country.
            - region (str): The region derived from the first timezone of the country.
            - name (str): The human-readable name of the country.
            - code (str): The ISO 3166-1 alpha-2 country code.

    """
    from zoneinfo import ZoneInfo
    from pytz import country_names, country_timezones

    countries = []
    for country_code in country_timezones:
        # Filter timezones for allowed regions
        filtered_zones = [zone for zone in country_timezones[country_code]]

        if filtered_zones:  # Only process if there are valid timezones
            pm_timezone = {
                "timezones": filtered_zones,
                "continent": ZoneInfo(filtered_zones[0]).key.split("/")[0],
                "region": ZoneInfo(filtered_zones[0]).key.split("/")[0],
                "name": country_names[country_code],
                "code": country_code,
            }
            countries.append(pm_timezone)
    return countries


def extract_mirror_url(data: str) -> str:
    """Extract mirror url from data"""
    line = data.strip()
    if line.startswith("Server"):
        return line[9:].replace("$branch/$repo/$arch", "")
    return ""


def get_country(data: str) -> str:
    """Extract mirror country from data"""
    line = data.strip()
    if line.startswith("[") and line.endswith("]"):
        return line[1:-1]

    elif line.startswith("## Country") or line.startswith("## Location"):
        return line[19:]
    return ""


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
        # get branch from config object
        branch = self.config["branch"]
        # branch should start with 'arm-'
        if not branch.startswith("arm-"):
            # change the internal configuration
            # branch to arm-{stable,testing,unstable}
            self.config["branch"] = f"arm-{branch}"
            if write:
                # write the branch to config storage
                apifn.write_config_branch(
                    self.config["branch"], self.config["config_file"], quiet=True
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


def build_static_from_config(self, static: str) -> list:
    urls = static.split(",")
    result = []
    for url in urls:
        if not str(url).endswith("/"):
            url = f"{url}/"
        temp = {
            "branches": [1, 1, 1],
            "country": "Static",
            "protocols": [str(url).split(":")[0]],
            "last_sync": "00:05",
            "resp_time": httpFn.get_mirror_response(url, self.config, self.tty),
            "url": url,
        }
        result.append(temp)
    return result
