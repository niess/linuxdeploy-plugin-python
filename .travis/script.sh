#! /bin/bash

set -ex


wrapped_run() {
    local script="./appimage/build-$1.sh"
    local arg="$2"
    local log
    if [ -z "$2" ]; then
        log="plugin.log"
    else
        log="${2}.log"
    fi

    ("${script}" "${arg}" >& "${log}" ; tail -300 "${log}")
}

wrapped_run plugin
wrapped_run python python2.7.17
wrapped_run python python3.7.5
wrapped_run python python3.8.0
wrapped_run python scipy
wrapped_run python xonsh
