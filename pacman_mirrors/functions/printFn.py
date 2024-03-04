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

"""Pacman-Mirrors Print Functions"""

from pacman_mirrors.constants import colors as color


def blue_msg(message: str) -> None:
    print(f"{color.BLUE}{message}{color.RESET}")


def green_msg(message: str) -> None:
    print(f"{color.GREEN}{message}{color.RESET}")


def red_msg(message: str) -> None:
    print(f"{color.RED}{message}{color.RESET}")


def yellow_msg(message: str) -> None:
    print(f"{color.YELLOW}{message}{color.RESET}")
