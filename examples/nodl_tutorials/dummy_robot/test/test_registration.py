# SPDX-FileCopyrightText: 2026 Open Source Robotics Foundation, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Verify the installed contracts used by the tutorial."""

from pathlib import Path

import pytest
from ament_index_python.packages import get_package_share_directory
from ament_index_python.resources import get_resource

from nodl_schema import load_nodl

PACKAGE = 'nodl_tutorial_dummy_robot'
DOCUMENT = 'dummy_laser'


def _installed_contract(relative_path):
    share = Path(get_package_share_directory(PACKAGE))
    return load_nodl(share / 'nodl' / relative_path)


def test_registered_document_matches_installed_source():
    content, prefix = get_resource('nodl', f'{PACKAGE}__{DOCUMENT}')

    assert prefix
    installed = Path(get_package_share_directory(PACKAGE)) / 'nodl' / f'{DOCUMENT}.nodl.yaml'
    assert installed.read_text() == content


@pytest.mark.parametrize(
    ('filename', 'name', 'type_name', 'reliability'),
    [
        ('topic.nodl.yaml', 'scan_regressed', 'sensor_msgs/msg/LaserScan', 'RELIABLE'),
        ('type.nodl.yaml', 'scan', 'sensor_msgs/msg/PointCloud', 'RELIABLE'),
        ('reliability.nodl.yaml', 'scan', 'sensor_msgs/msg/LaserScan', 'BEST_EFFORT'),
    ],
)
def test_candidate_contract_changes_one_interface_property(filename, name, type_name, reliability):
    publisher = _installed_contract(Path('candidates') / filename).publishers[0]

    assert publisher.name == name
    assert publisher.type == type_name
    assert publisher.qos.reliability.value == reliability
