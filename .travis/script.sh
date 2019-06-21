#! /bin/bash

set -ex


if [ -n "${OPENSSL}" ]; then
    source .travis/openssl-config.sh
    export PATH="${OPENSSL_DIR}/bin:${PATH}"
    export CFLAGS="${CFLAGS} -I${OPENSSL_DIR}/include"
    export LDFLAGS="-L${OPENSSL_DIR}/lib -Wl,-rpath=${OPENSSL_DIR}/lib"
    export LD_LIBRARY_PATH="${OPENSSL_DIR}/lib:${LD_LIBRARY_PATH}"
fi


./appimage/build-plugin.sh
./appimage/build-python.sh python2
./appimage/build-python.sh python3
./appimage/build-python.sh scipy

python3 -m tests
