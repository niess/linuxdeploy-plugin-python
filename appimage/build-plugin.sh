#!/bin/bash

if [ -z "$DEBUG" ] || [ "$DEBUG" -eq "0" ]; then
    set -e
else
    set -ex
fi


EXEC_NAME="${EXEC_NAME:-linuxdeploy-plugin-python}"
ARCH="${ARCH:-$(arch)}"

REPO_ROOT=$(readlink -f $(dirname "$0")"/..")


# Setup a temporary work space
if [ -z "${BUILD_DIR}" ]; then
    BUILD_DIR=$(mktemp -d)

    _cleanup() {
        rm -rf "${BUILD_DIR}"
    }

    trap _cleanup EXIT
else
    BUILD_DIR=$(readlink -m "${BUILD_DIR}")
    mkdir -p "${BUILD_DIR}"
fi

pushd $BUILD_DIR


# Build the AppImage
appimagetool="appimagetool-${ARCH}.AppImage"

if [ ! -f "${appimagetool}" ]; then
    url="https://github.com/AppImage/AppImageKit/releases/download/continuous"
    wget --no-check-certificate -q "${url}/${appimagetool}"
    chmod u+x "${appimagetool}"
fi

mkdir -p "AppDir/share"
cp "${REPO_ROOT}/${EXEC_NAME}.sh" "AppDir/AppRun"
chmod +x "AppDir/AppRun"
cp -r "${REPO_ROOT}/share" "AppDir"

pushd "AppDir"
cp "${REPO_ROOT}/${EXEC_NAME}.sh" "."
cp "${REPO_ROOT}/appimage/resources/python.png" "${EXEC_NAME}.png"
cp "${REPO_ROOT}/appimage/resources/plugin.desktop" "${EXEC_NAME}.desktop"
ln -s "${EXEC_NAME}.png" ".DirIcon"
popd

ARCH="${ARCH}" ./"${appimagetool}" AppDir
popd
mv "${BUILD_DIR}/${EXEC_NAME}-${ARCH}.AppImage" "${REPO_ROOT}/appimage"
