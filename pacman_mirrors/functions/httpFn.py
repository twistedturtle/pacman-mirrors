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


def headers():
    return {"User-Agent": f"{conf.USER_AGENT}/{__version__}"}


def check_timestamp(url: str) -> bool:
    """Use a head request to get the last modified time of the mirror pool"""
    resp = requests.head(url, headers=headers())
    resp.raise_for_status()
    remote_file_stamp = resp.headers.get("Last-Modified")
    local_file_stamp = os.path.getmtime(conf.MIRROR_FILE)
    return (
        remote_file_stamp is not None
        and local_file_stamp is not None
        and remote_file_stamp == local_file_stamp
    )


def download_mirrors(config: dict) -> tuple:
    """Retrieve mirrors from manjaro.org
    :param config:
    :returns: tuple with bool for mirrors.json and status.json
    :rtype: tuple
    """
    # assume all went well
    got_mirrors = True
    got_status = True
    message = ""

    # -----------------------------------------------------------
    # try to fetch mirrors.json
    try:
        util.msg(
            message=f"=> Mirror pool: {config['url_mirrors_json']}", urgency=txt.INF_CLR
        )
        # mirrors.json
        if not check_timestamp(config["url_mirrors_json"]):
            resp = requests.get(
                url=config["url_mirrors_json"],
                headers=headers(),
                timeout=config["timeout"],
            )

            resp.raise_for_status()
            mirrors_json = resp.json()
            temp_file = config["work_dir"] + "/.temp.file"
            jsonFn.json_dump_file(mirrors_json, temp_file)
            filecmp.clear_cache()
            # check if the file was downloaded and parsed correct
            if fileFn.check_file(conf.WORK_DIR, folder=True):
                if not fileFn.check_file(config["mirror_file"]):
                    jsonFn.json_dump_file(mirrors_json, config["mirror_file"])
                elif not filecmp.cmp(temp_file, config["mirror_file"]):
                    jsonFn.json_dump_file(mirrors_json, config["mirror_file"])

            os.remove(temp_file)

    except (json.JSONDecodeError,) as err:
        message = f"Invalid JSON data: {err}"
    except (requests.exceptions.ConnectionError,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.Timeout,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.HTTPError,) as err:
        message = f"Connection {err}"

    if message != "":
        # mirrors.json failed
        got_mirrors = False
        util.msg(message=message, urgency=txt.ERR_CLR, newline=True)
        message = ""

    # -----------------------------------------------------------
    # try to fetch status.json
    try:
        util.msg(
            message=f"=> Mirror status: {config['url_status_json']}",
            urgency=txt.INF_CLR,
        )
        resp = requests.get(
            url=config["url_status_json"],
            headers=headers(),
            timeout=config["timeout"],
        )

        status_json = resp.json()
        jsonFn.write_json_file(status_json, config["status_file"])

    except (json.JSONDecodeError,) as err:
        message = f"Invalid JSON data: {err}"
    except (requests.exceptions.ConnectionError,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.Timeout,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.HTTPError,) as err:
        message = f"Connection {err}"

    if message != "":
        # status.json failed
        got_status = False
        util.msg(message=message, urgency=txt.ERR_CLR, newline=True)

    return got_mirrors, got_status


def get_ip_country(timeout: int = 2) -> str:
    """
    Get the user country from connection IP (might be VPN who knows)
    :return: country name
    """
    try:
        url = "https://get.geojs.io/v1/ip/country/full"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()

    except requests.exceptions.ConnectionError:
        return ""

    return resp.text


def get_http_response(url: str, timeout: int) -> str:
    """
    Used for http mirrors
    :return: bool
    """
    message = ""
    try:
        resp = requests.get(url=url, headers=headers(), timeout=timeout)
        resp.raise_for_status()
        # _ = resp.text
    except (requests.exceptions.ConnectionError,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.Timeout,) as err:
        message = f"Connection: {err}"
    except (requests.exceptions.HTTPError,) as err:
        message = f"Connection {err}"
    return message


def get_ftp_response(url: str, timeout: int) -> str:
    """
    Used for ftp response
    :return:
    """
    message = ""
    try:
        with closing(request.urlopen(url, timeout=timeout)) as ftpReq:
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
    timeout: int = 2,
    count: int = 1,
    quiet: bool = False,
    ssl_verify: bool = True,
) -> float:
    """Query mirror by downloading a file and measuring the time taken
    :param config:
    :param ssl_verify:
    :param tty:
    :param url:
    :param timeout:
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
        message = get_http_response(url=probe_url, timeout=timeout)
        probe_stop = time.time()

    if probe_url.startswith("ftp"):
        message = get_ftp_response(url=probe_url, timeout=timeout)
        probe_stop = time.time()

    if message and not quiet:
        util.msg(message=f"{message}", urgency=txt.ERR_CLR, tty=tty, newline=True)

    if probe_stop and not message:
        response_time = round((probe_stop - probe_start), 3)

    return response_time


def check_internet_connection(tty: bool = False, timeout: int = 2) -> bool:
    """Check for internet connection
    @param timeout:
    @param tty:
    """

    error_msg = ""
    for host in conf.INET_CONN_CHECK_URLS:
        try:
            requests.get(host, headers=headers(), timeout=timeout)
            return True
        except (requests.exceptions.HTTPError, requests.exceptions.SSLError) as err:
            # this indicates an active internet connection
            # otherwise http errors would not be possible
            # the host didn't respond well to https request
            return True
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as err:
            # this indicates that internet connection is not available
            # until the configuration of
            # the ping server is corrected
            # we could neglect the error
            # don't return False as it will cause a premature exit
            # return False
            # collect error message(s)
            error_msg = error_msg + "\n" + f"Connection: '{host}' => '{err}'"
        except Exception as err:
            # don't return False as it will cause a premature exit
            # return False
            # collect error message(s)
            error_msg = error_msg + "\n" + f"Connection: '{host}' => '{err}'"

    if error_msg:
        util.msg(error_msg, urgency=txt.WRN_CLR, tty=tty)

    # the only valid result at this point is False
    return False


def ping_host(host: str, tty: bool = False, count: int = 1) -> bool:
    """Check a host's availability
    :param host:
    :param count:
    :param tty:
    :rtype: boolean
    """
    util.msg(f"ping {host} x {count}", urgency=txt.INF_CLR, tty=tty)
    return subprocess.Popen(f"ping -c{count} {host} > /dev/null", shell=True) == 0


def download_mirror_pool(config: dict, tty: bool = False, quiet: bool = False) -> tuple:
    """Download updates from repo.manjaro.org
    :param config:
    :param quiet:
    :param tty:
    :returns: tuple with True/False for mirrors.json and status.json
    :rtype: tuple
    """
    if not quiet:
        util.msg(
            message=f"{txt.DOWNLOADING_MIRROR_FILE} Manjaro",
            urgency=txt.INF_CLR,
            tty=tty,
        )

    result = download_mirrors(config)

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
