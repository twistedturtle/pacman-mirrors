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

"""Manjaro-Mirrors HTTP Functions"""

import filecmp
import json
import os
import ssl
import time
import shutil
from urllib import request
from urllib.error import URLError
from contextlib import closing
import subprocess
import requests
from pacman_mirrors import __version__
from pacman_mirrors.config import configuration as conf
from pacman_mirrors.constants import txt
from pacman_mirrors.functions import fileFn
from pacman_mirrors.functions import jsonFn
from pacman_mirrors.functions import util


def headers(agent: str = None):
    if agent is not None:
        return {"User-Agent": f"{conf.USER_AGENT}/{__version__}/{agent}"}
    return {"User-Agent": f"{conf.USER_AGENT}/{__version__}"}


def download_mirrors(config: dict) -> tuple:
    """Retrieve mirrors from manjaro.org
    :param config:
    :returns: tuple with bool for mirrors.json and status.json
    :rtype: tuple
    """
    fetchmirrors = True
    fetchstatus = True
    message = ""
    try:
        agent = util.user_agent()
        # mirrors.json
        util.msg(
            message=f"=> Mirror pool: {config['url_mirrors_json']}", urgency=txt.INF_CLR
        )
        resp = requests.get(
            url=config["url_mirrors_json"], headers=headers(agent), timeout=config["timeout"]
        )

        resp.raise_for_status()
        mirrorlist = resp.json()
        tempfile = config["work_dir"] + "/.temp.file"
        jsonFn.json_dump_file(mirrorlist, tempfile)
        filecmp.clear_cache()

        if fileFn.check_file(conf.USR_DIR, folder=True):
            if not fileFn.check_file(config["mirror_file"]):
                jsonFn.json_dump_file(mirrorlist, config["mirror_file"])
            elif not filecmp.cmp(tempfile, config["mirror_file"]):
                jsonFn.json_dump_file(mirrorlist, config["mirror_file"])

        os.remove(tempfile)

    except (json.JSONDecodeError,) as err:
        message = f"Invalid JSON data: {err}"
    except (requests.exceptions.ConnectionError,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.Timeout,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.HTTPError,) as err:
        message = f"Connection {err}"

    if message != "":
        fetchmirrors = False
        util.msg(message=message, urgency=txt.ERR_CLR, newline=True)
        message = ""

    try:
        util.msg(
            message=f"=> Mirror status: {config['url_status_json']}",
            urgency=txt.INF_CLR,
        )
        resp = requests.get(
            url=config["url_status_json"], headers=headers(None), timeout=config["timeout"]
        )

        statuslist = resp.json()
        jsonFn.write_json_file(statuslist, config["status_file"])

    except (json.JSONDecodeError,) as err:
        message = f"Invalid JSON data: {err}"
    except (requests.exceptions.ConnectionError,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.Timeout,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.HTTPError,) as err:
        message = f"Connection {err}"

    if message != "":
        fetchstatus = False
        util.msg(message=message, urgency=txt.ERR_CLR, newline=True)

    return fetchmirrors, fetchstatus


def get_ip_country(maxwait: int = 2) -> str:
    """
    Get the user country from connection IP (might be VPN who knows)
    :return: country name
    """
    try:
        url = "https://get.geojs.io/v1/ip/country/full"
        resp = requests.get(url, timeout=maxwait)
        resp.raise_for_status()

    except requests.exceptions.ConnectionError:
        return ""

    return resp.text


def get_http_response(url: str, maxwait: int) -> str:
    """
    Used for http mirrors
    :return: bool
    """
    message = ""
    try:
        resp = requests.get(url=url, headers=headers(None), timeout=maxwait)
        resp.raise_for_status()
        # _ = resp.text
    except (requests.exceptions.ConnectionError,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.Timeout,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.HTTPError,) as err:
        message = f"Connection {err}"

    return message


def get_ftp_response(url: str, maxwait: int) -> str:
    """
    Used for ftp response
    :return:
    """
    message = ""
    try:
        with closing(request.urlopen(url, timeout=maxwait)) as ftpReq:
            with open(conf.WORK_DIR + "/.testresponse", "wb") as testFile:
                shutil.copyfileobj(ftpReq, testFile)

            os.remove(conf.WORK_DIR + "/.testresponse")

    except URLError as e:
        if e.reason.find("No such file or directory") >= 0:
            message = "FileNotFound"
        else:
            message = f"{e.reason}"

    return message


def get_mirror_response(
    url: str,
    config: dict,
    tty: bool = False,
    maxwait: int = 2,
    count: int = 1,
    quiet: bool = False,
    ssl_verify: bool = True,
) -> float:
    """Query mirror by downloading a file and measuring the time taken
    :param config:
    :param ssl_verify:
    :param tty:
    :param url:
    :param maxwait:
    :param count:
    :param quiet:
    :returns: always return a float value with response time
    """
    response_time = txt.SERVER_RES  # prepare default return value
    probe_stop = None
    message = ""
    context = ssl.create_default_context()
    arch = "x86_64"

    if config["arm"]:
        arch = "aarch64"

    probe_url = f"{url}{config['branch']}/core/{arch}/{config['test_file']}"

    if not ssl_verify:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    probe_start = time.time()
    if probe_url.startswith("http"):
        message = get_http_response(url=probe_url, maxwait=maxwait)
        probe_stop = time.time()

    if probe_url.startswith("ftp"):
        message = get_ftp_response(url=probe_url, maxwait=maxwait)
        probe_stop = time.time()

    if message and not quiet:
        util.msg(message=f"{message}", urgency=txt.ERR_CLR, tty=tty, newline=True)

    if probe_stop and not message:
        response_time = round((probe_stop - probe_start), 3)

    return response_time


def check_internet_connection(agent: str = None, tty: bool = False, maxwait: int = 2) -> bool:
    """Check for internet connection
    @param maxwait:
    @param tty:
    @param agent:
    """

    def output_err(hostname, error):
        print("")
        util.msg(f"{hostname} '{error}'", urgency=txt.WRN_CLR, tty=tty)
        print("")

    for host in conf.INET_CONN_CHECK_URLS:
        try:
            requests.get(host, headers=headers(agent), timeout=maxwait)
            return True
        except requests.exceptions.ConnectionError as err:
            output_err(host, err)
        except requests.exceptions.Timeout as err:
            output_err(host, err)
        except requests.exceptions.HTTPError as err:
            output_err(host, err)

    return False


def ping_host(host: str, tty: bool = False, count: int = 1) -> bool:
    """Check a hosts availability
    :param host:
    :param count:
    :param tty:
    :rtype: boolean
    """
    util.msg(f"ping {host} x {count}", urgency=txt.INF_CLR, tty=tty)
    return subprocess.Popen(f"ping -c{count} {host} > /dev/null", shell=True) == 0


def download_mirror_pool(
    config: dict, tty: bool = False, quiet: bool = False
) -> tuple:
    """Download updates from repo.manjaro.org
    :param config:
    :param quiet:
    :param tty:
    :returns: tuple with True/False for mirrors.json and status.json
    :rtype: tuple
    """
    result = None
    connected = check_internet_connection(None, tty=tty)
    if connected:
        if not quiet:
            util.msg(
                message=f"{txt.DOWNLOADING_MIRROR_FILE} Manjaro",
                urgency=txt.INF_CLR,
                tty=tty,
            )

        result = download_mirrors(config)
    else:
        if not fileFn.check_file(config["status_file"]):
            if not quiet:
                util.msg(
                    message=f"{txt.MIRROR_FILE} {config['status_file']} {txt.IS_MISSING}",
                    urgency=txt.WRN_CLR,
                    tty=tty,
                )

                util.msg(
                    message=f"{txt.FALLING_BACK} {conf.MIRROR_FILE}",
                    urgency=txt.WRN_CLR,
                    tty=tty,
                )

            result = (True, False)

        if not fileFn.check_file(config["mirror_file"]):
            if not quiet:
                util.msg(message=f"{txt.HOUSTON}", urgency=txt.HOUSTON, tty=tty)

            result = (False, False)

    return result


def send_statistics(agent: str) -> None:
    url = f"{conf.STATISTIC_HOSTNAME}/{agent}"
    requests.get(url, headers=headers(agent))
