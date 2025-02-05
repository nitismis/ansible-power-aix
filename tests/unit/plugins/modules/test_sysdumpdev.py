# -*- coding: utf-8 -*-
# Copyright: (c) 2020- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import unittest
from unittest import mock
import copy

from ansible_collections.ibm.power_aix.plugins.modules import sysdumpdev

from .common.utils import (
    AnsibleExitJson, AnsibleFailJson, exit_json, fail_json,
    rootdir, sysdumpdev_output_path1
)

params = {
    'primary': '/dev/lg_dumplv',
    'secondary': '/dev/sysdumpnull',
    'copy_directory': '/var/adm/ras',
    'permanent': False,
    'forced_copy_flag': True,
    'always_allow_dump': False,
    'dump_compression': True,
    'dump_type': 'fw-assisted',
    'dump_mode': 'disallow',
    'nx_gzip': True}

expected_result = {
    'changed': True,
    'cmd': '',
    'rc': '',
    'stdout': '',
    'stderr': ''}

class TestSysdumpdev(unittest.TestCase):
    def setUp(self):
        self.module = mock.Mock()
        self.module.fail_json = fail_json
        rc, stdout, stderr = 0, "sample stdout", "sample stderr"
        self.module.run_command.return_value = (rc, stdout, stderr)
        # load sample output
        with open(sysdumpdev_output_path1, "r") as f:
            self.sysdumpdev_output1 = f.read().strip()

    def test_sysdumpdev_fact(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        expected_config = {
            'primary': '/dev/lg_dumplv',
            'secondary': '/dev/sysdumpnull',
            'copy_directory': '/var/adm/ras',
            'forced_copy_flag': True,
            'always_allow_dump': False,
            'dump_compression': True,
            'dump_type': 'fw-assisted',
            'dump_mode': 'disallow',
            'nx_gzip': True}
        current_config = sysdumpdev.get_dump_config(self.module)
        self.assertDictEqual(expected_config, current_config)

    def test_set_dump_devices(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['primary'] = "/dev/sysdump0"
        params['secondary'] = "/dev/sysdump1"
        params['permanent'] = False
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -p /dev/sysdump0 -s /dev/sysdump1'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_dump_devices_permanent(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['primary'] = "/dev/sysdump0"
        params['secondary'] = "/dev/sysdump1"
        params['permanent'] = True
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -p /dev/sysdump0 -s /dev/sysdump1 -P'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_copy_directory_forced_copy_true(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['copy_directory'] = "/var/adm/dump"
        params['forced_copy_flag'] = True
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -D /var/adm/dump'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_copy_directory_forced_copy_false(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['copy_directory'] = "/var/adm/dump"
        params['forced_copy_flag'] = False
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -d /var/adm/dump'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_always_allow_dump_true(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['always_allow_dump'] = True
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -K'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_dump_type_traditional(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['dump_type'] = 'traditional'
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -t traditional'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_dump_mode_allow(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['dump_mode'] = 'allow'
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -f allow'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)

    def test_set_nx_gzip_false(self):
        self.module.run_command.side_effect = [
            (0, self.sysdumpdev_output1, "sample stderr")
        ]
        params['nx_gzip'] = False
        self.module.params = params

        expected_result['cmd'] = 'sysdumpdev -n'

        current_config = sysdumpdev.get_dump_config(self.module)
        result = sysdumpdev.update_dump_config(self.module, current_config)
        self.assertDictEqual(expected_result, result)
