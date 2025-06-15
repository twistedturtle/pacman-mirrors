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

# http constants
TEST_FILE = "core.db.tar.gz"
USER_AGENT = "PacmanMirrors"
URL_MIRROR_JSON = "https://repo.manjaro.org/mirrors.json"
URL_STATUS_JSON = "https://repo.manjaro.org/status.json"
INET_CONN_CHECK_URLS = [
    "https://ping.manjaro.org/pacmanmirrors",
    "https://wikipedia.org",
    "https://archlinux.org",
]
# there is no certificate on the ping url
# we have been using https for everything
# need to set up a certificate for the ping domain
# STATISTIC_HOSTNAME = "http://ping.manjaro.org/pacmanmirrors"
CONFIG_FILE = "/etc/pacman-mirrors.conf"
MIRROR_LIST = "/etc/pacman.d/mirrorlist"
# /var/lib
# WORK_DIR = "/var/lib/pacman-mirrors"
WORK_DIR = "/var/lib/pacman-mirrors"
CUSTOM_FILE = f"{WORK_DIR}/custom-mirrors.json"
MIRROR_FILE = f"{WORK_DIR}/mirrors.json"
STATUS_FILE = f"{WORK_DIR}/status.json"
# repo constants
BRANCHES = ("stable", "testing", "unstable")
ARM_BRANCHES = ("arm-stable", "arm-testing", "arm-unstable")
PROTOCOLS = ("https", "http", "ftp")
METHODS = ("rank", "random")
SSL = ("True", "False")
REPO_ARCH = "/$repo/$arch"
