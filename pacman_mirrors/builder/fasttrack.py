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

"""Pacman-Mirrors Interactive Fasttrack Mirror List Builder Module"""

from random import shuffle

from pacman_mirrors.builder.builder import build_pool
from pacman_mirrors.constants import txt
from pacman_mirrors.functions import util
from pacman_mirrors.functions.outputFn import write_pacman_mirror_list
from pacman_mirrors.functions.sortMirrorFn import sort_mirror_pool
from pacman_mirrors.functions.testMirrorFn import test_mirror_pool


def build_mirror_list(self, limit: int) -> None:
    """
    Build and update the mirror list by probing and sorting available mirrors.

    Attributes
    ----------
    None

    Parameters
    ----------
    limit : int
        The maximum number of mirrors to be processed. If the value is less than or equal
        to 0, or exceeds the total number of available mirrors, the entire list is used.

    Raises
    ------
    IndexError
        Raised if work_pool is empty during mirror processing, which could occur if no
        mirrors pass the test stage.
    """
    work_pool = build_pool(self)
    shuffle(work_pool)
    # probe the mirrors
    if limit <= 0 or limit > len(work_pool):
        limit = len(work_pool)

    work_pool = test_mirror_pool(self=self, worklist=work_pool, limit=limit)
    # Write mirrorlist
    try:
        _ = work_pool[0]
        work_pool = sort_mirror_pool(
            worklist=work_pool, field="resp_time", reverse=False
        )

        write_pacman_mirror_list(self=self, selected_servers=work_pool)
    except IndexError:
        util.msg(message=f"{txt.NO_SELECTION}", urgency=txt.WRN_CLR, tty=self.tty)
        util.msg(message=f"{txt.NO_CHANGE}", urgency=txt.INF_CLR, tty=self.tty)
