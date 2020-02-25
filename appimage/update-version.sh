#! /bin/bash

set -e


# Parse the CLI
show_usage () {
    echo "Usage: $(basename $0) <old version tag> <new version tag>"
    echo
    echo "Update a Python version tag."
    echo ""
}


while [ ! -z "$1" ]; do
    case "$1" in
        -h)
            show_usage
            exit 0
            ;;
        -*)
            echo "Invalid option: $1."
            echo
            show_usage
            exit 1
            ;;
        *)
            break
    esac
done

if [ "$#" -ne 2 ]; then
    echo "Invalid number of arguments. Got $#, expected 2."
    echo
    show_usage
    exit 1
fi


# Process the version tag
match_and_replace() {
    local prefix="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
    if [ ! -f "${prefix}/appimage/recipes/python$1.sh" ]; then
        echo "Error: invalid version tag: $1. Aborting."
        exit 1
    fi

    local files=".travis/script.sh README.md appimage/recipes/python$1.sh tests/test_plugin.py"

    local file
    for file in ${files}; do
        echo "updating tag in ${file}"
        sed -i -- "s/$1/$2/g" "${prefix}/${file}"
    done

    git mv "${prefix}/appimage/recipes/python$1.sh" \
           "${prefix}/appimage/recipes/python$2.sh"
}

match_and_replace "$@"
