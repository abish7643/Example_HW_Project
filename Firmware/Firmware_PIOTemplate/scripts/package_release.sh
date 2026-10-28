#!/bin/bash

set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT=Firmware_PIOTemplate
OUT_DIR=release
ESPTOOL_FLAGS="--chip esp32 --port /dev/ttyUSB0 --baud 921600 write_flash 0x0"

fail() {
    echo "Package Failed: $1" >&2
    exit 1
}

[ $# -gt 0 ] || fail "Usage: $0 <env> [<env> ...]"

VERSION=$(sed -nE 's/^#define FIRMWARE_VERSION +"(V[0-9]+\.[0-9]+\.[0-9]+[A-Z]?)".*/\1/p' include/firmware.h)
[ -n "$VERSION" ] || fail "FIRMWARE_VERSION not found in include/firmware.h"
HASH=$(sed -nE 's/^#define GIT_COMMIT_HASH "([0-9A-Z]+)".*/\1/p' include/build_attributes.h 2>/dev/null || true)
[ -n "$HASH" ] || fail "GIT_COMMIT_HASH not found in include/build_attributes.h, build first"

TAG="${PROJECT}_${VERSION}"
PRERELEASE=false
if [[ "$VERSION" =~ [A-Z]$ ]]; then
    PRERELEASE=true
fi

write_readme() {
    cat <<EOF
# ${PROJECT} ${BUILD}

${BOARD}

## OTA (Keeps Settings)

Install \`OTA/${NAME}.bin\` through the device's OTA update.

## UART (Resets Settings)

\`\`\`
pip install esptool
esptool.py ${ESPTOOL_FLAGS} Image/${NAME}_Full.bin
\`\`\`
EOF
}

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

BOARDS=""
for ENV in "$@"; do
    APP=$(ls -t .pio/build/"$ENV"/"${PROJECT}_${ENV}_${VERSION}+${HASH}"_*.bin 2>/dev/null | { grep -v '_Full\.bin$' || true; } | sed -n 1p)
    [ -n "$APP" ] || fail "No $ENV image for ${VERSION}+${HASH}, build $ENV first"
    NAME=$(basename "$APP" .bin)
    FULL=".pio/build/$ENV/${NAME}_Full.bin"
    [ -f "$FULL" ] || fail "$FULL missing, build $ENV first"
    BUILD="${NAME#"${PROJECT}_${ENV}_"}"

    MODEL=$(sed -nE "/^\[env:${ENV}\]/,/^\[env:/"'s/^[[:space:]]*-DBOARD_MODEL=\\"([^\\"]+)\\".*/\1/p' platformio.ini)
    BOARD="${ENV}${MODEL:+ (${MODEL})}"

    STAGE="$OUT_DIR/$ENV"
    mkdir -p "$STAGE/OTA" "$STAGE/Image"
    cp "$APP" "$STAGE/OTA/"
    cp "$FULL" "$STAGE/Image/"
    write_readme > "$STAGE/README.md"
    (cd "$STAGE" && zip -q -X -r "../$NAME.zip" README.md OTA Image)
    rm -rf "$STAGE"

    BOARDS+="${BOARDS:+, }${BOARD}"
done

CHANNEL=Stable
if [ "$PRERELEASE" = true ]; then
    CHANNEL=Pre-release
fi

cat > "$OUT_DIR/release_notes.md" <<EOF
## 🎯 Release Information
- **Version**: ${VERSION} (${CHANNEL})
- **Build**: ${VERSION}+${HASH}
- **Supported HW Revs**: ${BOARDS}

## Flashing
- **OTA**: install the \`.bin\` from \`OTA/\` through the device's OTA update (keeps the settings)
- **UART**: flash the \`_Full.bin\` from \`Image/\` at \`0x0\` (resets the settings)

Each zip's \`README.md\` has the steps for that board.
EOF

if [ -n "${GITHUB_OUTPUT:-}" ]; then
    {
        echo "VERSION=$VERSION"
        echo "HASH=$HASH"
        echo "TAG=$TAG"
        echo "PRERELEASE=$PRERELEASE"
    } >> "$GITHUB_OUTPUT"
fi

echo "Packaged $TAG (prerelease: $PRERELEASE) into $OUT_DIR/:"
ls -1 "$OUT_DIR"
