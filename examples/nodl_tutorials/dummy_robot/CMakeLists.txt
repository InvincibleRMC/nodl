# SPDX-FileCopyrightText: 2026 Open Source Robotics Foundation, Inc.
# SPDX-License-Identifier: Apache-2.0
cmake_minimum_required(VERSION 3.22)
project(nodl_tutorial_dummy_robot)

find_package(ament_cmake REQUIRED)
find_package(ament_nodl REQUIRED)

ament_nodl_register(dummy_laser FILE nodl/dummy_laser.nodl.yaml)
install(DIRECTORY nodl/candidates DESTINATION share/${PROJECT_NAME}/nodl)
install(DIRECTORY rviz DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(tutorial_registration_tests test/test_registration.py)
  ament_add_pytest_test(tutorial_runtime_tests test/test_runtime.py TIMEOUT 90)
endif()

ament_package()
