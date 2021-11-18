FROM alpine/git as intermediate
ARG SSH_PRIVATE_KEY
RUN mkdir /root/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN chmod 755 /root/.ssh
RUN chmod 400 /root/.ssh/id_rsa
RUN git clone git@github.com:strathclyde-artificial-intelligence/CAELUS_DigitalTwin.git /CAELUS_DigitalTwin

FROM python:3.7
RUN apk update && apk add bash
COPY --from=intermediate /CAELUS_DigitalTwin /CAELUS_DigitalTwin
RUN apt-get update && apt-get -y install cmake protobuf-compiler
RUN apt-get install libboost-all-dev -y
RUN apt install libeigen3-dev
WORKDIR /CAELUS_DigitalTwin
RUN bash install_all.sh

CMD source venv/bin/activate
ENTRYPOINT ["python3", "start.py"]