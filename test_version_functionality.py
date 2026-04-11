#!/usr/bin/env python3
"""
Test script for version query and work speed functionality
"""

import sys
import os
sys.path.append('.')

from stepper_motor_controller import StepperMotorController
from config import *

def test_version_query():
    """Test version query functionality"""
    print("Testing version query functionality...")

    controller = StepperMotorController()

    # Test CRC calculation for version query command
    # Command: 01 03 00 02 00 02 (station 1, read 2 registers from 0x0002)
    test_command = "010300020002"
    from stepper_motor_controller import calc_crc
    crc = calc_crc(test_command)
    full_command = test_command + crc

    print(f"Version query command: {full_command}")
    print(f"Expected from manual:  01030002000265CB")
    print(f"CRC calculated: {crc}")
    print(f"CRC expected:   65CB")
    print(f"CRC matches: {crc == '65CB'}")

    # Test work speed register strategy logic
    print("\nTesting work speed register strategy...")

    # Mock version scenarios
    test_cases = [
        (115, "32bit", "0x00D8"),
        (113, "32bit", "0x00D8"),
        (112, "16bit", "0x009A"),
        (100, "16bit", "0x009A"),
    ]

    for version, expected_strategy, expected_register in test_cases:
        # Temporarily override the version reading
        original_read_version = controller.read_version_number

        def mock_version():
            return version

        controller.read_version_number = mock_version
        strategy, ver = controller.get_work_speed_register_strategy()

        print(f"Version {version}: Strategy={strategy}, Expected={expected_strategy}, Match={strategy == expected_strategy}")

        # Restore original method
        controller.read_version_number = original_read_version

if __name__ == "__main__":
    test_version_query()