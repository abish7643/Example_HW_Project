import subprocess

Import("env")


result = subprocess.call(["bash", "scripts/build_attributes.sh"])
if result != 0:
    print("Error: Failed to generate build_info.h")
    env.Exit(1)
