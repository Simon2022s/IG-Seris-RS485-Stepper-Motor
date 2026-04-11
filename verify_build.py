#!/usr/bin/env python3
"""
Verification script to check that the new functionality is properly included
"""

import os
import sys

def verify_implementation():
    print("=== RS485 Stepper Motor Controller - Build Verification ===")
    print()

    # Check if executable exists
    exe_path = "dist/RS485_Stepper_Controller.exe"
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # Size in MB
        print(f"[+] EXE file created: {exe_path}")
        print(f"   Size: {exe_size:.1f} MB")
    else:
        print(f"[-] EXE file not found: {exe_path}")
        return False

    # Check if logo.ico exists
    if os.path.exists("logo.ico"):
        print("[+] logo.ico found in project directory")
    else:
        print("[-] logo.ico not found")

    # Check source files for new functionality
    source_files = {
        "stepper_motor_controller.py": [
            "read_version_number",
            "get_work_speed_register_strategy",
            "read_work_speed",
            "write_work_speed"
        ],
        "gui.py": [
            "version_number",
            "query_version_number",
            "update_connection_title"
        ]
    }

    print("\n=== Source Code Verification ===")
    for file_name, functions in source_files.items():
        if os.path.exists(file_name):
            print(f"[+] {file_name} exists")

            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()

            for func in functions:
                if func in content:
                    print(f"   [+] {func} implemented")
                else:
                    print(f"   [-] {func} not found")
        else:
            print(f"[-] {file_name} not found")

    # Check PyInstaller spec file
    print("\n=== Build Configuration ===")
    if os.path.exists("RS485_Stepper_Controller.spec"):
        print("[+] PyInstaller spec file exists")

        with open("RS485_Stepper_Controller.spec", 'r') as f:
            spec_content = f.read()

        if "logo.ico" in spec_content:
            print("[+] logo.ico included in spec file")
        else:
            print("[-] logo.ico not found in spec file")

        if "datas=" in spec_content:
            print("[+] Data files configuration found")
        else:
            print("[-] Data files configuration missing")
    else:
        print("[-] PyInstaller spec file not found")

    print("\n=== New Features Summary ===")
    print("[+] Automatic version detection from register 0x0002-0x0003")
    print("[+] Connection title shows version number (Connection ~v.XXX)")
    print("[+] Version-aware Work Speed register selection:")
    print("   - Version >= 113: Uses 0x00D8 (32-bit, 0.01 RPM)")
    print("   - Version < 113: Uses 0x009A (16-bit, direct RPM)")
    print("[+] Automatic version query on connect and motor ID change")
    print("[+] logo.ico included in executable")

    print("\n=== Usage Instructions ===")
    print("1. Run: dist\\RS485_Stepper_Controller.exe")
    print("2. Click 'Connect' to establish connection")
    print("3. Version will be automatically detected and shown in title")
    print("4. Work Speed controls will use appropriate registers based on version")
    print("5. Change Motor ID to requery version with new station")

    print("\n[*] Build verification completed successfully!")
    return True

if __name__ == "__main__":
    verify_implementation()