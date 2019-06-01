#! /bin/bash

set -ex


if [ -n "${OPENSSL}" ]; then
    source .travis/openssl-config.sh
    export PATH="${HOME}/${OPENSSL_DIR}/bin:${PATH}"
    export CFLAGS="${CFLAGS} -I${HOME}/${OPENSSL_DIR}/include"
    # rpath on linux will cause it to use an absolute path so we don't need to
    # do LD_LIBRARY_PATH
    export LDFLAGS="-L${HOME}/${OPENSSL_DIR}/lib -Wl,-rpath=${HOME}/${OPENSSL_DIR}/lib"
fi


DEBUG=true ./appimage/build-appimage.sh
python3 -m tests
