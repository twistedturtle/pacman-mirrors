#!/usr/bin/env python

"""
test_pacman-mirrors
----------------------------------

Tests for `pacman-mirrors` module.
"""
import unittest
from unittest.mock import patch

from pacman_mirrors.builder import common, fasttrack
from pacman_mirrors.functions import fileFn, config_setup, cliFn, defaultFn
from pacman_mirrors.functions import httpFn
from pacman_mirrors.pacman_mirrors import PacmanMirrors
from . import mock_configuration as mock


test_conf = {
    "branch": "stable",
    "branches": mock.BRANCHES,
    "config_file": mock.CONFIG_FILE,
    "custom_file": mock.CUSTOM_FILE,
    "method": "rank",
    "work_dir": mock.WORK_DIR,
    "mirror_file": mock.MIRROR_FILE,
    "mirror_list": mock.MIRROR_LIST,
    "no_update": False,
    "country_pool": [],
    "protocols": [],
    "repo_arch": mock.REPO_ARCH,
    "status_file": mock.STATUS_FILE,
    "ssl_verify": True,
    "test_file": mock.TEST_FILE,
    "url_mirrors_json": mock.URL_MIRROR_JSON,
    "url_status_json": mock.URL_STATUS_JSON,
    "arm": False,
    "timeout": 2,
    "timezone": False,
    "continent": False,
    "selected_countries": [],
}


class TestPacmanMirrors(unittest.TestCase):
    """Pacman Mirrors Test suite"""

    def setUp(self):
        pass

    @patch("os.getuid")
    @patch.object(config_setup, "setup_config")
    def test_full_run_fasttrack(self, mock_build_config, mock_os_getuid):
        """TEST: pacman-mirrors -f5"""
        mock_os_getuid.return_value = 0
        mock_build_config.return_value = test_conf
        args = "-f5"
        cmd = mock.TEST_CMD + args
        with unittest.mock.patch("sys.argv", cmd.split()):
            app = PacmanMirrors()
            app.config = config_setup.setup_config(app)
            fileFn.create_dir(test_conf["work_dir"])
            cliFn.parse_command_line(app, True)
            httpFn.download_mirror_pool(app.config)
            defaultFn.load_default_mirror_pool(app)
            fasttrack.build_mirror_list(app, app.fasttrack)

    @patch("os.getuid")
    @patch.object(config_setup, "setup_config")
    def test_full_run_random(self, mock_build_config, mock_os_getuid):
        """TEST: pacman-mirrors -c all -m random"""
        mock_os_getuid.return_value = 0
        mock_build_config.return_value = test_conf
        args = "-c all -m random"
        cmd = mock.TEST_CMD + args
        with unittest.mock.patch("sys.argv", cmd.split()):
            app = PacmanMirrors()
            app.config = config_setup.setup_config(app)
            fileFn.create_dir(test_conf["work_dir"])
            cliFn.parse_command_line(app, True)
            httpFn.download_mirror_pool(app.config)
            defaultFn.load_default_mirror_pool(app)
            common.build_mirror_list(app)

    @patch("os.getuid")
    @patch.object(config_setup, "setup_config")
    def test_full_run_rank(self, mock_build_config, mock_os_getuid):
        """TEST: pacman-mirrors -c all"""
        mock_os_getuid.return_value = 0
        mock_build_config.return_value = test_conf
        args = "-c all"
        cmd = mock.TEST_CMD + args
        with unittest.mock.patch("sys.argv", cmd.split()):
            app = PacmanMirrors()
            app.config = config_setup.setup_config(app)
            fileFn.create_dir(test_conf["work_dir"])
            cliFn.parse_command_line(app, True)
            httpFn.download_mirror_pool(app.config)
            defaultFn.load_default_mirror_pool(app)
            common.build_mirror_list(app)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
