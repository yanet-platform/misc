FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    less \
    openssh-server \
    openssh-client \
    bash-completion \
    pciutils \
    htop \
    curl \
    ca-certificates \
    iproute2 \
    iputils-arping \
    iputils-tracepath \
    iputils-ping \
    netbase \
    tcpdump \
    nano \
    gdb \
    mc \
    iptables

# this need for install linux-modules-extra
RUN apt-get update && apt-get install -y \
    linux-generic

RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

COPY fstab /root
COPY rc.local /root
