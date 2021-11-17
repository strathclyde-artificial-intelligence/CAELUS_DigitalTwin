FROM alpine
RUN git clone https://github.com/strathclyde-artificial-intelligence/CAELUS_DigitalTwin
RUN cd CAELUS_DigitalTwin
RUN bash install_all