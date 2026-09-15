# SPDX-FileCopyrightText: 2026 Open Source Robotics Foundation, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Exercise runtime conformance through the commands shown in the tutorial."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from ament_index_python.packages import get_package_prefix, get_package_share_directory

PACKAGE = 'nodl_tutorial_dummy_robot'
NODE_NAME = '/dummy_laser'


def _test_environment():
    environment = os.environ.copy()
    environment['ROS_DOMAIN_ID'] = str(os.getpid() % 100 + 100)
    environment['ROS_AUTOMATIC_DISCOVERY_RANGE'] = 'LOCALHOST'
    environment['RMW_IMPLEMENTATION'] = 'rmw_cyclonedds_cpp'
    return environment


def _node_executable():
    prefix = Path(get_package_prefix('dummy_sensors'))
    return prefix / 'lib' / 'dummy_sensors' / 'dummy_laser'


def _contract(relative_path):
    share = Path(get_package_share_directory(PACKAGE))
    return share / 'nodl' / relative_path


def _run_conform(relative_path):
    ros2 = shutil.which('ros2')
    assert ros2 is not None

    node = subprocess.Popen(
        [_node_executable()],
        env=_test_environment(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        return subprocess.run(
            [ros2, 'nodl', 'conform', NODE_NAME, '--file', _contract(relative_path), '--timeout', '10'],
            env=_test_environment(),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    finally:
        node.terminate()
        try:
            node.wait(timeout=5)
        except subprocess.TimeoutExpired:
            node.kill()
            node.wait()


def test_upstream_node_conforms():
    result = _run_conform('dummy_laser.nodl.yaml')

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f'{NODE_NAME}: conforms'


@pytest.mark.parametrize(
    ('filename', 'diagnostics'),
    [
        (
            'topic.nodl.yaml',
            (
                "[extra] publishers '/scan'",
                "[missing] publishers '/scan_regressed'",
            ),
        ),
        (
            'type.nodl.yaml',
            (
                "[type_mismatch] publishers '/scan': expected 'sensor_msgs/msg/PointCloud', "
                "got 'sensor_msgs/msg/LaserScan'",
            ),
        ),
        ('reliability.nodl.yaml', ('reliability: expected BEST_EFFORT, got RELIABLE',)),
    ],
)
def test_candidate_contract_does_not_conform(filename, diagnostics):
    result = _run_conform(Path('candidates') / filename)

    assert result.returncode != 0
    for diagnostic in diagnostics:
        assert diagnostic in result.stderr
