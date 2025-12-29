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

from pacman_mirrors.functions.filter_mirror_pool_functions import (
    filter_mirror_protocols,
    filter_mirror_country,
    filter_user_branch,
)

from pacman_mirrors.functions.filter_mirror_status_functions import (
    filter_bad_mirrors,
    filter_error_mirrors,
    filter_poor_mirrors,
)


def build_pool(self) -> list:
    """
    Builds and returns a filtered list of mirrors based on several criteria.

    The method processes a list of mirrors by applying various filters such as
    removing bad and error-prone mirrors, filtering based on country, protocol,
    and user configuration. It optionally considers factors like synchronization
    interval and user branches in the filtering process.

    Returns:
        list: A list of mirrors that match the applied filters.

    Raises:
        IndexError: Raised when protocol configuration is accessed without any
        available protocols.
    """

    # remove known bad mirrors - last sync 9999:99
    work_pool = filter_bad_mirrors(mirror_pool=self.mirrors.mirror_pool)

    # remove known error mirrors - response time 99.99
    work_pool = filter_error_mirrors(mirror_pool=work_pool)

    # Apply country filter if not fasttrack
    if not self.fasttrack:
        work_pool = filter_mirror_country(
            mirror_pool=work_pool, country_pool=self.config["selected_countries"]
        )

    # Apply protocol filter
    try:
        _ = self.config["protocols"][0]
        work_pool = filter_mirror_protocols(
            mirror_pool=work_pool, protocols=self.config["protocols"]
        )

    except IndexError:
        pass

    # Apply --no-status argument if applicable
    if self.no_status:
        # Apply interval filter
        if self.interval:
            work_pool = filter_poor_mirrors(
                mirror_pool=work_pool, interval=self.interval
            )
    else:
        work_pool = filter_user_branch(mirror_pool=work_pool, config=self.config)

    return work_pool
