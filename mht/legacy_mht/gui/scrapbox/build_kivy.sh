#!/bin/bash
set -e

# Prevent Homebrew from auto-cleanup hints/errors
export HOMEBREW_NO_INSTALL_CLEANUP=1

# 0. Pin Cython to a compatible version
~/dev/kivy_venv/bin/pip install --upgrade "Cython>=0.29.1,<3.0.11"

# 1. Ensure all Pango deps are installed as arm64 from source
brew install --build-from-source \
  pkg-config pango glib fontconfig harfbuzz fribidi

# 2. Exports for Pango build & silence nullability warnings
export USE_PANGOFT2=1
export PKG_CONFIG_PATH="$(brew --prefix)/lib/pkgconfig:$PKG_CONFIG_PATH"
export CFLAGS="-Wno-error=nullability-completeness"
export CXXFLAGS="$CFLAGS"
export PIP_NO_BUILD_ISOLATION=1

# 3. Clean previous Kivy builds
cd ~/dev/kivy
rm -rf build/ dist/ *.egg-info

# 4. Build & install Kivy in editable mode
~/dev/kivy_venv/bin/python -m pip install -e . \
  --no-deps \
  --no-build-isolation \
  -vvv > /Users/pabloherrero/Documents/ManHatTan/mht/gui/scrapbox/logging.txt 2>&1