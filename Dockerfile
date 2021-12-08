FROM python:3.7

RUN apt-get update -y
RUN apt-get update && \
apt-get install -y --no-install-recommends \
        openjdk-11-jre

ENV ANT_VERSION=1.10.3
ENV ANT_HOME=/opt/ant
ENV IN_DOCKER=1

# change to tmp folder
WORKDIR /tmp

RUN apt-get update && apt-get install -y bash
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
COPY . /CAELUS_DigitalTwin
RUN apt-get update && apt-get -y install cmake protobuf-compiler
RUN apt-get install libboost-all-dev -y
RUN apt install libeigen3-dev
RUN apt-get install -y bc
WORKDIR /CAELUS_DigitalTwin
ENV PX4_ROOT_FOLDER="/CAELUS_DigitalTwin/Dependencies/PX4-Autopilot"
RUN bash install_all.sh

ENTRYPOINT ["python", "-u", "start.py"]