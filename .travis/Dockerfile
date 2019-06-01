FROM ubuntu:trusty
LABEL maintainer="https://github.com/niess"

ARG Arch=x86_64
ARG OpenSLL=1.1.1c
ENV ARCH=${Arch} OPENSSL=${OpenSLL}

RUN apt update -y -qq                                                       && \
    apt install --no-install-recommends -y -qq                                 \
        build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev \
        libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev     \
        libexpat1-dev liblzma-dev libffi-dev libfuse2 wget                  && \
    rm -rf /var/lib/apt/lists/*

COPY . /work/.travis
WORKDIR /work

RUN ./.travis/install.sh
CMD ./.travis/script.sh
