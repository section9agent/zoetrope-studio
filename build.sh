#!/usr/bin/env bash
# ============================================================
#  Vinyl Zoetrope Designer — macOS / Linux build script
#  Run this once from inside the vinyl_zoetrope folder:
#    chmod +x build.sh && ./build.sh
#  Requires Python 3.10+ (brew install python on macOS).
# ============================================================

set -e
echo "=== Vinyl Zoetrope Designer — $(uname -s) build ==="
echo

# -- Virtual environment -------------------------------------
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# -- Dependencies --------------------------------------------
echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install PyQt6 Pillow pyinstaller --quiet

# -- Build ---------------------------------------------------
echo
echo "Building standalone app..."
pyinstaller zoetrope_studio.spec --clean --noconfirm

# -- Result --------------------------------------------------
echo
if [ "$(uname -s)" = "Darwin" ]; then
    TARGET="dist/VinylZoetrope.app"
    LAUNCH="open dist/VinylZoetrope.app"
else
    TARGET="dist/VinylZoetrope/VinylZoetrope"
    LAUNCH="./dist/VinylZoetrope/VinylZoetrope"
fi

if [ -e "$TARGET" ]; then
    echo "BUILD SUCCESSFUL"
    echo "Output: $TARGET"
    echo
    echo "To run:  $LAUNCH"
    if [ "$(uname -s)" = "Darwin" ]; then
        echo "To distribute: zip the dist/VinylZoetrope.app bundle."
    else
        echo "To distribute: zip the entire dist/VinylZoetrope/ folder."
    fi
else
    echo "BUILD FAILED — check output above for errors."
    exit 1
fi
