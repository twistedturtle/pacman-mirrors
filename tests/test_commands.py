#!/usr/bin/env python

import unittest
from subprocess import run, CalledProcessError

branches = ("stable", "testing", "unstable")


def _test_command_works_properly(args):
    cmd = "sudo poetry run pacman-mirrors "
    try:
        result = run(
            cmd + args,
            check=True,
            capture_output=True,
            text=True,
            shell=True
        )
        return (result.returncode, result.stdout)
    except CalledProcessError as error:
        return (1, error)

def raise_error(return_code, error):
    if return_code != 0:
        raise error

class TestDefaultConfig(unittest.TestCase):
    # TODO implement mirrorlist outputcheck using test-checkpoints.md guidelines

    def test_branch(self):
        args = "--api --get-branch"
        res = _test_command_works_properly(args)
        raise_error(res[0], res[1])

    def test_gioip(self):
        for i in branches:
            args = f"--geoip --api -B {i}"
            res = _test_command_works_properly(args)
            raise_error(res[0], res[1])

    def test_fasttrack(self):
        for i in branches:
            args = f"-f 5 --api -B {i}"
        res = _test_command_works_properly(args)
        raise_error(res[0], res[1])

    def test_default(self):
        for i in branches:
            args = f"-g --api -B {i}"
            res = _test_command_works_properly(args)
            raise_error(res[0], res[1])

    def test_country_stable(self):
        args = "-c Germany --api -B stable"
        res = _test_command_works_properly(args)
        raise_error(res[0], res[1])

    def test_country_testing(self):
        args = "-c France --api -B testing"
        res = _test_command_works_properly(args)
        raise_error(res[0], res[1])

    def test_country_unstable(self):
        args = "-c Italy --api -B unstable"
        res = _test_command_works_properly(args)
        raise_error(res[0], res[1])

    # we cannot automatize UI tests
    #def test_interactive_country(self):
    #    args = "-i -c Italy --api -B stable"
    #    _test_command_works_properly(args)

    def test_reset_mirrors(self):
        args = "-c all"
        res = _test_command_works_properly(args)
        raise_error(res[0], res[1])

    def test_invalid_arguments(self):
        args = "--invalid-args"
        res = _test_command_works_properly(args)
        if res[0] == 0:
            # test must fail
            raise res[1]

if __name__ == "__main__":
    unittest.main()
