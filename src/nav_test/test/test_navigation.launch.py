import unittest
import sys
import os

import ament_index_python
from ament_index_python.packages import get_package_share_directory

import pytest
import launch_testing
from launch_testing.actions import ReadyToTest  
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


@pytest.mark.launch_test
def generate_test_description():
    rosbag_cmd = ["ros2", "bag", "record"]
    bag_recorder = ExecuteProcess(
        cmd=rosbag_cmd, output="screen", additional_env={"PYTHONUNBUFFERED": "1"}
    )


    # snapshot sky
    snapshot_sky = Node(
        package='nav_test', 
        executable='snapshot_sky', 
    )

    video_recorder = Node(
        package='image_view',
        executable='video_recorder',
        parameters=[{
            "filename": '/tmp/artefacts_output/topdown.mp4',
            "codec": "h264"
        }],
        remappings=[
            ("image", "/sky_cam")
        ]
    )

    reach_goal = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(get_package_share_directory("nav_test"), "launch"),
                "/reach_goal.launch.py",
            ]
        ),
        launch_arguments={
            # "seed": "7",
        }.items(),
    )

    return LaunchDescription(
        [
            reach_goal,
            bag_recorder,
            ReadyToTest(),
            snapshot_sky,
            video_recorder,
        ]
    )


class TestTurtle(unittest.TestCase):
    def test_tank_reach_target(self, proc_output):
        # This will match stdout from test_process.
        proc_output.assertWaitFor("Goal reached!", timeout=50)
