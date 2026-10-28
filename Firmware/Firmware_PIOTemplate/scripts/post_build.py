import os
import time
import subprocess
import shutil

Import("env")


def get_firmware_version():
    """Extract firmware version from firmware.h"""
    firmware_h_path = os.path.join(
        env.get("PROJECT_DIR"), "include", "firmware.h")
    firmware_attributes_path = os.path.join(
        env.get("PROJECT_DIR"), "include", "build_attributes.h")
    version = "UNKNOWN"
    commit_hash = "UNKNOWN"
    build_timestamp = "UNKNOWN"

    with open(firmware_h_path, 'r') as f:
        for line in f:
            if '#define FIRMWARE_VERSION' in line and '"V' in line:
                # Extract version like V1.0.2B
                version = line.split('"')[1]

    with open(firmware_attributes_path, 'r') as f:
        for line in f:
            if '#define GIT_COMMIT_HASH' in line:
                commit_hash = line.split('"')[1]
            elif '#define BUILD_TIMESTAMP' in line:
                build_timestamp = line.split('"')[1]

    return version, commit_hash, build_timestamp


def merge_firmware(app_bin, merged_bin, env):
    images = []
    for offset, image in env.get("FLASH_EXTRA_IMAGES", []):
        images += [offset, f'"{env.subst(image)}"']
    images += ["$ESP32_APP_OFFSET", f'"{app_bin}"']

    board = env.BoardConfig()
    command = " ".join([
        '"$PYTHONEXE"', '"$OBJCOPY"', "--chip", board.get("build.mcu", "esp32"),
        "merge_bin", "-o", f'"{merged_bin}"',
        "--flash_mode", "${__get_board_flash_mode(__env__)}",
        "--flash_freq", "${__get_board_f_flash(__env__)}",
        "--flash_size", board.get("upload.flash_size", "keep"),
    ] + images)
    return env.Execute(command)


def rename_firmware(source, target, env):
    """Rename firmware file after build"""
    print("Post-build: Renaming firmware file...")

    # Get version info
    version, commit_hash, build_timestamp = get_firmware_version()

    # Get the current PlatformIO environment name
    env_name = env.get("PIOENV", "unknown")
    print(f"Building for environment: {env_name}")

    # Create new filename with environment name
    new_filename = f"Firmware_PIOTemplate_{env_name}_{version}+{commit_hash}_{build_timestamp}.bin"

    # The source parameter is the actual firmware path
    firmware_src = str(source[0]).replace(".elf", ".bin")
    print(f"Source firmware: {firmware_src}")

    # Get the directory and create new path
    firmware_dir = os.path.dirname(firmware_src)
    firmware_dst = os.path.join(firmware_dir, new_filename)

    # Copy with new name
    if not os.path.exists(firmware_src):
        print(f"Error: Firmware file not found at {firmware_src}")
        return 1

    shutil.copy2(firmware_src, firmware_dst)
    print(f"Firmware renamed to: {new_filename}")
    print(f"Full path: {firmware_dst}")

    full_dst = os.path.splitext(firmware_dst)[0] + "_Full.bin"
    if merge_firmware(firmware_src, full_dst, env):
        print("Error: Failed to write the full flash image")
        return 1
    print(f"Full flash image: {os.path.basename(full_dst)}")
    print(f"Flash over UART: esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0 {os.path.basename(full_dst)}")
    return 0


# Register post-build action
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", rename_firmware)
