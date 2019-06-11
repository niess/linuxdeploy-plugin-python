#! /bin/bash

set -ex

# Download, compile, and install if it's not already present in cache
if [ -n "${OPENSSL}" ]; then
    source .travis/openssl-config.sh

    wget --no-check-certificate -q "https://www.openssl.org/source/openssl-${OPENSSL}.tar.gz"
    tar zxf "openssl-${OPENSSL}.tar.gz"
    pushd "openssl-${OPENSSL}"
    ./config $OPENSSL_CONFIG_FLAGS -fPIC --prefix="$OPENSSL_DIR"
    make depend
    make -j"$(nproc)"
    if [[ "${OPENSSL}" =~ 1.0.1 ]]; then
        # OpenSSL 1.0.1 doesn't support installing without the docs.
        make install
    else
        # Avoid installing the docs
        make install_sw install_ssldirs
    fi
    popd
fi
