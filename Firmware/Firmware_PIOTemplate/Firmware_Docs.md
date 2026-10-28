# Firmware Docs

## Releases

A push to `Firmware_Releases` that changes this project (not `*.md`) runs `.github/workflows/firmware-release.yml`. It builds the envs in `RELEASE_ENVS` and publishes `Firmware_PIOTemplate_<version>`, as a prerelease when the version ends in a letter (`V0.0.1B`). A version that already has a release fails the run, so bump `FIRMWARE_VERSION` in `include/firmware.h` first.

Each board gets a zip:

- `OTA/<name>.bin`: the app, for an OTA update (keeps the settings)
- `Image/<name>_Full.bin`: bootloader, partition table and app, flashed at `0x0` over UART (resets the settings)
- `README.md`: the steps, with the exact esptool command

`scripts/post_build.py` writes both images on every build. `scripts/package_release.sh <envs>` makes the zips and release notes in `release/`, locally the same way as in CI.
