#!/bin/bash

if [ -z "$DEBUG" ] || [ "$DEBUG" -eq "0" ]; then
    set -e
else
    set -ex
fi


REPO_ROOT=$(readlink -f $(dirname "$0")"/..")


if [ -z "$1" ]; then
    echo "no recipe specified. Aborting..."
    exit 1
fi
if [ -f "$1" ]; then
    source "$1"
    filename=$(basename "$1")
    name="${filename%.*}"
else
    source "${REPO_ROOT}/appimage/recipes/${1}.sh"
    name="$1"
fi

export PYTHON_SOURCE="${PYTHON_SOURCE:-https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz}"
export PIP_REQUIREMENTS


ARCH="${ARCH:-$(arch)}"
export ARCH="${ARCH}"


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
linuxdeploy="linuxdeploy-${ARCH}.AppImage"
plugin="linuxdeploy-plugin-python-${ARCH}.AppImage"

if [ ! -f "${linuxdeploy}" ]; then
    url="https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous"
    wget --no-check-certificate -q "${url}/${linuxdeploy}"
    chmod u+x "${linuxdeploy}"
fi

if [ ! -f "${REPO_ROOT}/appimage/${plugin}" ]; then
    ${REPO_ROOT}/appimage/build-plugin.sh
fi
cp "${REPO_ROOT}/appimage/${plugin}" "."

exe="python${PYTHON_VERSION::3}"

cp "${REPO_ROOT}/appimage/resources/python.desktop" "${name}.desktop"
sed -i "s|[{][{]exe[}][}]|${exe}|g" "${name}.desktop"
sed -i "s|[{][{]name[}][}]|${name}|g" "${name}.desktop"

cp "${REPO_ROOT}/appimage/resources/apprun.sh" "AppRun"
sed -i "s|[{][{]exe[}][}]|${exe}|g" "AppRun"
sed -i "s|[{][{]entrypoint[}][}]|${APPRUN_ENTRYPOINT}|g" "AppRun"

./"${linuxdeploy}" --appdir AppDir \
                   --plugin python \
                   -i "${REPO_ROOT}/appimage/resources/python.png" \
                   -d "${name}.desktop" \
                   --custom-apprun "AppRun" \
                   --output "appimage"

popd
mv -f "${BUILD_DIR}/${name}-${ARCH}.AppImage" "${REPO_ROOT}/appimage"
