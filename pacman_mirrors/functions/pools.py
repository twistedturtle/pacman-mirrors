#!/usr/bin/env python
#
# This file is part of pacman-mirrors.
#
# pacman-mirrors is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published b
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

"""Pacman-Mirrors Country Functions"""
import os
from pacman_mirrors.functions.validFn import country_list_is_valid
from pacman_mirrors.functions.util import get_zone_countries

countries = get_zone_countries()


def wash_country_list(country_list: list):
    """
    Cleans and standardizes a list of country identifiers.

    This function processes a list of country identifiers, such as country names
    or codes, and standardizes them by matching against known country data. If a
    match is found, the standardized country name is included in the output list.
    Duplicates in the input list are removed in the output.

    Args:
        country_list: A list of strings, where each string represents a
            country identifier (e.g., name or code) to be cleaned and standardized.

    Returns:
        list: A list of unique, standardized country names.
    """
    washed = []
    for p in country_list:
        c = p.lower()
        r = p
        search = (
            r for r in countries if r["code"].lower() == c or r["name"].lower() == c
        )
        for s in search:
            if s is not None:
                r = s["name"]
        if r not in washed:
            washed.append(r)
    return washed


def build_country_list(self) -> list:
    """
    Do a check on the user's country selection
    :param self:
    :return: list a of valid countries
    :rtype: list
    """
    # Dear Fellow Manjaro Maintainer:
    # When I wrote this code, only I knew how it worked.
    # Now, no one knows!
    #
    # If you are trying to optimize
    # this function it fails (most surely),
    # please increase this counter as a warning for the next maintainer.
    #
    # total_hours_wasted_here = 1
    result = []
    if self.selected_countries:
        if self.selected_countries == ["all"]:
            result = self.mirrors.country_pool
        else:
            self.selected_countries = wash_country_list(self.selected_countries)
            if country_list_is_valid(
                onlycountry=self.selected_countries,
                countrylist=self.mirrors.country_pool,
                tty=self.tty,
            ):
                result = self.selected_countries
    # this executes when geoip or continent is True
    if not result:
        # get country
        if self.tz:
            country = get_timezone_country()
            if country:
                result.append(country)

        # get a country list for the continent
        if self.continent:
            continent_mirror_countries = get_continent_countries(
                get_timezone_continent(), self.mirrors.mirror_pool
            )
            if continent_mirror_countries:
                result = continent_mirror_countries

        # validate the result
        # but do not return an empty list
        if not result:
            result = self.mirrors.country_pool
    return result


def get_continent(country: str) -> str:
    """
    Database query for the continent where a country belongs
    :param country:
    """
    continent = (x for x in countries if country in x["name"])
    for x in continent:
        return x["continent"].strip().replace(" ", "_")
    return ""


def get_continent_countries(continent: str, mirror_pool: list) -> list:
    """
    Database query for countries on continent
    :param continent:
    :param mirror_pool:
    :return: list
    """
    result = []
    mirror_countries = [c for c in mirror_pool if continent in c["continent"]]
    for m in mirror_countries:
        if m["country"] not in result:
            result.append(m["country"])
    return result


def get_mirror_country_from_zone(zone: str) -> str:
    """
    Retrieves the corresponding mirror country for a given timezone.

    This function determines the country that corresponds to a specific timezone
    (zone) by examining a list of country data and their associated timezones.
    It uses data from a configuration file to map the timezone to a mirror
    country, if a match is found.

    Parameters:
    zone : str
        The timezone for which the corresponding mirror country is to be found.

    Returns:
    str
        The name of the mirror country corresponding to the specified timezone.
        Returns an empty string if no matching country is found.
    """
    import json
    from pacman_mirrors.functions.jsonFn import read_file_content
    from pacman_mirrors.config import configuration as config
    mirror_countries = json.loads(read_file_content(config.MIRROR_FILE, binary=False))
    country_zones = [x for x in countries if zone in x["timezones"]]
    if not country_zones:
        return ""
    filtered_countries = [x for x in mirror_countries if country_zones[0]["name"] in x["country"]]
    return filtered_countries[0]["country"] if filtered_countries else ""


def get_timezone_country() -> str:
    """
    Gets the name of the country corresponding to the system's current timezone.

    The function retrieves the system's timezone based on the symbolic link `/etc/localtime`.
    It then matches this timezone with a list of countries and their associated timezones,
    returning the name of the country whose timezones include the system's timezone.

    Returns:
        str: The name of the country corresponding to the system's timezone, or an
        empty string if no matching country is found.
    """
    localtime = os.readlink("/etc/localtime").split("/")
    timezone = "{}/{}".format(localtime[-2], localtime[-1])
    filtered_zones = [x for x in countries if timezone in x["timezones"]]
    return filtered_zones[0]["name"] if filtered_zones else ""


def get_timezone_continent() -> str:
    """
    Determines the continent of the current timezone.

    This function identifies the continent based on the current
    timezone's country. It performs this by comparing the current
    country against a list of countries and their corresponding
    continents.

    Returns:
        str: The continent of the current timezone, formatted with
        underscores replacing spaces. Returns an empty string if
        the continent cannot be determined.
    """
    country = get_timezone_country()
    continent = (x for x in countries if country in x["name"])
    for x in continent:
        return x["continent"].strip().replace(" ", "_")
    return ""
