#!/bin/bash

if [ -z "$DEBUG" ] || [ "$DEBUG" -eq "0" ]; then
    set -e
else
    set -ex
fi


# Configuration variables
NPROC="${NPROC:-$(nproc)}"
PIP_OPTIONS="${PIP_OPTIONS:---upgrade}"
PIP_REQUIREMENTS="${PIP_REQUIREMENTS:-}"
PYTHON_BUILD_DIR="${PYTHON_BUILD_DIR:-}"
PYTHON_CONFIG="${PYTHON_CONFIG:-}"
version="3.7.3"
PYTHON_SOURCE="${PYTHON_SOURCE:-https://www.python.org/ftp/python/${version}/Python-${version}.tgz}"

script=$(readlink -f $0)
exe_name="$(basename ${APPIMAGE:-$script})"
BASEDIR="${APPDIR:-$(readlink -m $(dirname $script))}"


# Parse the CLI
show_usage () {
    echo "Usage: ${exe_name} --appdir <path to AppDir>"
    echo
    echo "Bundle Python into an AppDir"
    echo
    echo "Variables:"
    echo "  NPROC=\"${NPROC}\""
    echo "      The number of processors to use for building Python from a"
    echo "      source distribution"
    echo ""
    echo "  PIP_OPTIONS=\"${PIP_OPTIONS}\""
    echo "      Options for pip when bundling extra site-packages"
    echo ""
    echo "  PIP_REQUIREMENTS=\"${PIP_REQUIREMENTS}\""
    echo "      Specify extra site-packages to embed in the AppImage. Those are"
    echo "      installed with pip as requirements"
    echo ""
    echo "  PYTHON_BUILD_DIR=\"\""
    echo "      Set the build directory for Python. A temporary one will be"
    echo "      created otherwise"
    echo ""
    echo "  PYTHON_CONFIG=\"${PYTHON_CONFIG}\""
    echo "      Provide extra configuration flags for the Python build. Note"
    echo "      that the install prefix will be overwritten"
    echo ""
    echo "  PYTHON_SOURCE=\"${PYTHON_SOURCE}\""
    echo "      The source to use for Python. Can be a directory, an url or/and"
    echo "      an archive"
    echo ""
}

APPDIR=

while [ ! -z "$1" ]; do
    case "$1" in
        --plugin-api-version)
            echo "0"
            exit 0
            ;;
        --appdir)
            APPDIR="$2"
            shift
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Invalid argument: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
done

if [ -z "$APPDIR" ]; then
    show_usage
    exit 1
else
    APPDIR=$(readlink -m "$APPDIR")
    mkdir -p "$APPDIR"
fi


# Setup a temporary work space
if [ -z "${PYTHON_BUILD_DIR}" ]; then
    PYTHON_BUILD_DIR=$(mktemp -d)

    atexit() {
        rm -rf "${PYTHON_BUILD_DIR}"
    }

    trap atexit EXIT
else
    PYTHON_BUILD_DIR=$(readlink -m "${PYTHON_BUILD_DIR}")
    mkdir -p "${PYTHON_BUILD_DIR}"
fi

cd "${PYTHON_BUILD_DIR}"



# Install Python from sources
source_dir=$(basename "${PYTHON_SOURCE}")
if [[ "${PYTHON_SOURCE}" == http* ]] || [[ "${PYTHON_SOURCE}" == ftp* ]]; then
    wget -c --no-check-certificate "${PYTHON_SOURCE}"
else
    cp -r "${source_dir}" "."
fi
if [[ "${source_dir}" == *.tgz ]] || [[ "${source_dir}" == *.tar.gz ]]; then
    filename="${source_dir%.*}"
    [[ -f $filename ]] || tar -xzf "${source_dir}"
    source_dir="$filename"
fi

cd "${source_dir}"
./configure ${PYTHON_CONFIG} "--with-ensurepip=install" "--prefix=/usr"
HOME="${PYTHON_BUILD_DIR}" make -j"$NPROC" DESTDIR="$APPDIR" install


# Copy any TCl/Tk shared data
if [ -d "/usr/share/tcltk" ]; then
    cp -r "/usr/share/tcltk" "${APPDIR}/usr/share/tcltk"
fi


# Install any extra requirements with pip
if [ ! -z "${PIP_REQUIREMENTS}" ]; then
    cd "${APPDIR}/usr"
    pythons=( "python"?"."? )
    HOME="${PYTHON_BUILD_DIR}" PYTHONHOME=$PWD ./bin/${pythons[0]} -m pip install ${PIP_OPTIONS} ${PIP_REQUIREMENTS}
fi


# Prune the install
cd "$APPDIR/usr"
rm -rf "bin/python"*"-config" "bin/idle"* "include" "lib/pkgconfig" \
       "share/doc" "share/man" "lib/libpython"*".a" "lib/python"*"/test" \
       "lib/python"*"/config-"*"-x86_64-linux-gnu"




# Wrap the Python executables
cd "$APPDIR/usr/bin"
set +e
pythons=$(ls "python" "python"? "python"?"."? "python"?"."?"m" 2>/dev/null)
set -e
for python in $pythons
do
    if [ ! -L "$python" ]; then
        mv "$python" ".$python"
        cp "${BASEDIR}/share/python-wrapper.sh" "$python"
        sed -i "s|[{][{]PYTHON[}][}]|$python|g" "$python"
    fi
done

# Set a hook in Python for cleaning the path detection
cp "$BASEDIR/share/sitecustomize.py" "$APPDIR"/usr/lib/python*/site-packages
