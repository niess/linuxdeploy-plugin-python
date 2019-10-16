#! /bin/bash

set -ex

./appimage/build-plugin.sh
./appimage/build-python.sh python2
./appimage/build-python.sh python3
./appimage/build-python.sh scipy
./appimage/build-python.sh xonsh

python3 -m tests
