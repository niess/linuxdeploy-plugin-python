FROM quay.io/pypa/manylinux2010_x86_64
LABEL maintainer="https://github.com/niess"

ARG Arch=x86_64
ENV ARCH="${Arch}"                                                             \
    OPENSSL="1.1.1c"

RUN yum -y install bzip2-devel fuse-sshfs ncurses-devel readline-devel         \
                   sqlite-devel openssl-devel symlinks tk-devel xz-devel wget

COPY . /work/.travis
WORKDIR /work
SHELL ["/bin/bash", "-c"]

ENV OPENSSL_DIR="${HOME}/openssl/${OPENSSL}"
RUN ./.travis/install.sh

ENV PATH="${OPENSSL_DIR}/bin:${PATH}"                                          \
    CFLAGS="${CFLAGS} -I${OPENSSL_DIR}/include"                                \
    LDFLAGS="-L${OPENSSL_DIR}/lib"                                             \
    LD_LIBRARY_PATH="${OPENSSL_DIR}/lib:${LD_LIBRARY_PATH}"

CMD ["./.travis/script.sh"]
