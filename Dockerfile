FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        libcharls-dev \
        libfmt-dev \
        libeigen3-dev \
        pybind11-dev \
        python-is-python3 \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        wget

RUN pip install build

WORKDIR /tmp

ARG CMAKE_VERSION=3.28.1
ARG CMAKE_ARCH=x86_64

RUN wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-linux-${CMAKE_ARCH}.sh && \
    bash cmake-${CMAKE_VERSION}-linux-${CMAKE_ARCH}.sh --skip-license --prefix=/usr/local


