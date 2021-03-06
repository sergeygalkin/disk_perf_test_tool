# docker build -t ubuntu1604py36
FROM ubuntu:20.04

LABEL maintainer="Kostiantyn Danylov <kdanilov@mirantis.com>" version="2.0"

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt upgrade -yq && \
    DEBIAN_FRONTEND=noninteractive apt install -yq vim git tmux build-essential \
        python3 python3-dev python3-pip python3-venv python3-tk wget

COPY . /opt/wally

# git clone https://github.com/Mirantis/disk_perf_test_tool.git /opt/disk_perf_tool

RUN git clone https://github.com/koder-ua/cephlib.git /opt/cephlib && \
    git clone https://github.com/koder-ua/xmlbuilder3.git /opt/xmlbuilder3 && \
    git clone https://github.com/koder-ua/agent.git /opt/agent && \
    git clone https://github.com/koder-ua/koder_utils  /opt/koder_utils && \
    python3 -m pip install pip --upgrade && \
    cd /opt/wally && \
    python3 -m pip install wheel && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install -U cryptography && \
    ln -s /opt/wally/scripts/wally /usr/bin && \
    chmod a+x /opt/wally/scripts/wally

RUN apt purge -y python3-dev build-essential && apt -y autoremove

ENV PYTHONPATH /opt/cephlib:/opt/xmlbuilder3:/opt/agent:/opt/wally:/opt/koder_utils

CMD ["/bin/bash"]
