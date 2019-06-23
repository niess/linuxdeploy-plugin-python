FROM ubuntu:trusty
LABEL maintainer="https://github.com/niess"

ARG Arch=x86_64
ENV ARCH="${Arch}"                                                             \
    OPENSSL="1.1.1c"                                                           \
    OPENSSL_DIR="${HOME}/openssl/${OPENSSL}${CONFIG_HASH}"

RUN apt update -y -qq                                                       && \
    apt install --no-install-recommends -y -qq                                 \
        build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev \
        libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev     \
        libexpat1-dev liblzma-dev libffi-dev tk-dev automake libfuse2 wget  && \
    rm -rf /var/lib/apt/lists/*

COPY . /work/.travis
WORKDIR /work
SHELL ["/bin/bash", "-c"]

RUN ./.travis/install.sh

ENV PATH="${OPENSSL_DIR}/bin:${PATH}"                                          \
    CFLAGS="${CFLAGS} -I${OPENSSL_DIR}/include"                                \
    LDFLAGS="-L${OPENSSL_DIR}/lib -Wl,-rpath=${OPENSSL_DIR}/lib"               \
    LD_LIBRARY_PATH="${OPENSSL_DIR}/lib:${LD_LIBRARY_PATH}"

CMD ["./.travis/script.sh"]
